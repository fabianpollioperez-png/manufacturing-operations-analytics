"""Create the SQLite star schema and load the existing portfolio CSV files."""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
LAB_DIR = SCRIPT_DIR.parent
WORKSPACE_DIR = LAB_DIR.parent
DATA_DIR = LAB_DIR / "data"
DATABASE_PATH = DATA_DIR / "manufacturing.db"
SCHEMA_PATH = LAB_DIR / "sql" / "00_schema.sql"


def read_csv(filename: str) -> list[dict[str, str]]:
    """Read one source CSV as a list of dictionaries."""
    path = WORKSPACE_DIR / filename
    with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        return list(csv.DictReader(csv_file))


def load_dates(connection: sqlite3.Connection) -> int:
    rows = read_csv("calendar_data.csv")
    values = [
        (
            row["date"],
            int(row["year"]),
            row["quarter"],
            int(row["month_number"]),
            row["month_name"],
            row["year_month"],
            int(row["week_number"]),
            row["week_start_date"],
            int(row["day_of_month"]),
            row["day_name"],
            int(row["day_of_week_number"]),
            row["is_weekend"],
            row["is_month_end"],
            int(row["fiscal_year"]),
            int(row["fiscal_period"]),
        )
        for row in rows
    ]
    connection.executemany(
        """
        INSERT INTO dim_date VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """,
        values,
    )
    return len(values)


def load_machines(connection: sqlite3.Connection) -> int:
    rows = read_csv("machine_data.csv")
    values = [
        (
            row["line_id"],
            row["line_name"],
            row["area"],
            row["machine_type"],
            row["primary_product"],
            int(row["commissioned_year"]),
            int(row["planned_minutes_per_shift"]),
            float(row["standard_rate_units_per_hour"]),
            float(row["baseline_availability"]),
            float(row["baseline_performance"]),
            float(row["baseline_quality"]),
            row["bottleneck_risk"],
            row["maintenance_strategy"],
        )
        for row in rows
    ]
    connection.executemany(
        "INSERT INTO dim_machine VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        values,
    )
    return len(values)


def load_production(connection: sqlite3.Connection) -> int:
    rows = read_csv("production_data.csv")
    values = [
        (
            row["production_id"],
            row["date"],
            row["line_id"],
            row["shift"],
            row["shift_start_time"],
            row["shift_end_time"],
            int(row["daily_target_quantity"]),
            int(row["daily_production_quantity"]),
            int(row["good_quantity"]),
            int(row["scrap_quantity"]),
            int(row["downtime_minutes"]),
            row["downtime_category"],
            row["defect_category"],
            int(row["operator_count"]),
            float(row["availability"]),
            float(row["performance"]),
            float(row["quality"]),
            float(row["oee"]),
        )
        for row in rows
    ]
    connection.executemany(
        """
        INSERT INTO fact_production VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """,
        values,
    )
    return len(values)


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

        date_count = load_dates(connection)
        machine_count = load_machines(connection)
        production_count = load_production(connection)

        connection.commit()
        integrity_result = connection.execute(
            "PRAGMA integrity_check"
        ).fetchone()[0]

    print(f"Database created: {DATABASE_PATH}")
    print(f"dim_date: {date_count:,} rows")
    print(f"dim_machine: {machine_count:,} rows")
    print(f"fact_production: {production_count:,} rows")
    print(f"SQLite integrity check: {integrity_result}")


if __name__ == "__main__":
    main()

