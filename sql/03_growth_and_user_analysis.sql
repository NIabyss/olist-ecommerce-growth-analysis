-- 可独立运行：月度经营、首次购买、新复购、RFM 和 cohort 留存。
WITH x AS (
 SELECT *, MIN(order_purchase_timestamp) OVER(PARTITION BY customer_unique_id) first_purchase
 FROM order_fact
), m AS (
 SELECT purchase_month, SUM(gmv) gmv, COUNT(*) orders, COUNT(DISTINCT customer_unique_id) users,
        COUNT(DISTINCT customer_unique_id) FILTER(WHERE DATE_TRUNC('month',first_purchase)=purchase_month) new_users,
        COUNT(DISTINCT customer_unique_id) FILTER(WHERE DATE_TRUNC('month',first_purchase)<purchase_month) repeat_users
 FROM x GROUP BY 1
)
SELECT *, gmv/NULLIF(orders,0) aov, orders::numeric/NULLIF(users,0) orders_per_user,
       LAG(gmv) OVER(ORDER BY purchase_month) prev_gmv,
       gmv/NULLIF(LAG(gmv) OVER(ORDER BY purchase_month),0)-1 gmv_mom
FROM m ORDER BY purchase_month;

-- RFM：分析日为最新购买日+1；NTILE 是相对评分，需定期复标定。
WITH analysis_date AS (SELECT MAX(order_purchase_timestamp::date)+1 AS as_of_date FROM order_fact), rfm_base AS (
 SELECT customer_unique_id, (SELECT as_of_date FROM analysis_date)-MAX(order_purchase_timestamp::date) recency_days,
        COUNT(*) frequency,SUM(gmv) monetary FROM order_fact GROUP BY 1
), scored AS (
 SELECT *, 6-NTILE(5) OVER(ORDER BY recency_days) r, NTILE(5) OVER(ORDER BY frequency) f,
        NTILE(5) OVER(ORDER BY monetary) m FROM rfm_base
)
SELECT *, CASE WHEN r+f+m>=12 THEN '高价值' WHEN r+f+m>=9 THEN '潜力' WHEN r+f+m>=6 THEN '需唤回' ELSE '沉睡' END segment FROM scored;

-- Cohort：month_number=0 为首购月；请只横向比较已成熟的 cohort。
WITH base AS (
 SELECT customer_unique_id,DATE_TRUNC('month',order_purchase_timestamp)::date order_month,
 MIN(DATE_TRUNC('month',order_purchase_timestamp)::date) OVER(PARTITION BY customer_unique_id) cohort_month FROM order_fact
), activity AS (
 SELECT cohort_month, order_month, COUNT(DISTINCT customer_unique_id) users FROM base GROUP BY 1,2
), sized AS (SELECT *, FIRST_VALUE(users) OVER(PARTITION BY cohort_month ORDER BY order_month) cohort_size FROM activity)
SELECT cohort_month, order_month,
       (EXTRACT(YEAR FROM age(order_month,cohort_month))*12 + EXTRACT(MONTH FROM age(order_month,cohort_month)))::int AS month_number,
       users, users::numeric/cohort_size retention_rate
FROM sized ORDER BY 1,2;
