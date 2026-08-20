-- Query 06
-- Business question:
-- How does production change month by month?

SELECT
    d.year_month,
    SUM(f.production_quantity) AS total_production,
    SUM(f.target_quantity) AS total_target

FROM fact_production AS f

JOIN dim_date AS d
    ON f.date_key = d.date_key

GROUP BY d.year_month

ORDER BY d.year_month;