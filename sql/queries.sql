


-- ------------------------------------------
-- 1. Total revenue per category
-- Formula: revenue = quantity × unit_price × (1 - discount_percent/100)
-- ------------------------------------------
SELECT 
    p.category, 
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent/100.0)), 2) AS total_revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY total_revenue DESC;

-- ------------------------------------------
-- 2. Top 10 customers by total order value
-- ------------------------------------------
SELECT 
    c.customer_id, 
    c.customer_name, 
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent/100.0)), 2) AS total_order_value
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_id, c.customer_name
ORDER BY total_order_value DESC
LIMIT 10;

-- ------------------------------------------
-- 3. Month-wise order count for the last 12 months
-- ------------------------------------------
SELECT 
    strftime('%Y-%m', order_date) AS order_month, 
    COUNT(DISTINCT order_id) AS total_orders
FROM orders
WHERE order_date >= date('now', '-12 months')
GROUP BY order_month
ORDER BY order_month ASC;

-- ------------------------------------------
-- 4. Find customers who placed orders but never had any item delivered
-- ------------------------------------------
SELECT DISTINCT 
    c.customer_id, 
    c.customer_name
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE c.customer_id NOT IN (
    SELECT customer_id 
    FROM orders 
    WHERE status = 'DELIVERED' AND customer_id IS NOT NULL
);

-- ------------------------------------------
-- 5. Products that were ordered but had more returns than purchases
-- Logic: Compares returned items volume vs purchased volume based on order status
-- ------------------------------------------
SELECT 
    p.product_id, 
    p.product_name,
    SUM(CASE WHEN o.status = 'RETURNED' THEN oi.quantity ELSE 0 END) AS total_returned_qty,
    SUM(CASE WHEN o.status != 'RETURNED' THEN oi.quantity ELSE 0 END) AS total_purchased_qty
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
GROUP BY p.product_id, p.product_name
HAVING total_returned_qty > total_purchased_qty;

-- ------------------------------------------
-- 6. Calculate the return rate per category
-- Formula: (returned items / total items) * 100
-- ------------------------------------------
SELECT 
    p.category,
    SUM(CASE WHEN o.status = 'RETURNED' THEN oi.quantity ELSE 0 END) AS returned_items,
    SUM(oi.quantity) AS total_items,
    ROUND(
        CAST(SUM(CASE WHEN o.status = 'RETURNED' THEN oi.quantity ELSE 0 END) AS FLOAT) / 
        SUM(oi.quantity) * 100, 2
    ) AS return_rate_percentage
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
GROUP BY p.category
ORDER BY return_rate_percentage DESC;



-- ------------------------------------------
-- 7. Running Totals with Window Functions
-- Calculate running total of revenue per region, ordered by date.
-- ------------------------------------------
SELECT 
    o.region_code,
    DATE(o.order_date) AS order_date,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent/100.0)), 2) AS daily_revenue,
    ROUND(SUM(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent/100.0))) 
          OVER(PARTITION BY o.region_code ORDER BY DATE(o.order_date)), 2) AS running_total
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY o.region_code, DATE(o.order_date)
ORDER BY o.region_code, order_date;

-- ------------------------------------------
-- 8. Ranking with DENSE_RANK
-- Rank products by total revenue per category.
-- ------------------------------------------
WITH ProductRevenue AS (
    SELECT 
        p.category, 
        p.product_name, 
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent/100.0)) AS total_revenue
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    GROUP BY p.category, p.product_name
)
SELECT 
    category, 
    product_name, 
    ROUND(total_revenue, 2) AS total_revenue,
    DENSE_RANK() OVER(PARTITION BY category ORDER BY total_revenue DESC) AS rank_in_category
FROM ProductRevenue;

-- ------------------------------------------
-- 9. LAG/LEAD Analysis (Days between orders & Risk Flag)
-- ------------------------------------------
WITH OrderDates AS (
    SELECT 
        customer_id,
        order_date,
        LAG(order_date) OVER(PARTITION BY customer_id ORDER BY order_date) AS previous_order_date
    FROM orders
    WHERE customer_id IS NOT NULL
),
Gaps AS (
    SELECT 
        customer_id,
        order_date,
        previous_order_date,
        CAST(julianday(order_date) - julianday(previous_order_date) AS INTEGER) AS days_gap
    FROM OrderDates
    WHERE previous_order_date IS NOT NULL
),
AvgGaps AS (
    SELECT customer_id, AVG(days_gap) AS avg_gap FROM Gaps GROUP BY customer_id
)
SELECT 
    g.customer_id,
    g.order_date,
    g.previous_order_date,
    g.days_gap,
    CASE WHEN a.avg_gap > 30 THEN 'At Risk' ELSE 'Safe' END AS risk_flag
FROM Gaps g
JOIN AvgGaps a ON g.customer_id = a.customer_id;

-- ------------------------------------------
-- 10. CTE with Multiple Levels (Categorizing Customers)
-- ------------------------------------------
WITH MonthlyRevenue AS (
    SELECT 
        o.customer_id,
        strftime('%Y-%m', o.order_date) AS order_month,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent/100.0)) AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.customer_id IS NOT NULL
    GROUP BY o.customer_id, order_month
),
CategorizedCustomers AS (
    SELECT 
        customer_id, order_month,
        CASE 
            WHEN revenue > 10000 THEN 'High'
            WHEN revenue BETWEEN 5000 AND 10000 THEN 'Medium'
            ELSE 'Low'
        END AS customer_category
    FROM MonthlyRevenue
)
SELECT 
    order_month,
    customer_category,
    COUNT(customer_id) AS customer_count
