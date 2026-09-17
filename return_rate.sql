-- return_rate.sql
-- Question: Which product categories have the highest return rate,
-- and what's the revenue impact of those returns?
-- A line is counted as "returned" when it has a ReturnReason set.

SELECT
    cat.CategoryName,
    COUNT(od.OrderDetailID)                                              AS TotalLines,
    SUM(CASE WHEN od.ReturnReason IS NOT NULL THEN 1 ELSE 0 END)         AS ReturnedLines,
    ROUND(
        SUM(CASE WHEN od.ReturnReason IS NOT NULL THEN 1 ELSE 0 END) * 100.0
        / COUNT(od.OrderDetailID), 2
    )                                                                     AS ReturnRatePct,
    ROUND(
        SUM(CASE WHEN od.ReturnReason IS NOT NULL THEN od.LineTotal ELSE 0 END), 2
    )                                                                     AS ReturnedRevenue
FROM order_details od
JOIN products p     ON p.ProductID = od.ProductID
JOIN categories cat ON cat.CategoryID = p.CategoryID
GROUP BY cat.CategoryName
ORDER BY ReturnRatePct DESC;
