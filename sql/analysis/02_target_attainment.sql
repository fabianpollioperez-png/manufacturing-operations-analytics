-- Query 02
-- Business question:
-- Which production lines are closest to meeting their production targets?

SELECT
    m.line_name,
    SUM(f.production_quantity) AS total_production,
    SUM(f.target_quantity) AS total_target,

    ROUND(
        100.0 * SUM(f.production_quantity)
        / NULLIF(SUM(f.target_quantity), 0),
        1
    ) AS target_attainment_pct

FROM fact_production AS f

JOIN dim_machine AS m
    ON f.line_id = m.line_id

GROUP BY m.line_name

ORDER BY target_attainment_pct DESC;