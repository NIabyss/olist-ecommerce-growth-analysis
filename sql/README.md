# SQL 执行顺序与我对质量的要求

我是在 PostgreSQL 14+ 上写的这些脚本。按顺序执行:`01_schema.sql` → 导入 CSV → `00_data_quality_checks.sql` → `02_clean_order_fact.sql` → `03_growth_and_user_analysis.sql` → `04_operations_diagnosis.sql`。

导入示例(把路径换成你自己的):

```sql
\copy orders FROM 'C:/data/olist_orders_dataset.csv' WITH (FORMAT csv, HEADER true);
\copy customers FROM 'C:/data/olist_customers_dataset.csv' WITH (FORMAT csv, HEADER true);
```

我给自己定的发布前最低标准:质量门禁里出现的关键时间 / 关联错误都要能解释清楚;`order_fact` 表里每个 `order_id` 只能有一行;GMV 用的是商品价+运费口径,不能和支付实收口径混用——这两个口径经常被搞混,我在指标口径文档里也单独强调了这一点。

另外我特意没有让 SQL 用 `CURRENT_DATE` 作为 RFM 的截止日,而是用数据里的最大下单日期 + 1 天,这样不管什么时候重跑,历史结果都是一致的,不会因为"今天是哪天"而变化。
