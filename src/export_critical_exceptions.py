"""Export critical manufacturing exceptions from SQLite to a CSV file."""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path


LAB_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = LAB_DIR / "data" / "manufacturing.db"
OUTPUT_DIR = LAB_DIR / "output"
OUTPUT_PATH = OUTPUT_DIR / "critical_exceptions.csv"

# Business rules for the current investigation.
LINE_ID = "L05"
SHIFT = "Shift 3"
START_DATE = "2025-08-01"
END_DATE = "2025-08-31"
CRITICAL_SCRAP_RATE_PCT = 8.0
CRITICAL_DOWNTIME_MINUTES = 100


EXCEPTIONS_QUERY = """
    SELECT
        f.date_key,
        d.day_name,
        f.line_id,
        m.line_name,
        m.area,
        f.shift,
        f.production_quantity,
        f.scrap_quantity,
        ROUND(
            100.0 * f.scrap_quantity
            / NULLIF(f.production_quantity, 0),
            2
        ) AS daily_scrap_rate_pct,
        f.downtime_minutes,
        f.downtime_category,
        f.defect_category,
        'Critical' AS performance_status
    FROM fact_production AS f
    JOIN dim_machine AS m
        ON f.line_id = m.line_id
    JOIN dim_date AS d
        ON f.date_key = d.date_key
    WHERE f.line_id = ?
      AND f.shift = ?
      AND f.date_key BETWEEN ? AND ?
      AND (
            100.0 * f.scrap_quantity
            / NULLIF(f.production_quantity, 0) >= ?
            OR f.downtime_minutes >= ?
      )
    ORDER BY f.date_key;
"""


def main() -> None:
    if not DATABASE_PATH.exists():
        raise SystemExit("Database not found. Run src/build_database.py first.")

    OUTPUT_DIR.mkdir(exist_ok=True)

    parameters = (
        LINE_ID,
        SHIFT,
        START_DATE,
        END_DATE,
        CRITICAL_SCRAP_RATE_PCT,
        CRITICAL_DOWNTIME_MINUTES,
    )

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(EXCEPTIONS_QUERY, parameters).fetchall()

    if not rows:
        raise SystemExit("No critical exceptions matched the business rules.")

    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(dict(row) for row in rows)

    print(f"Critical exception report created: {OUTPUT_PATH}")
    print(f"Rows exported: {len(rows)}")
    print(
        "Rules: "
        f"scrap rate >= {CRITICAL_SCRAP_RATE_PCT:.1f}% "
        f"OR downtime >= {CRITICAL_DOWNTIME_MINUTES} minutes"
    )
    print(f"Scope: {LINE_ID}, {SHIFT}, {START_DATE} to {END_DATE}")


if __name__ == "__main__":
    main()

