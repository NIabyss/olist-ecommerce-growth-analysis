# 数据说明

我用的是 Kaggle 上的 **Olist Brazilian E-Commerce Dataset**(`olistbr/brazilian-ecommerce`),公开许可证和字段说明以 Kaggle 页面为准。这份数据覆盖 2016–2018 年大约 10 万笔订单,包含订单、客户、订单商品、支付、评价和商品维度表,是我找到的、字段够完整、能支撑"增长诊断"这个主题的公开数据集。

原始 CSV 我没有放进这个仓库——一是文件本身有 180MB 左右,不适合直接塞进 Git 仓库;二是这是 Kaggle 上的第三方数据,分发原始文件也不太合适。想复现的话,从 [Kaggle 页面](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) 下载后放进 `data/raw/`,`run_olist.py` 兼容 Kaggle 的原始文件名(比如 `olist_orders_dataset.csv`),会自动生成分析需要的标准别名。

在还没拿到真实数据、或者只是想快速看一下项目能不能跑起来的时候,我写了 `src/generate_demo_data.py` 来生成一份**确定性的模拟数据集**,只用来验证全链路和演示统计检验,报告里所有基于模拟数据的结论都会显著标出来,不会和真实结果混在一起。

| 文件 | 粒度 | 用途 |
|---|---|---|
| `orders.csv` | 订单 | 下单、状态、交付日期 |
| `customers.csv` | 订单客户映射 | `customer_unique_id` 用来识别复购 |
| `order_items.csv` | 订单-商品行 | 商品金额、运费、品类 |
| `payments.csv` | 订单支付行 | 支付方式、分期 |
| `reviews.csv` | 订单评价 | 评分 |
| `products.csv` | 商品 | 通过 `product_id` 关联品类 |
