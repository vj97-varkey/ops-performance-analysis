-- Tables: `orders` (cleaned closed orders, with `breached` flag) and `open_orders` (cleaned, still open,
-- with `age_days` as of 2026-07-01). See analysis.py.

-- 1. SLA breach rate by branch
SELECT branch, COUNT(*) AS orders,
       ROUND(100.0 * SUM(breached) / COUNT(*), 1) AS breach_pct,
       ROUND(AVG(resolution_hours), 1) AS avg_resolution_hours
FROM orders GROUP BY branch ORDER BY breach_pct DESC;

-- 2. SLA breach rate by category
SELECT category, sla_hours, COUNT(*) AS orders,
       ROUND(100.0 * SUM(breached) / COUNT(*), 1) AS breach_pct
FROM orders GROUP BY category, sla_hours ORDER BY breach_pct DESC;

-- 3. Top delay reasons among breached orders
SELECT delay_reason, COUNT(*) AS breached_orders,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM orders WHERE breached = 1), 1) AS share_pct
FROM orders WHERE breached = 1 GROUP BY delay_reason ORDER BY breached_orders DESC;

-- 4. Monthly trend
SELECT strftime('%Y-%m', order_date) AS month, COUNT(*) AS orders,
       ROUND(100.0 * SUM(breached) / COUNT(*), 1) AS breach_pct
FROM orders GROUP BY month ORDER BY month;

-- 5. Open-order backlog by branch and age bucket (as of 2026-07-01)
SELECT branch,
       COUNT(*) AS open_orders,
       SUM(CASE WHEN age_days <= 30 THEN 1 ELSE 0 END) AS age_0_30d,
       SUM(CASE WHEN age_days BETWEEN 31 AND 90 THEN 1 ELSE 0 END) AS age_31_90d,
       SUM(CASE WHEN age_days > 90 THEN 1 ELSE 0 END) AS age_over_90d,
       ROUND(AVG(age_days), 0) AS avg_age_days
FROM open_orders GROUP BY branch ORDER BY open_orders DESC;
