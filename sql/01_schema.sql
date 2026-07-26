-- PostgreSQL：原始表。CSV 导入后执行本项目 SQL；金额均为 numeric，避免浮点误差。
CREATE TABLE IF NOT EXISTS customers (customer_id text PRIMARY KEY, customer_unique_id text, customer_state text);
CREATE TABLE IF NOT EXISTS orders (order_id text PRIMARY KEY, customer_id text, order_status text, order_purchase_timestamp timestamp, order_delivered_customer_date timestamp, order_estimated_delivery_date timestamp);
CREATE TABLE IF NOT EXISTS order_items (order_id text, order_item_id int, product_category_name text, price numeric, freight_value numeric);
CREATE TABLE IF NOT EXISTS payments (order_id text, payment_type text, payment_value numeric, payment_installments int);
CREATE TABLE IF NOT EXISTS reviews (order_id text, review_score numeric);

