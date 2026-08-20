PRAGMA foreign_keys = ON;

DROP VIEW IF EXISTS vw_line_performance;
DROP TABLE IF EXISTS fact_production;
DROP TABLE IF EXISTS dim_machine;
DROP TABLE IF EXISTS dim_date;

CREATE TABLE dim_date (
    date_key TEXT PRIMARY KEY,
    year INTEGER NOT NULL,
    quarter TEXT NOT NULL,
    month_number INTEGER NOT NULL,
    month_name TEXT NOT NULL,
    year_month TEXT NOT NULL,
    week_number INTEGER NOT NULL,
    week_start_date TEXT NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_name TEXT NOT NULL,
    day_of_week_number INTEGER NOT NULL,
    is_weekend TEXT NOT NULL,
    is_month_end TEXT NOT NULL,
    fiscal_year INTEGER NOT NULL,
    fiscal_period INTEGER NOT NULL
);

CREATE TABLE dim_machine (
    line_id TEXT PRIMARY KEY,
    line_name TEXT NOT NULL,
    area TEXT NOT NULL,
    machine_type TEXT NOT NULL,
    primary_product TEXT NOT NULL,
    commissioned_year INTEGER NOT NULL,
    planned_minutes_per_shift INTEGER NOT NULL,
    standard_rate_units_per_hour REAL NOT NULL,
    baseline_availability REAL NOT NULL,
    baseline_performance REAL NOT NULL,
    baseline_quality REAL NOT NULL,
    bottleneck_risk TEXT NOT NULL,
    maintenance_strategy TEXT NOT NULL
);

CREATE TABLE fact_production (
    production_id TEXT PRIMARY KEY,
    date_key TEXT NOT NULL,
    line_id TEXT NOT NULL,
    shift TEXT NOT NULL,
    shift_start_time TEXT NOT NULL,
    shift_end_time TEXT NOT NULL,
    target_quantity INTEGER NOT NULL,
    production_quantity INTEGER NOT NULL,
    good_quantity INTEGER NOT NULL,
    scrap_quantity INTEGER NOT NULL,
    downtime_minutes INTEGER NOT NULL,
    downtime_category TEXT NOT NULL,
    defect_category TEXT NOT NULL,
    operator_count INTEGER NOT NULL,
    availability REAL NOT NULL,
    performance REAL NOT NULL,
    quality REAL NOT NULL,
    oee REAL NOT NULL,
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (line_id) REFERENCES dim_machine(line_id),
    CHECK (target_quantity >= 0),
    CHECK (production_quantity >= 0),
    CHECK (good_quantity >= 0),
    CHECK (scrap_quantity >= 0),
    CHECK (downtime_minutes >= 0)
);

CREATE INDEX idx_fact_production_date
    ON fact_production(date_key);

CREATE INDEX idx_fact_production_line
    ON fact_production(line_id);

CREATE INDEX idx_fact_production_downtime_category
    ON fact_production(downtime_category);

CREATE VIEW vw_line_performance AS
SELECT
    m.line_id,
    m.line_name,
    m.area,
    m.bottleneck_risk,
    SUM(f.production_quantity) AS total_production,
    SUM(f.target_quantity) AS total_target,
    SUM(f.good_quantity) AS good_units,
    SUM(f.scrap_quantity) AS scrap_units,
    SUM(f.downtime_minutes) AS downtime_minutes,
    ROUND(
        100.0 * SUM(f.production_quantity) / NULLIF(SUM(f.target_quantity), 0),
        2
    ) AS target_attainment_pct,
    ROUND(
        100.0 * SUM(f.scrap_quantity) / NULLIF(SUM(f.production_quantity), 0),
        2
    ) AS scrap_rate_pct,
    ROUND(
        100.0 * SUM(f.oee * f.target_quantity)
        / NULLIF(SUM(f.target_quantity), 0),
        2
    ) AS weighted_oee_pct
FROM fact_production AS f
JOIN dim_machine AS m
    ON f.line_id = m.line_id
GROUP BY
    m.line_id,
    m.line_name,
    m.area,
    m.bottleneck_risk;

