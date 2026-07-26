-- 专题诊断：交付时效、品类和取消订单。每个查询均在订单粒度运行。
SELECT late_delivery,COUNT(*) orders,COUNT(review_score) reviewed_orders,
       AVG(review_score) avg_review,AVG(gmv) aov
FROM order_fact WHERE late_delivery IS NOT NULL GROUP BY 1 ORDER BY 1;

SELECT category,COUNT(*) orders,SUM(gmv) gmv,AVG(review_score) avg_review
FROM order_fact GROUP BY 1 ORDER BY gmv DESC;

SELECT order_status,COUNT(*) orders,COUNT(*)::numeric/SUM(COUNT(*)) OVER() order_share
FROM orders GROUP BY 1 ORDER BY orders DESC;
