WITH line_month_performance AS (
    SELECT
        d.year_month,
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

    JOIN dim_date AS d
        ON f.date_key = d.date_key

    GROUP BY
        d.year_month,
        m.line_name
)

SELECT
    year_month,
    line_name,
    total_production,
    total_target,
    total_scrap,
    total_downtime,
    target_attainment_pct,
    scrap_rate_pct,

    CASE
        WHEN target_attainment_pct < 75
             OR scrap_rate_pct > 4
        THEN 'CRITICAL'

        WHEN target_attainment_pct < 80
             OR scrap_rate_pct > 3
        THEN 'WATCH'

        ELSE 'NORMAL'
    END AS performance_status

FROM line_month_performance

WHERE
    target_attainment_pct < 80
    OR scrap_rate_pct > 3

ORDER BY
    year_month,
    target_attainment_pct;
    