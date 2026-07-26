# 数据字典

| 字段 | 表 | 含义 | 注意事项 |
|---|---|---|---|
| `order_id` | orders / items / payments / reviews | 订单主键 | 一单可多商品、可多支付行 |
| `customer_id` | orders / customers | 订单级客户 ID | 不能用于识别复购 |
| `customer_unique_id` | customers | 跨订单客户 ID | 用户分析主键 |
| `order_purchase_timestamp` | orders | 下单时间 | 经营月份按此字段截断 |
| `order_status` | orders | 订单状态 | GMV 口径仅 `delivered` |
| `price` / `freight_value` | order_items | 商品价 / 运费 | 订单金额先在订单粒度汇总 |
| `payment_type` | payments | 支付方式 | 多支付订单取金额最高方式 |
| `review_score` | reviews | 1–5 星满意度 | 非所有订单都有评价 |

