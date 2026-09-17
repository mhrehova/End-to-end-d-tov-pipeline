-- top_customers.sql
-- Question: Who are our most valuable customers, by revenue and margin?
-- Only counts fulfilled orders (excludes Zrušená/Vrátená).

SELECT
    c.CustomerID,
    c.CustomerName,
    c.Segment,
    c.Country,
    COUNT(DISTINCT o.OrderID)                AS OrderCount,
    ROUND(SUM(o.TotalAmount), 2)             AS TotalRevenue,
    ROUND(SUM(o.TotalMargin), 2)             AS TotalMargin,
    ROUND(AVG(o.TotalAmount), 2)             AS AvgOrderValue
FROM orders o
JOIN customers c ON c.CustomerID = o.CustomerID
WHERE o.Status NOT IN ('Zrušená', 'Vrátená')
GROUP BY c.CustomerID, c.CustomerName, c.Segment, c.Country
ORDER BY TotalRevenue DESC
LIMIT 10;
