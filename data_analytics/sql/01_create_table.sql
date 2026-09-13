-- 01_create_table.sql
-- Create the schema for the Metro Interstate Traffic Volume dataset.
-- Run this before loading the CSV data (see load_csv_to_sqlite.py).

DROP TABLE IF EXISTS traffic;

CREATE TABLE traffic (
    holiday             TEXT,       -- 'None' or the name of a US federal holiday
    temp                REAL,       -- temperature in Kelvin
    rain_1h             REAL,       -- rain in the last hour, mm
    snow_1h             REAL,       -- snow in the last hour, mm
    clouds_all          INTEGER,    -- cloud cover percentage
    weather_main        TEXT,       -- short weather category, e.g. Clear, Clouds, Rain
    weather_description TEXT,       -- detailed weather description
    date_time           TEXT,       -- hourly timestamp, 'YYYY-MM-DD HH:MM:SS'
    traffic_volume      INTEGER     -- westbound I-94 hourly traffic volume
);

CREATE INDEX IF NOT EXISTS idx_traffic_datetime ON traffic (date_time);
