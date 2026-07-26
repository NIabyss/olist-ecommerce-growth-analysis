# 仪表盘交付(Power BI / Tableau)

我用 Tableau 做了最终的仪表盘,搭建过程按照 [Tableau 搭建指南](tableau_build_guide.md) 里我写的数据源、工作表和三页布局来做;如果你想用 Power BI 复现同样的逻辑,下面也有对应的 DAX。

导入 `dashboard/data/*.csv` 就能拿到全部数据。表之间的关系是:`monthly_kpis` 和 `growth_decomposition` 各自独立;`rfm_customers` 通过 `segment` 关联 `rfm_summary`;`cohort_retention` 独立;其余专题表也都各自独立——我特意把它们拆开,是为了避免有人在 BI 工具里把订单商品明细和订单表直接连起来求和,导致金额重复计算(这是我在写这个项目时反复提醒自己的一个坑)。首页我放了 `summary.json[data_mode]`、数据截止日和"模拟/真实"说明卡片,让人一眼能看出这份仪表盘的数据是不是真实的。

## P1 经营总览

KPI:GMV、订单量、用户数、AOV;折线图:`monthly_kpis[purchase_month]` × GMV/订单;地图或条形图:`state_kpis`;品类条形图:`category_kpis`。筛选器:月份、地区、品类、支付方式(如果加载了订单事实表)。

## P2 用户增长

堆叠柱状图:新客/复购用户;三因子表:`growth_decomposition` 里的 users、orders_per_user、aov、gmv_mom_pct;RFM 矩阵:`rfm_summary[segment]` × revenue/users;留存热力图:cohort_month × period,按 retention_rate 上色,并筛选 `m3_mature=True` 的 cohort(未成熟的 cohort 我不会拿来横向比较)。筛选器:首购 cohort、RFM 分层。

## P3 运营诊断

交付是否逾期 × 平均评分;支付方式的 GMV/AOV;品类 GMV 与评分的散点图;右侧放了一张"策略机会"卡片。筛选器:地区、品类、支付方式、月份。

## Power BI DAX(基于订单事实表)
```DAX
GMV = SUM(order_fact[gmv])
订单量 = DISTINCTCOUNT(order_fact[order_id])
用户数 = DISTINCTCOUNT(order_fact[customer_unique_id])
客单价 = DIVIDE([GMV], [订单量])
```

## Tableau 计算字段
`客单价 = SUM([gmv]) / COUNTD([order_id])`;`GMV = SUM([gmv])`;`用户数 = COUNTD([customer_unique_id])`。
