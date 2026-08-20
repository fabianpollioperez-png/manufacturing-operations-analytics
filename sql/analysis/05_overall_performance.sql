-- Query 05
-- Business question:
-- Which production lines show the weakest overall operational performance?

SELECT
    m.line_name,

    SUM(f.production_quantity) AS total_production,
    SUM(f.target_quantity) AS total_target,
    SUM(f.scrap_quantity) AS total_scrap,
    SUM(f.downtime_minutes) AS total_downtime,

    ROUND(
        100.0 * SUM(f.production_quantity)
        / NULLIF(SUM(f.target_quantity), 0),
        1
    ) AS target_attainment_pct,

    ROUND(
        100.0 * SUM(f.scrap_quantity)
        / NULLIF(SUM(f.production_quantity), 0),
        2
    ) AS scrap_rate_pct

FROM fact_production AS f

JOIN dim_machine AS m
    ON f.line_id = m.line_id

GROUP BY m.line_name

ORDER BY target_attainment_pct ASC;