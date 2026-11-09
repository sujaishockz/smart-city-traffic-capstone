-- 02_annual_traffic_trends.sql
-- Compare total yearly traffic volume for 2012-2017.
-- Note: 2012 and 2018 are partial years in this dataset (data starts Oct 2012
-- and ends Sep 2018), so they are shown for context but should not be
-- compared directly against the complete years 2013-2017.

SELECT
    CAST(strftime('%Y', date_time) AS INTEGER)               AS year,
    COUNT(*)                                                  AS hours_recorded,
    SUM(traffic_volume)                                       AS total_traffic_volume,
    ROUND(AVG(traffic_volume), 1)                             AS avg_hourly_traffic_volume
FROM traffic
WHERE strftime('%Y', date_time) BETWEEN '2012' AND '2017'
GROUP BY year
ORDER BY year;

-- Year-on-year change in total traffic volume
WITH yearly AS (
    SELECT
        CAST(strftime('%Y', date_time) AS INTEGER) AS year,
        SUM(traffic_volume)                        AS total_traffic_volume
    FROM traffic
    WHERE strftime('%Y', date_time) BETWEEN '2012' AND '2017'
    GROUP BY year
)
SELECT
    year,
    total_traffic_volume,
    total_traffic_volume - LAG(total_traffic_volume) OVER (ORDER BY year)               AS change_vs_prev_year,
    ROUND(
        100.0 * (total_traffic_volume - LAG(total_traffic_volume) OVER (ORDER BY year))
        / LAG(total_traffic_volume) OVER (ORDER BY year), 2
    )                                                                                     AS pct_change_vs_prev_year
FROM yearly
ORDER BY year;
