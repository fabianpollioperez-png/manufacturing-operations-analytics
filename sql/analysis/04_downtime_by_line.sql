-- Query 04
-- Business question:
-- Which production line generates the highest downtime?

SELECT
    m.line_name,
    SUM(f.downtime_minutes) AS total_downtime

FROM fact_production AS f

JOIN dim_machine AS m
    ON f.line_id = m.line_id

GROUP BY m.line_name

ORDER BY total_downtime DESC;