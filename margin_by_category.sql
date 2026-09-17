-- margin_by_category.sql
-- Question: Which product categories generate the most revenue and margin?
-- Only counts orders that were actually fulfilled (excludes Zrušená/Vrátená),
-- so the numbers reflect real, kept revenue rather than gross bookings.

WITH category_totals AS (
    SELECT
        c.CategoryName,
        COUNT(DISTINCT od.OrderDetailID)                      AS LinesSold,
        SUM(od.Quantity)                                       AS UnitsSold,
        SUM(od.LineTotal)                                      AS Revenue,
        SUM(od.Cost * od.Quantity)                             AS TotalCost,
        SUM(od.MarginEUR)                                      AS MarginEUR,
        SUM(od.MarginEUR) * 100.0 / NULLIF(SUM(od.LineTotal), 0) AS MarginPct
    FROM order_details od
    JOIN products p   ON p.ProductID = od.ProductID
    JOIN categories c ON c.CategoryID = p.CategoryID
    JOIN orders o     ON o.OrderID = od.OrderID
    WHERE o.Status NOT IN ('Zrušená', 'Vrátená')
    GROUP BY c.CategoryName
)
SELECT
    CategoryName,
    LinesSold,
    UnitsSold,
    ROUND(Revenue, 2)      AS Revenue,
    ROUND(TotalCost, 2)    AS TotalCost,
    ROUND(MarginEUR, 2)    AS MarginEUR,
    ROUND(MarginPct, 2)    AS MarginPct,
    -- window function: how each category's margin % compares to the overall average
    ROUND(AVG(MarginPct) OVER (), 2)                       AS AvgMarginPctAllCategories,
    ROUND(MarginPct - AVG(MarginPct) OVER (), 2)           AS MarginPctVsAverage,
    RANK() OVER (ORDER BY MarginEUR DESC)                  AS MarginEurRank
FROM category_totals
ORDER BY MarginEUR DESC;
