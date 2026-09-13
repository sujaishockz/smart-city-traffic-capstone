"""
load_csv_to_sqlite.py

Load the Metro Interstate Traffic Volume CSV into a SQLite database
and verify that it loaded correctly.

Usage (from the data_analytics/ folder):
    python sql/load_csv_to_sqlite.py
"""

import csv
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "Metro_Interstate_Traffic_Volume.csv"
DB_PATH = BASE_DIR / "db" / "traffic.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "01_create_table.sql"


def load_data() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Create schema
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        cur.executescript(f.read())

    # Load CSV rows
    with open(CSV_PATH, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = [
            (
                row["holiday"],
                float(row["temp"]),
                float(row["rain_1h"]),
                float(row["snow_1h"]),
                int(row["clouds_all"]),
                row["weather_main"],
                row["weather_description"],
                row["date_time"],
                int(row["traffic_volume"]),
            )
            for row in reader
        ]

    cur.executemany(
        """
        INSERT INTO traffic (
            holiday, temp, rain_1h, snow_1h, clouds_all,
            weather_main, weather_description, date_time, traffic_volume
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    conn.commit()

    # --- Verification ---
    cur.execute("SELECT COUNT(*) FROM traffic;")
    row_count = cur.fetchone()[0]
    print(f"Loaded {row_count} rows into {DB_PATH.name} (source CSV had {len(rows)} rows).")

    cur.execute("PRAGMA table_info(traffic);")
    print("Columns:", [c[1] for c in cur.fetchall()])

    cur.execute("SELECT MIN(date_time), MAX(date_time) FROM traffic;")
    print("Date range:", cur.fetchone())

    cur.execute("SELECT * FROM traffic LIMIT 3;")
    print("Sample rows:")
    for r in cur.fetchall():
        print(" ", r)

    conn.close()


if __name__ == "__main__":
    load_data()
