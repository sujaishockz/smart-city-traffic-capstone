# Data Analytics: Understanding Traffic Patterns

SQL, statistics, probability and Power BI analysis of the Metro Interstate
Traffic Volume dataset.

## Folder Structure

```
data_analytics/
├── data/
│   └── Metro_Interstate_Traffic_Volume.csv   # raw dataset (48,204 rows)
├── db/
│   └── traffic.db                            # SQLite database built from the CSV
├── sql/
│   ├── 01_create_table.sql                   # schema definition
│   ├── load_csv_to_sqlite.py                 # loads CSV -> SQLite, verifies row counts
│   ├── 02_annual_traffic_trends.sql          # annual trend queries
│   └── 03_holiday_temperature.sql            # holiday temperature queries
├── reports/
│   └── sql_traffic_analysis_results.md       # query outputs + written observations
└── README.md
```

The descriptive statistics and correlation script can be run with:

```bash
python3 sql/04_descriptive_statistics.py
python3 sql/05_probability_congestion.py
```

## Status

- [x] **SQL-Based Traffic Analysis**: data loaded into SQLite and
      verified; annual trend and holiday-temperature queries written and run
      (see `reports/sql_traffic_analysis_results.md`).
- [x] Descriptive Statistics and Correlation
- [x] Probability and Congestion Analysis
- [ ] Power BI Traffic Intelligence Dashboard
- [ ] 1–2 page Data Analytics Insights Report (final, covering all of the above)

## How to Run

1. Make sure Python 3 is installed (SQLite's `sqlite3` module is built in —
   no extra install needed).
2. From this folder, rebuild the database at any time with:
   ```bash
   cd data_analytics
   python3 sql/load_csv_to_sqlite.py
   ```
   This drops and recreates the `traffic` table from
   `data/Metro_Interstate_Traffic_Volume.csv` and prints a verification
   summary (row count, columns, date range, sample rows).
3. Run the analysis queries with any SQLite client, e.g.:
   ```bash
   sqlite3 db/traffic.db < sql/02_annual_traffic_trends.sql
   sqlite3 db/traffic.db < sql/03_holiday_temperature.sql
   ```
   or open `db/traffic.db` in [DB Browser for SQLite](https://sqlitebrowser.org/).
4. Written findings for each analysis go in `reports/`.

## Data Notes

- The raw CSV loads exactly as-is (48,204 rows in → 48,204 rows in the
  `traffic` table).
- The dataset has ~7,629 duplicate `date_time` rows and uneven year-to-year
  coverage (e.g. 2015 only has data from June onward). Both are documented in
  `reports/sql_traffic_analysis_results.md` and will be handled explicitly during
  cleaning in the Python pipeline work.
