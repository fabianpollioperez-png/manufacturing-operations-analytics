-- Query 03
-- Business question:
-- Which production line has the highest scrap rate?

SELECT
    m.line_name,
    SUM(f.scrap_quantity) AS total_scrap,
    SUM(f.production_quantity) AS total_production,

    ROUND(
        100.0 * SUM(f.scrap_quantity)
        / NULLIF(SUM(f.production_quantity), 0),
        2
    ) AS scrap_rate_pct

FROM fact_production AS f

JOIN dim_machine AS m
    ON f.line_id = m.line_id

GROUP BY m.line_name

ORDER BY scrap_rate_pct DESC;