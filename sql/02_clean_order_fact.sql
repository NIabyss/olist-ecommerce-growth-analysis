-- 构建订单粒度事实表：先聚合商品/支付，避免多表 JOIN 造成 GMV 翻倍。
DROP TABLE IF EXISTS order_fact;
CREATE TABLE order_fact AS
WITH item_agg AS (
 SELECT order_id, SUM(price) product_amount, SUM(freight_value) freight_amount,
        COUNT(*) item_count, MODE() WITHIN GROUP (ORDER BY product_category_name) category
 FROM order_items GROUP BY 1
), payment_ranked AS (
 SELECT *, ROW_NUMBER() OVER(PARTITION BY order_id ORDER BY payment_value DESC) rn
 FROM payments
), review_agg AS (SELECT order_id, AVG(review_score) review_score FROM reviews GROUP BY 1)
SELECT o.order_id,c.customer_unique_id,c.customer_state,o.order_status,o.order_purchase_timestamp,
       DATE_TRUNC('month',o.order_purchase_timestamp)::date purchase_month,
       i.product_amount+i.freight_amount AS gmv,i.item_count,i.category,p.payment_type,p.payment_installments,
       r.review_score, EXTRACT(day FROM o.order_delivered_customer_date-o.order_purchase_timestamp) delivery_days,
       (o.order_delivered_customer_date>o.order_estimated_delivery_date) late_delivery
FROM orders o JOIN customers c USING(customer_id) LEFT JOIN item_agg i USING(order_id)
LEFT JOIN payment_ranked p ON p.order_id=o.order_id AND p.rn=1 LEFT JOIN review_agg r USING(order_id)
WHERE o.order_status='delivered' AND i.product_amount+i.freight_amount>0;

