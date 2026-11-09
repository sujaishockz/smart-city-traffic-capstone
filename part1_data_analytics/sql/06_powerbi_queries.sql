-- Power BI preparation and dashboard queries.
-- Import the traffic table into Power BI, or run these queries in SQLite
-- before importing the resulting views.

DROP VIEW IF EXISTS powerbi_traffic_prepared;
CREATE VIEW powerbi_traffic_prepared AS
SELECT
    holiday,
    temp,
    ROUND(temp - 273.15, 2) AS temp_celsius,
    rain_1h,
    snow_1h,
    clouds_all,
    weather_main,
    weather_description,
    date_time,
    date(date_time) AS traffic_date,
    CAST(strftime('%Y', date_time) AS INTEGER) AS traffic_year,
    CAST(strftime('%H', date_time) AS INTEGER) AS traffic_hour,
    traffic_volume,
    CASE
        WHEN traffic_volume < 4500 THEN 'Low'
        WHEN traffic_volume <= 5500 THEN 'Medium'
        ELSE 'High'
    END AS traffic_category
FROM traffic;

-- Daily average traffic for 2015, 2016 and 2017.
SELECT traffic_date, traffic_year, ROUND(AVG(traffic_volume), 1) AS avg_traffic_volume
FROM powerbi_traffic_prepared
WHERE traffic_year IN (2015, 2016, 2017)
GROUP BY traffic_date, traffic_year
ORDER BY traffic_date;

-- Average traffic by hour for 2017.
SELECT traffic_hour, ROUND(AVG(traffic_volume), 1) AS avg_traffic_volume
FROM powerbi_traffic_prepared
WHERE traffic_year = 2017
GROUP BY traffic_hour
ORDER BY traffic_hour;

-- Weather impact summary.
SELECT
    weather_main,
    COUNT(*) AS hours_recorded,
    ROUND(AVG(traffic_volume), 1) AS avg_traffic_volume
FROM powerbi_traffic_prepared
GROUP BY weather_main
ORDER BY avg_traffic_volume DESC;

-- KPI values for dashboard cards.
SELECT
    COUNT(*) AS total_hours_analysed,
    ROUND(AVG(traffic_volume), 1) AS avg_traffic_volume,
    ROUND(AVG(temp_celsius), 2) AS avg_temperature_celsius
FROM powerbi_traffic_prepared;