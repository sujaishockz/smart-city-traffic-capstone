# Power BI Dashboard Specification

The SQL view in `sql/06_powerbi_queries.sql` prepares the fields required by
the Part 1 dashboard:

- `traffic_date` and `traffic_year` for daily trend analysis
- `traffic_hour` for hourly analysis
- `temp_celsius` for readable temperature values
- `traffic_category` using the assignment thresholds: below 4,500 Low,
  4,500–5,500 Medium, and above 5,500 High

## Power Query preparation

1. Import `data_analytics/data/Metro_Interstate_Traffic_Volume.csv`.
2. Set `date_time` to Date/Time, numeric weather fields to Decimal Number,
   `clouds_all` and `traffic_volume` to Whole Number, and text fields to Text.
3. Add `Hour` from `date_time`.
4. Add `Temperature Celsius` as `temp - 273.15`.
5. Add `Traffic Category` using the three thresholds above.
6. Inspect null counts and retain the duplicate-timestamp warning documented in
   `sql_traffic_analysis_results.md`.

## Required visuals

- Line chart: daily average traffic, filtered to 2015, 2016 and 2017.
- Column chart: average traffic by `traffic_hour`, filtered to 2017.
- Bar chart: average traffic by `weather_main`; report highest, lowest and the
  difference between them.
- Scatter chart: `temp_celsius` versus `traffic_volume`, with a trend line.
- KPI cards: total hours, average traffic, and average temperature.
- Slicers: hour, weather condition, and traffic category.

The actual `.pbix` dashboard must be created in Power BI Desktop. Power BI
Desktop is not available in this macOS workspace, so this repository contains
the reproducible preparation queries and dashboard specification instead of
claiming a completed binary dashboard file.