-- Query 01
-- Business question:
-- Which production line generates the highest production output?

SELECT
    m.line_name,
    SUM(f.production_quantity) AS total_production
FROM fact_production AS f
JOIN dim_machine AS m
    ON f.line_id = m.line_id
GROUP BY m.line_name
ORDER BY total_production DESC;