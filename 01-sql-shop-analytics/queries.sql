-- 1. Общая статистика по базе
SELECT
    (SELECT COUNT(*) FROM customers) AS customers,
    (SELECT COUNT(*) FROM orders) AS orders,
    (SELECT COUNT(*) FROM orders WHERE status = 'delivered') AS delivered;


-- 2. Выручка по категориям товаров
SELECT
    p.category,
    ROUND(SUM(oi.quantity * p.price), 2) AS revenue,
    SUM(oi.quantity) AS units
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN orders o ON o.order_id = oi.order_id
WHERE o.status = 'delivered'
GROUP BY p.category
ORDER BY revenue DESC;


-- 3. Города, где средний чек выше 20000
SELECT
    c.city,
    COUNT(DISTINCT o.order_id) AS orders,
    ROUND(SUM(oi.quantity * p.price) / COUNT(DISTINCT o.order_id), 2) AS avg_check
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
JOIN products p ON p.product_id = oi.product_id
WHERE o.status = 'delivered'
GROUP BY c.city
HAVING avg_check > 20000
ORDER BY avg_check DESC;


-- 4. Топ-10 клиентов по выручке
SELECT
    c.customer_id,
    c.name,
    c.city,
    COUNT(DISTINCT o.order_id) AS orders,
    ROUND(SUM(oi.quantity * p.price), 2) AS revenue
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
JOIN products p ON p.product_id = oi.product_id
WHERE o.status = 'delivered'
GROUP BY c.customer_id
ORDER BY revenue DESC
LIMIT 10;


-- 5. Выручка и число заказов по месяцам
SELECT
    strftime('%Y-%m', o.order_date) AS month,
    COUNT(DISTINCT o.order_id) AS orders,
    ROUND(SUM(oi.quantity * p.price), 2) AS revenue
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
JOIN products p ON p.product_id = oi.product_id
WHERE o.status = 'delivered'
GROUP BY month
ORDER BY month;


-- 6. Средний чек по месяцам через CTE
WITH order_totals AS (
    SELECT
        o.order_id,
        strftime('%Y-%m', o.order_date) AS month,
        SUM(oi.quantity * p.price) AS total
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p ON p.product_id = oi.product_id
    WHERE o.status = 'delivered'
    GROUP BY o.order_id
)
SELECT
    month,
    COUNT(*) AS orders,
    ROUND(AVG(total), 2) AS avg_check
FROM order_totals
GROUP BY month
ORDER BY month;


-- 7. Оконная функция: рейтинг товаров внутри своей категории
WITH product_revenue AS (
    SELECT
        p.product_id,
        p.name,
        p.category,
        SUM(oi.quantity * p.price) AS revenue
    FROM products p
    JOIN order_items oi ON oi.product_id = p.product_id
    JOIN orders o ON o.order_id = oi.order_id
    WHERE o.status = 'delivered'
    GROUP BY p.product_id
)
SELECT
    category,
    name,
    ROUND(revenue, 2) AS revenue,
    RANK() OVER (PARTITION BY category ORDER BY revenue DESC) AS rank_in_category,
    ROUND(100.0 * revenue / SUM(revenue) OVER (PARTITION BY category), 1) AS pct_of_category
FROM product_revenue
ORDER BY category, rank_in_category;


-- 8. Оконная функция: накопительная выручка по месяцам
WITH monthly AS (
    SELECT
        strftime('%Y-%m', o.order_date) AS month,
        SUM(oi.quantity * p.price) AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p ON p.product_id = oi.product_id
    WHERE o.status = 'delivered'
    GROUP BY month
)
SELECT
    month,
    ROUND(revenue, 2) AS revenue,
    ROUND(SUM(revenue) OVER (ORDER BY month), 2) AS cumulative_revenue
FROM monthly
ORDER BY month;


-- 9. Retention: сколько клиентов вернулись за вторым заказом
WITH per_customer AS (
    SELECT customer_id, COUNT(*) AS orders
    FROM orders
    WHERE status = 'delivered'
    GROUP BY customer_id
)
SELECT
    COUNT(*) AS active_customers,
    SUM(CASE WHEN orders >= 2 THEN 1 ELSE 0 END) AS repeat_customers,
    ROUND(100.0 * SUM(CASE WHEN orders >= 2 THEN 1 ELSE 0 END) / COUNT(*), 1) AS repeat_rate
FROM per_customer;


-- 10. Доля отменённых заказов по месяцам
SELECT
    strftime('%Y-%m', order_date) AS month,
    COUNT(*) AS total_orders,
    SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled,
    ROUND(100.0 * SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) / COUNT(*), 1) AS cancel_rate
FROM orders
GROUP BY month
ORDER BY month;
