-- PostgreSQL 数据质量门禁：任一 failed_rows > 0 时，先解释/修复再发布仪表盘。
SELECT 'orders_duplicate_key' AS check_name, COUNT(*)-COUNT(DISTINCT order_id) AS failed_rows FROM orders
UNION ALL SELECT 'orders_missing_customer', COUNT(*) FILTER (WHERE customer_id IS NULL) FROM orders
UNION ALL SELECT 'orders_invalid_delivery_time', COUNT(*) FILTER (WHERE order_delivered_customer_date < order_purchase_timestamp) FROM orders
UNION ALL SELECT 'orders_invalid_estimated_time', COUNT(*) FILTER (WHERE order_estimated_delivery_date < order_purchase_timestamp) FROM orders
UNION ALL SELECT 'delivered_missing_items', COUNT(*) FROM orders o LEFT JOIN order_items i USING(order_id) WHERE o.order_status='delivered' AND i.order_id IS NULL;

-- 诊断多支付订单；事实表只保留最大支付方式作分类，不将该字段当成订单总收入。
SELECT order_id, COUNT(*) payment_rows, SUM(payment_value) payment_total
FROM payments GROUP BY 1 HAVING COUNT(*) > 1 ORDER BY payment_rows DESC;
