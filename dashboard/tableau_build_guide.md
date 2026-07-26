# Tableau 仪表盘搭建指南

数据目录：`dashboard/data/`。先导入以下聚合 CSV：`monthly_kpis`、`growth_decomposition`、`rfm_summary`、`cohort_retention`、`category_kpis`、`state_kpis`、`payment_kpis`、`delivery_impact`。这些表均为汇总表，**不要建立它们之间的关系或 Join**；每张工作表使用对应数据源即可，避免重复聚合。

在任何仪表板右下角放置数据说明文本：`Olist 公开数据；GMV=已交付订单商品金额+运费；截止下单日=2018-08-29；2018-08 非完整自然月。`

## 建议创建的计算字段

在 `monthly_kpis` 数据源创建：

```tableau
GMV = SUM([gmv])
订单量 = SUM([orders])
用户数 = SUM([users])
客单价 = SUM([gmv]) / SUM([orders])
```

在 `cohort_retention` 数据源创建：

```tableau
留存率 = AVG([retention_rate])
成熟 Cohort = [m3_mature] = TRUE
```

## 工作表与字段映射

| 工作表 | 数据源 | 列 / 行 / 标记 | 关键设置 |
|---|---|---|---|
| 月度 GMV | monthly_kpis | 列：purchase_month；行：SUM(gmv) | 过滤 is_complete_month=True；折线 |
| 核心 KPI | monthly_kpis | 文本：GMV、订单量、用户数、客单价 | 取完整月或全期间，口径一致 |
| 地区 GMV | state_kpis | 行：customer_state；列：SUM(gmv) | 排序降序，条形 |
| 品类 GMV | category_kpis | 行：category；列：SUM(gmv) | Top 10，条形 |
| 新客与复购 | monthly_kpis | 列：purchase_month；行：new_users、repeat_users | 双轴或并排柱；过滤完整月 |
| 增长三因子 | growth_decomposition | 列：purchase_month；行：users / orders_per_user / aov | 三张独立小折线，避免不同量纲同轴 |
| RFM 收入贡献 | rfm_summary | 行：segment；列：SUM(revenue)；标签：SUM(users) | 条形，按收入降序 |
| Cohort 留存 | cohort_retention | 行：cohort_month；列：period；颜色：AVG(retention_rate) | 过滤 Mature Cohort=True；方块热力图；百分比格式 |
| 交付诊断 | delivery_impact | 列：late_delivery；行：AVG(avg_review) | 将 0/1 重命名为“未逾期/逾期” |
| 品类机会 | category_kpis | 列：SUM(gmv)；行：AVG(avg_review)；详情：category | 散点；加平均参考线 |
| 支付方式 | payment_kpis | 行：payment_type；列：SUM(gmv) | 标签显示 AVG(aov) |

## 三页仪表板

### P1 经营总览

顶部：4 个 KPI。中部左：月度 GMV；中部右：地区 GMV；底部：Top 10 品类和支付方式。所有趋势图过滤 `is_complete_month=True`。

### P2 用户增长

顶部：新客与复购用户；中部：三因子小折线；底部左：RFM 收入贡献；底部右：Cohort 留存热力图。页注：三因子用于定位，不代表因果归因。

### P3 运营诊断

左侧：逾期/未逾期评分对比；中部：品类 GMV×评分；右侧：支付方式。加文本卡：P0 履约、P1 高价值保护、P2 实验验证；注明“逾期与评分是相关性，不是因果”。

## 发布与展示

1. 保存为 `ecommerce_growth_diagnosis.twbx`（打包工作簿，便于备份）。
2. 发布到 Tableau Public，标题建议：`Olist 电商经营增长诊断与用户复购提升`。
3. 截取三页仪表板 PNG，保存到 `reports/figures/`；将 Tableau Public 链接加入 README。

