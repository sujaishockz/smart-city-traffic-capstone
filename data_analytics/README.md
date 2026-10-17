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
│   ├── 03_holiday_temperature.sql            # holiday temperature queries
│   ├── 04_descriptive_statistics.py
│   ├── 05_probability_congestion.py
│   └── 06_powerbi_queries.sql
├── reports/
│   ├── sql_traffic_analysis_results.md       # query outputs + written observations
│   ├── part1_insights_report.md
│   ├── powerbi_dashboard_spec.md
│   └── smart-city-traffic-dashboard.pbix
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
- [x] Power BI Traffic Intelligence Dashboard (prepared SQL view, specification,
      and [`smart-city-traffic-dashboard.pbix`](reports/smart-city-traffic-dashboard.pbix) deliverable)

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
   sqlite3 db/traffic.db < sql/06_powerbi_queries.sql
   ```
   or open `db/traffic.db` in [DB Browser for SQLite](https://sqlitebrowser.org/).
4. Written findings for each analysis go in `reports/`.

## Data Notes

- The raw CSV loads exactly as-is (48,204 rows in → 48,204 rows in the
  `traffic` table).
- The dataset has ~7,629 repeated `date_time` values and uneven year-to-year
   coverage (e.g. 2015 only has data from June onward). The pipeline removes 17
   exact duplicate rows while retaining non-identical observations that share a
   timestamp. See `reports/sql_traffic_analysis_results.md` and the Part 2
   methodology report.

## Power BI Dashboard Manual Check

The completed dashboard is
[`reports/smart-city-traffic-dashboard.pbix`](reports/smart-city-traffic-dashboard.pbix).
On macOS, check its package integrity with:

```bash
unzip -t reports/smart-city-traffic-dashboard.pbix
```

To verify visual behavior, open the file in Power BI Desktop on Windows and
confirm the daily, hourly, weather, and temperature/traffic visuals, KPI cards,
and hour/weather/traffic-category slicers. The ZIP integrity check passed;
interactive visual testing requires Power BI Desktop and was not available in
this macOS run.
