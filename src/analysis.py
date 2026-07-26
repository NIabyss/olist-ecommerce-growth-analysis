"""订单事实表、用户分层、留存和检验的可复用实现。"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy import stats

def load_and_clean(raw_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """读入标准化 CSV，返回订单粒度事实表和数据质量表。"""
    o=pd.read_csv(raw_dir/'orders.csv', parse_dates=['order_purchase_timestamp','order_delivered_customer_date','order_estimated_delivery_date'])
    c=pd.read_csv(raw_dir/'customers.csv')
    i=pd.read_csv(raw_dir/'order_items.csv')
    p=pd.read_csv(raw_dir/'payments.csv')
    r=pd.read_csv(raw_dir/'reviews.csv')
    # Olist 的品类位于 products 表；模拟数据为简化可直接带在订单商品表中。
    if 'product_category_name' not in i.columns and (raw_dir/'products.csv').exists():
        products=pd.read_csv(raw_dir/'products.csv',usecols=['product_id','product_category_name'])
        i=i.merge(products,on='product_id',how='left',validate='many_to_one')
    if 'product_category_name' not in i.columns:
        i['product_category_name']='unknown'
    quality=[]
    for name, df, key in [('orders',o,'order_id'),('customers',c,'customer_id'),('items',i,'order_id'),('payments',p,'order_id')]:
        quality.append([name,len(df),int(df.duplicated().sum()),int(df[key].isna().sum())])
    def mode_or_unknown(x: pd.Series) -> str:
        x=x.dropna()
        return x.mode().iat[0] if not x.empty else 'unknown'
    item=i.groupby('order_id',as_index=False).agg(product_amount=('price','sum'),freight_amount=('freight_value','sum'),item_count=('order_item_id','count'),category=('product_category_name',mode_or_unknown))
    pay=p.sort_values('payment_value',ascending=False).drop_duplicates('order_id')[['order_id','payment_type','payment_installments']]
    review=r.groupby('order_id',as_index=False).agg(review_score=('review_score','mean'))
    f=o.merge(c,on='customer_id',how='left',validate='one_to_one').merge(item,on='order_id',how='left',validate='one_to_one').merge(pay,on='order_id',how='left',validate='one_to_one').merge(review,on='order_id',how='left',validate='one_to_one')
    f['gmv']=f['product_amount'].fillna(0)+f['freight_amount'].fillna(0)
    f['purchase_month']=f['order_purchase_timestamp'].dt.to_period('M').astype(str)
    f['delivery_days']=(f['order_delivered_customer_date']-f['order_purchase_timestamp']).dt.total_seconds()/86400
    f['late_delivery']=np.where(f['order_delivered_customer_date'].notna(),f['order_delivered_customer_date']>f['order_estimated_delivery_date'],np.nan)
    # 业务规则：只用已交付、金额正且下单时间有效的记录进入经营分析
    f['is_valid_analysis']=(f.order_status.eq('delivered') & f.gmv.gt(0) & f.order_purchase_timestamp.notna())
    quality.append(['fact_before_filter',len(f),int(f.duplicated('order_id').sum()),int(f.order_id.isna().sum())])
    # 把关键业务校验写入结果，真实数据接入时应先审阅这些行再解读指标。
    business_checks = pd.DataFrame([
        ['orders_without_customer', int(f.customer_unique_id.isna().sum())],
        ['delivered_without_item_amount', int((f.order_status.eq('delivered') & f.gmv.le(0)).sum())],
        ['delivered_before_purchase', int((f.order_delivered_customer_date < f.order_purchase_timestamp).sum())],
        ['estimated_before_purchase', int((f.order_estimated_delivery_date < f.order_purchase_timestamp).sum())],
        ['duplicate_order_fact', int(f.order_id.duplicated().sum())],
    ], columns=['check','failed_rows'])
    q = pd.DataFrame(quality,columns=['check_name','rows','duplicate_rows','null_primary_key'])
    q['check_type']='table'; q['failed_rows']=np.nan
    business_checks['check_type']='business'; business_checks['rows']=np.nan
    business_checks['duplicate_rows']=np.nan; business_checks['null_primary_key']=np.nan
    business_checks=business_checks.rename(columns={'check':'check_name'})
    return f, pd.concat([q,business_checks[q.columns]],ignore_index=True)

def monthly_kpis(f: pd.DataFrame) -> pd.DataFrame:
    d=f[f.is_valid_analysis].copy(); d['first_purchase']=d.groupby('customer_unique_id').order_purchase_timestamp.transform('min')
    d['is_new']=d.order_purchase_timestamp.dt.to_period('M').eq(d.first_purchase.dt.to_period('M'))
    out=d.groupby('purchase_month').agg(gmv=('gmv','sum'),orders=('order_id','nunique'),users=('customer_unique_id','nunique'),new_users=('customer_unique_id',lambda x: x[d.loc[x.index,'is_new']].nunique()),repeat_users=('customer_unique_id',lambda x: x[~d.loc[x.index,'is_new']].nunique())).reset_index()
    out['aov']=out.gmv/out.orders
    out['orders_per_user']=out.orders/out.users
    # 可审计恒等式：GMV = active users × orders/user × AOV。
    out['identity_gmv']=out.users*out.orders_per_user*out.aov
    out['identity_gap']=out.gmv-out.identity_gmv
    max_date=d['order_purchase_timestamp'].max().normalize()
    latest_month=max_date.to_period('M')
    # Olist 最后一个自然月可能未采全；趋势环比时默认排除该月。
    out['is_complete_month']=out['purchase_month'].map(lambda x: pd.Period(x,freq='M') < latest_month or max_date == latest_month.end_time.normalize())
    return out

def growth_decomposition(f: pd.DataFrame) -> pd.DataFrame:
    """按月输出 GMV 的三因子（活跃用户、频次、客单价）而非把相关变化误认为因果贡献。"""
    m=monthly_kpis(f).copy()
    for col in ['gmv','users','orders_per_user','aov']:
        m[f'{col}_mom_pct']=m[col].pct_change()
    return m

def rfm_table(f: pd.DataFrame) -> pd.DataFrame:
    d=f[f.is_valid_analysis].copy(); as_of=d.order_purchase_timestamp.max()+pd.Timedelta(days=1)
    x=d.groupby('customer_unique_id').agg(recency_days=('order_purchase_timestamp',lambda s:(as_of-s.max()).days),frequency=('order_id','nunique'),monetary=('gmv','sum')).reset_index()
    # rank(method=first) 避免 qcut 在大量单次购买时边界重复
    x['r_score']=pd.qcut(x.recency_days.rank(method='first',ascending=False),5,labels=[1,2,3,4,5]).astype(int)
    x['f_score']=pd.qcut(x.frequency.rank(method='first'),5,labels=[1,2,3,4,5]).astype(int)
    x['m_score']=pd.qcut(x.monetary.rank(method='first'),5,labels=[1,2,3,4,5]).astype(int)
    score=x.r_score+x.f_score+x.m_score
    x['segment']=np.select([score>=12,score>=9,score>=6],['高价值','潜力','需唤回'],default='沉睡')
    return x

def cohort_table(f: pd.DataFrame) -> pd.DataFrame:
    d=f[f.is_valid_analysis][['customer_unique_id','order_purchase_timestamp']].copy()
    d['order_month']=d.order_purchase_timestamp.dt.to_period('M')
    d['cohort_month']=d.groupby('customer_unique_id').order_month.transform('min')
    d['period']=(d.order_month.astype('int64')-d.cohort_month.astype('int64')).astype(int)
    n=d.groupby(['cohort_month','period']).customer_unique_id.nunique().rename('users').reset_index()
    # 补齐 0 用户月份，热力图中的 0 与“无数据”可区分。
    cutoff_period=d.order_month.max()
    cohorts=pd.PeriodIndex(n['cohort_month'].unique(),freq='M')
    grid=pd.MultiIndex.from_tuples([(c,p) for c in cohorts for p in range(cutoff_period.ordinal-c.ordinal+1)],names=['cohort_month','period']).to_frame(index=False)
    n=grid.merge(n,on=['cohort_month','period'],how='left').fillna({'users':0})
    n['users']=n['users'].astype(int); n=n.sort_values(['cohort_month','period'])
    n['cohort_size']=n.groupby('cohort_month').users.transform('first'); n['retention_rate']=n.users/n.cohort_size
    # 后续会用全局数据截止月判断 cohort 成熟度；不把尾部 cohort 与成熟 cohort 横比。
    cutoff=d.order_month.max(); n['months_observed']=(cutoff.ordinal-pd.PeriodIndex(n['cohort_month'],freq='M').asi8).astype(int)
    n['m3_mature']=n['months_observed']>=3
    n['cohort_month']=n.cohort_month.astype(str); return n

def ab_simulation(f: pd.DataFrame, seed=20260724) -> dict:
    """可复现的模拟 A/B：仅随机分组并施加假设 uplift，不能作为真实实验结论。"""
    rng=np.random.default_rng(seed); users=f[f.is_valid_analysis].customer_unique_id.drop_duplicates().to_frame()
    users['group']=rng.choice(['control','treatment'],len(users)); base=rng.binomial(1,.100,len(users)); effect=(users.group.eq('treatment') & (rng.random(len(users))<.018)).astype(int)
    users['converted']=np.maximum(base,effect); a=users[users.group=='control'].converted; b=users[users.group=='treatment'].converted
    diff=b.mean()-a.mean(); se=np.sqrt(a.mean()*(1-a.mean())/len(a)+b.mean()*(1-b.mean())/len(b))
    z=diff/se; p=2*stats.norm.sf(abs(z))
    pooled=(a.sum()+b.sum())/(len(a)+len(b)); n_harm=2/(1/len(a)+1/len(b))
    # 近似 MDE：双侧 alpha=.05、power=.80、两组规模近似相等。
    mde=(stats.norm.ppf(.975)+stats.norm.ppf(.8))*np.sqrt(2*pooled*(1-pooled)/n_harm)
    return {'type':'模拟A/B（统计方法演示），不是 Olist 实际实验','control_n':int(len(a)),'treatment_n':int(len(b)),'control_rate':float(a.mean()),'treatment_rate':float(b.mean()),'uplift_pp':float(diff),'ci95_low':float(diff-1.96*se),'ci95_high':float(diff+1.96*se),'z_stat':float(z),'p_value':float(p),'alpha':0.05,'approx_mde_pp_80_power':float(mde)}

def run(raw_dir:Path, output_dir:Path, data_mode: str = 'UNKNOWN') -> dict:
    output_dir.mkdir(parents=True,exist_ok=True); f,q=load_and_clean(raw_dir); valid=f[f.is_valid_analysis].copy()
    monthly=monthly_kpis(f); growth=growth_decomposition(f); rfm=rfm_table(f); cohort=cohort_table(f)
    category=valid.groupby('category').agg(gmv=('gmv','sum'),orders=('order_id','nunique'),aov=('gmv','mean'),avg_review=('review_score','mean')).reset_index().sort_values('gmv',ascending=False)
    state=valid.groupby('customer_state').agg(gmv=('gmv','sum'),orders=('order_id','nunique'),users=('customer_unique_id','nunique')).reset_index().sort_values('gmv',ascending=False)
    payment=valid.groupby('payment_type').agg(gmv=('gmv','sum'),orders=('order_id','nunique'),aov=('gmv','mean')).reset_index()
    delivery=valid[valid.late_delivery.notna()].groupby('late_delivery').agg(orders=('order_id','nunique'),avg_review=('review_score','mean'),review_coverage=('review_score','count'),gmv=('gmv','sum')).reset_index()
    rfm_summary=rfm.groupby('segment').agg(users=('customer_unique_id','nunique'),revenue=('monetary','sum'),avg_frequency=('frequency','mean')).reset_index()
    for name,df in {'order_fact':f,'monthly_kpis':monthly,'growth_decomposition':growth,'rfm_customers':rfm,'rfm_summary':rfm_summary,'cohort_retention':cohort,'category_kpis':category,'state_kpis':state,'payment_kpis':payment,'delivery_impact':delivery,'data_quality':q}.items(): df.to_csv(output_dir/f'{name}.csv',index=False)
    ab=ab_simulation(f); (output_dir/'ab_simulation.json').write_text(json.dumps(ab,ensure_ascii=False,indent=2),encoding='utf-8')
    summary={'data_mode':data_mode,'valid_orders':int(len(valid)),'valid_users':int(valid.customer_unique_id.nunique()),'gmv':float(valid.gmv.sum()),'repeat_rate':float((valid.groupby('customer_unique_id').order_id.nunique().ge(2)).mean()),'data_max_purchase_date':str(valid.order_purchase_timestamp.max().date()),'latest_month':monthly.iloc[-1].to_dict(),'ab':ab}
    (output_dir/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,default=str),encoding='utf-8'); return summary
