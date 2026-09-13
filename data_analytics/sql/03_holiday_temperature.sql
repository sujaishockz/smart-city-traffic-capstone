-- 03_holiday_temperature.sql
-- Compare temperature patterns for 2015, 2016 and 2017 during
-- New Year's Day and Labor Day.
--
-- The 'holiday' column is only flagged on the first hour (00:00) of a
-- holiday in this dataset, so we match on calendar date instead of the
-- holiday flag, to capture the full day's temperature readings.

-- New Year's Day (Jan 1) temperature by year
SELECT
    CAST(strftime('%Y', date_time) AS INTEGER) AS year,
    'New Year''s Day'                          AS holiday_name,
    COUNT(*)                                   AS hours_recorded,
    ROUND(AVG(temp), 2)                        AS avg_temp_kelvin,
    ROUND(AVG(temp) - 273.15, 2)               AS avg_temp_celsius,
    ROUND(AVG(traffic_volume), 1)              AS avg_traffic_volume
FROM traffic
WHERE strftime('%m-%d', date_time) = '01-01'
  AND strftime('%Y', date_time) IN ('2015', '2016', '2017')
GROUP BY year

UNION ALL

-- Labor Day (first Monday of September) temperature by year
-- 2015-09-07, 2016-09-05, 2017-09-04
SELECT
    CAST(strftime('%Y', date_time) AS INTEGER) AS year,
    'Labor Day'                                AS holiday_name,
    COUNT(*)                                   AS hours_recorded,
    ROUND(AVG(temp), 2)                        AS avg_temp_kelvin,
    ROUND(AVG(temp) - 273.15, 2)               AS avg_temp_celsius,
    ROUND(AVG(traffic_volume), 1)              AS avg_traffic_volume
FROM traffic
WHERE date(date_time) IN ('2015-09-07', '2016-09-05', '2017-09-04')
GROUP BY year
ORDER BY holiday_name, year;
