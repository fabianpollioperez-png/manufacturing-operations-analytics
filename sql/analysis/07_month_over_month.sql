-- Query 07
-- Business question:
-- How much did production change compared with the previous month?

WITH monthly_production AS (
    SELECT
        d.year_month,
        SUM(f.production_quantity) AS total_production

    FROM fact_production AS f

    JOIN dim_date AS d
        ON f.date_key = d.date_key

    GROUP BY d.year_month
),

monthly_comparison AS (
    SELECT
        year_month,
        total_production,

        LAG(total_production) OVER (
            ORDER BY year_month
        ) AS previous_month_production

    FROM monthly_production
)

SELECT
    year_month,
    total_production,
    previous_month_production,

    total_production
        - previous_month_production
        AS monthly_change_units,

    ROUND(
        100.0 *
        (total_production - previous_month_production)
        / NULLIF(previous_month_production, 0),
        2
    ) AS monthly_change_pct

FROM monthly_comparison

ORDER BY year_month;