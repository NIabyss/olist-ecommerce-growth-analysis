"""生成确定性模拟电商数据；仅用于演示管道，不代表 Olist 实际观测。"""
from pathlib import Path
import numpy as np
import pandas as pd

SEED = 20260724

def generate(out_dir: Path, n_users: int = 3600) -> None:
    rng = np.random.default_rng(SEED)
    out_dir.mkdir(parents=True, exist_ok=True)
    users = pd.DataFrame({"customer_unique_id": [f"u{i:05d}" for i in range(n_users)],
                          "state": rng.choice(["SP","RJ","MG","RS","PR","BA"], n_users, p=[.34,.17,.15,.12,.12,.10])})
    start, end = pd.Timestamp("2017-01-01"), pd.Timestamp("2018-08-31")
    first_dates = start + pd.to_timedelta(rng.integers(0, (end-start).days, n_users), unit="D")
    orders=[]; customers=[]; items=[]; payments=[]; reviews=[]; oid=0
    categories=["health_beauty","bed_bath_table","computers_accessories","sports_leisure","furniture_decor"]
    pay_types=["credit_card","boleto","voucher"]
    for i, u in users.iterrows():
        # 分层复购倾向：模拟而非实验分组
        n=1+rng.binomial(3, .19 if i % 3 else .30)
        dates=[first_dates[i]]
        for _ in range(n-1):
            d=dates[-1]+pd.Timedelta(days=int(rng.integers(25,180)))
            if d<=end: dates.append(d)
        for d in dates:
            oid+=1; order_id=f"o{oid:06d}"; cust=f"c{oid:06d}"
            status=rng.choice(["delivered","canceled","unavailable"],p=[.93,.045,.025])
            delay=int(rng.gamma(2.2,3)); estimated=12
            delivered = d+pd.Timedelta(days=delay) if status=="delivered" else pd.NaT
            customers.append([cust,u["customer_unique_id"],u["state"]])
            orders.append([order_id,cust,status,d,delivered,d+pd.Timedelta(days=estimated)])
            k=int(rng.choice([1,2,3],p=[.78,.18,.04]))
            total=0
            for j in range(k):
                price=round(float(rng.lognormal(4.2,.55)),2); freight=round(float(rng.uniform(7,28)),2); total+=price+freight
                items.append([order_id,j+1,rng.choice(categories),price,freight])
            ptype=rng.choice(pay_types,p=[.72,.23,.05]); payments.append([order_id,ptype,total,int(rng.integers(1,7)) if ptype=="credit_card" else 1])
            if status=="delivered" and rng.random()<.83:
                score=int(np.clip(round(4.5 - .18*max(delay-estimated,0) - rng.normal(0,.8)),1,5)); reviews.append([order_id,score])
    pd.DataFrame(orders,columns=["order_id","customer_id","order_status","order_purchase_timestamp","order_delivered_customer_date","order_estimated_delivery_date"]).to_csv(out_dir/"orders.csv",index=False)
    pd.DataFrame(customers,columns=["customer_id","customer_unique_id","customer_state"]).to_csv(out_dir/"customers.csv",index=False)
    pd.DataFrame(items,columns=["order_id","order_item_id","product_category_name","price","freight_value"]).to_csv(out_dir/"order_items.csv",index=False)
    pd.DataFrame(payments,columns=["order_id","payment_type","payment_value","payment_installments"]).to_csv(out_dir/"payments.csv",index=False)
    pd.DataFrame(reviews,columns=["order_id","review_score"]).to_csv(out_dir/"reviews.csv",index=False)
    (out_dir/'DATA_MODE.txt').write_text('SIMULATED_DEMO\n', encoding='utf-8')

if __name__ == "__main__": generate(Path(__file__).resolve().parents[1]/"data/raw")
