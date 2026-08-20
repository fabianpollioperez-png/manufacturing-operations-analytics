"""Run simple data-quality controls against the manufacturing database."""

from __future__ import annotations

import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).resolve().parent.parent / "data" / "manufacturing.db"

CHECKS = {
    "Duplicate production IDs": """
        SELECT COUNT(*)
        FROM (
            SELECT production_id
            FROM fact_production
            GROUP BY production_id
            HAVING COUNT(*) > 1
        )
    """,
    "Production rows without a valid date": """
        SELECT COUNT(*)
        FROM fact_production AS f
        LEFT JOIN dim_date AS d ON f.date_key = d.date_key
        WHERE d.date_key IS NULL
    """,
    "Production rows without a valid machine": """
        SELECT COUNT(*)
        FROM fact_production AS f
        LEFT JOIN dim_machine AS m ON f.line_id = m.line_id
        WHERE m.line_id IS NULL
    """,
    "Rows where good units plus scrap do not equal production": """
        SELECT COUNT(*)
        FROM fact_production
        WHERE good_quantity + scrap_quantity <> production_quantity
    """,
    "Rows with an invalid KPI range": """
        SELECT COUNT(*)
        FROM fact_production
        WHERE availability NOT BETWEEN 0 AND 1
           OR performance NOT BETWEEN 0 AND 1.2
           OR quality NOT BETWEEN 0 AND 1
           OR oee NOT BETWEEN 0 AND 1
    """,
}


def main() -> None:
    if not DATABASE_PATH.exists():
        raise SystemExit("Database not found. Run src/build_database.py first.")

    print("DATA QUALITY REPORT")
    print("=" * 60)

    failed_checks = 0
    with sqlite3.connect(DATABASE_PATH) as connection:
        for name, query in CHECKS.items():
            issue_count = connection.execute(query).fetchone()[0]
            status = "PASS" if issue_count == 0 else "REVIEW"
            failed_checks += issue_count > 0
            print(f"{status:6} | {issue_count:5} issues | {name}")

        above_standard_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM fact_production
            WHERE performance > 1
            """
        ).fetchone()[0]

    print("=" * 60)
    print(f"Checks requiring review: {failed_checks}")
    print(
        "Business observation: "
        f"{above_standard_count} rows exceed 100% performance. "
        "This is allowed up to the agreed 120% validation threshold."
    )


if __name__ == "__main__":
    main()
