# Data Analytics: Understanding Traffic Patterns

SQL, statistics, probability and Power BI analysis of the Metro Interstate
Traffic Volume dataset.

## Folder Structure

```
part1_data_analytics/
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
│   ├── Power BI dashboard results.md
│   └── smart-city-traffic-dashboard.pbix
└── README.md
```

The descriptive statistics and correlation script can be run with:

```bash
python3 sql/04_descriptive_statistics.py
python3 sql/05_probability_congestion.py
```

## Reports and Outputs

| Artifact | What it contains |
|---|---|
| [SQL traffic analysis results](reports/sql_traffic_analysis_results.md) | SQL query results and written observations |
| [Part 1 insights report](reports/part1_insights_report.md) | Consolidated findings from the analytics tasks |
| [Power BI dashboard specification](reports/powerbi_dashboard_spec.md) | Dashboard fields, visuals, measures, and slicer requirements |
| [Power BI dashboard results](reports/Power%20BI%20dashboard%20results.md) | Summary of dashboard findings |
| [Power BI dashboard file](reports/smart-city-traffic-dashboard.pbix) | Power BI report package; interactive visuals and slicers verified in Power BI Desktop |
| [SQLite database](db/traffic.db) | Database generated from the source CSV |

The source dataset is [Metro Interstate Traffic Volume](data/Metro_Interstate_Traffic_Volume.csv).

### Task-to-Output Map

| Task | Output and report files |
|---|---|
| 1.1 Load CSV into SQLite | [SQLite database](db/traffic.db); [load verification and query results](reports/sql_traffic_analysis_results.md) |
| 1.2 Annual traffic trends | [SQL results and observations](reports/sql_traffic_analysis_results.md); [Part 1 insights](reports/part1_insights_report.md) |
| 1.3 Holiday temperature analysis | [SQL results and observations](reports/sql_traffic_analysis_results.md); [Part 1 insights](reports/part1_insights_report.md) |
| 2.1 Descriptive statistics | [Statistics results](reports/sql_traffic_analysis_results.md); [Part 1 insights](reports/part1_insights_report.md) |
| 2.2 Temperature/traffic correlation | [Correlation results](reports/sql_traffic_analysis_results.md); [Part 1 insights](reports/part1_insights_report.md) |
| 3 Probability and congestion | [Probability results](reports/sql_traffic_analysis_results.md); [Part 1 insights](reports/part1_insights_report.md) |
| 4.1 Power Query preparation | [Power BI queries](sql/06_powerbi_queries.sql); [dashboard specification](reports/powerbi_dashboard_spec.md) |
| 4.2 Dashboard visuals | [Power BI dashboard](reports/smart-city-traffic-dashboard.pbix); [dashboard findings](reports/Power%20BI%20dashboard%20results.md) |
| 4.3 KPI cards and slicers | [Power BI dashboard](reports/smart-city-traffic-dashboard.pbix); [dashboard specification](reports/powerbi_dashboard_spec.md) |
| Final insights report | [Part 1 insights report](reports/part1_insights_report.md) |

## Power BI Dashboard Results

The consolidated weather and temperature findings are documented in
[`reports/Power BI dashboard results.md`](reports/Power%20BI%20dashboard%20results.md).

- **Highest average traffic weather condition:** Clouds, at 3,618.4 vehicles.
- **Lowest average traffic weather condition:** Squall, at 2,061.8 vehicles.
- **Weather difference:** 1,556.7 vehicles between the highest and lowest averages.
- **Temperature/traffic relationship:** Weak positive correlation (`r = 0.1303`).
  Traffic volume is generally higher around 25–35°C, while the wider scatter shows
  that temperature alone is not a strong predictor.
- **Notable outliers/data quality:** The traffic maximum is 7,280 vehicles. Ten
  source records contain an invalid temperature of approximately -273.15°C and
  should be treated as zero-Kelvin data-quality errors.

## Status

- [x] **SQL-Based Traffic Analysis**: data loaded into SQLite and
      verified; annual trend and holiday-temperature queries written and run
      (see `reports/sql_traffic_analysis_results.md`).
- [x] Descriptive Statistics and Correlation
- [x] Probability and Congestion Analysis
- [x] Power BI preparation query, specification, and [`smart-city-traffic-dashboard.pbix`](reports/smart-city-traffic-dashboard.pbix) package are present; interactive behavior verified in Power BI Desktop (user-confirmed).
- [x] Power BI Dashboard Results Summary: Weather and temperature findings are complete in [`reports/Power BI dashboard results.md`](reports/Power%20BI%20dashboard%20results.md).

## How to Run

1. Make sure Python 3 is installed (SQLite's `sqlite3` module is built in —
   no extra install needed).
2. From this folder, rebuild the database at any time with:
   ```bash
   cd part1_data_analytics
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

## Power BI Dashboard Verification

The Power BI report package and interactive dashboard verification are complete.
Visuals, KPI cards, and slicers were checked in Power BI Desktop (user-confirmed).
The report package is
[`reports/smart-city-traffic-dashboard.pbix`](reports/smart-city-traffic-dashboard.pbix).
Its package integrity can also be checked with:

```bash
unzip -t reports/smart-city-traffic-dashboard.pbix
```

The archive integrity check passes. The interactive visual check is recorded as
complete based on the user's confirmation that the report was opened and checked
in Power BI Desktop.