FROM CategorizedCustomers
GROUP BY order_month, customer_category
ORDER BY order_month, customer_category;

-- ------------------------------------------
-- 11. NTILE for Segmentation (Lifetime Value Quartiles)
-- ------------------------------------------
WITH LifetimeValue AS (
    SELECT 
        o.customer_id,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent/100.0)) AS total_value
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.customer_id IS NOT NULL
    GROUP BY o.customer_id
),
Quartiles AS (
    SELECT 
        customer_id, total_value,
        NTILE(4) OVER(ORDER BY total_value DESC) AS quartile
    FROM LifetimeValue
)
SELECT 
    customer_id,
    ROUND(total_value, 2) AS total_value,
    quartile,
    CASE 
        WHEN quartile = 1 THEN 'Platinum'
        WHEN quartile = 2 THEN 'Gold'
        WHEN quartile = 3 THEN 'Silver'
        WHEN quartile = 4 THEN 'Bronze'
    END AS quartile_label
FROM Quartiles;

-- ------------------------------------------
-- 12. Year-over-Year Comparison
-- ------------------------------------------
WITH MonthlyTotal AS (
    SELECT 
        strftime('%Y', o.order_date) AS year,
        strftime('%m', o.order_date) AS month,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent/100.0)) AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY year, month
)
SELECT 
    year, month,
    ROUND(revenue, 2) AS revenue,
    ROUND(LAG(revenue) OVER(PARTITION BY month ORDER BY year), 2) AS prev_year_revenue,
    ROUND(((revenue - LAG(revenue) OVER(PARTITION BY month ORDER BY year)) / 
            NULLIF(LAG(revenue) OVER(PARTITION BY month ORDER BY year), 0)) * 100, 2) AS yoy_growth_percent
FROM MonthlyTotal
ORDER BY month, year;

-- ------------------------------------------
-- 13. First/Last Value Analysis (Category Shift)
-- ------------------------------------------
WITH OrderedCategories AS (
    SELECT 
        o.customer_id, p.category, o.order_date,
        ROW_NUMBER() OVER(PARTITION BY o.customer_id ORDER BY o.order_date ASC) AS first_order,
        ROW_NUMBER() OVER(PARTITION BY o.customer_id ORDER BY o.order_date DESC) AS last_order
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    WHERE o.customer_id IS NOT NULL
),
FirstLast AS (
    SELECT 
        customer_id,
        MAX(CASE WHEN first_order = 1 THEN category END) AS first_purchased_category,
        MAX(CASE WHEN last_order = 1 THEN category END) AS most_recent_category
    FROM OrderedCategories
    GROUP BY customer_id
)
SELECT 
    customer_id,
    first_purchased_category,
    most_recent_category,
    CASE WHEN first_purchased_category != most_recent_category THEN 'Yes' ELSE 'No' END AS category_shift
FROM FirstLast;

-- ------------------------------------------
-- 14. Cumulative Distribution
-- ------------------------------------------
WITH CustomerRev AS (
    SELECT 
        o.customer_id,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent/100.0)) AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.customer_id IS NOT NULL
    GROUP BY o.customer_id
),
TotalRev AS (
    SELECT SUM(revenue) AS grand_total FROM CustomerRev
),
Cumulatives AS (
    SELECT 
        c.customer_id, c.revenue,
        SUM(c.revenue) OVER(ORDER BY c.revenue DESC) AS cumulative_revenue,
        t.grand_total
    FROM CustomerRev c
    CROSS JOIN TotalRev t
)
SELECT 
    customer_id,
    ROUND(revenue, 2) AS revenue,
    ROUND(cumulative_revenue, 2) AS cumulative_revenue,
    ROUND((cumulative_revenue / grand_total) * 100, 2) AS cumulative_percent
FROM Cumulatives;

-- ------------------------------------------
-- 15 & 16. Complex CTE: Cohort Analysis (0 to 3 months) & Retention
-- ------------------------------------------
WITH Cohorts AS (
    SELECT customer_id, strftime('%Y-%m', registration_date) AS cohort_month
    FROM customers
),
OrderActivity AS (
    SELECT 
        c.customer_id, c.cohort_month,
        CAST((julianday(DATE(o.order_date)) - julianday(DATE(c.cohort_month || '-01'))) / 30 AS INTEGER) AS month_number
    FROM Cohorts c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
),
CohortAgg AS (
    SELECT 
        cohort_month, month_number,
        COUNT(DISTINCT customer_id) AS active_users
    FROM OrderActivity
    WHERE month_number BETWEEN 0 AND 3
    GROUP BY cohort_month, month_number
)
SELECT 
    cohort_month,
    MAX(CASE WHEN month_number = 0 THEN active_users ELSE 0 END) AS month_0_active,
    MAX(CASE WHEN month_number = 1 THEN active_users ELSE 0 END) AS month_1_active,
    MAX(CASE WHEN month_number = 2 THEN active_users ELSE 0 END) AS month_2_active,
    MAX(CASE WHEN month_number = 3 THEN active_users ELSE 0 END) AS month_3_active,
    ROUND(CAST(MAX(CASE WHEN month_number = 1 THEN active_users ELSE 0 END) AS FLOAT) / 
          NULLIF(MAX(CASE WHEN month_number = 0 THEN active_users ELSE 0 END), 0) * 100, 2) AS retention_rate_month_1
FROM CohortAgg
GROUP BY cohort_month
ORDER BY cohort_month DESC
LIMIT 12;