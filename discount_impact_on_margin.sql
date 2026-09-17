-- discount_impact_on_margin.sql
-- Question: How does discount depth affect margin and sales volume?
-- Buckets order lines into discount bands and compares volume vs. margin per band.

SELECT
    CASE
        WHEN od.DiscountPct = 0             THEN '0% (bez zľavy)'
        WHEN od.DiscountPct <= 0.10         THEN '1-10%'
        WHEN od.DiscountPct <= 0.20         THEN '11-20%'
        ELSE '20%+'
    END                                          AS DiscountBand,
    COUNT(*)                                     AS Lines,
    SUM(od.Quantity)                             AS UnitsSold,
    ROUND(SUM(od.LineTotal), 2)                  AS Revenue,
    ROUND(SUM(od.MarginEUR), 2)                  AS MarginEUR,
    ROUND(AVG(od.MarginPct) * 100, 2)            AS AvgMarginPct
FROM order_details od
GROUP BY DiscountBand
ORDER BY MIN(od.DiscountPct);
