"""Create ML-ready time, weather, numeric, and congestion features."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from pipeline import (
    DEFAULT_OUTPUT as DEFAULT_CLEANED_DATA,
    LOG_PATH,
    configure_logging,
)


LOGGER = logging.getLogger(__name__)
FEATURE_OUTPUT = Path(__file__).resolve().parent / "data" / "processed" / "traffic_features.csv"
REQUIRED_COLUMNS = {
    "holiday",
    "temp",
    "rain_1h",
    "snow_1h",
    "weather_main",
    "date_time",
    "traffic_volume",
}
SCALED_COLUMNS = ("temp", "rain_1h", "snow_1h", "clouds_all")
LOW_VISIBILITY_WEATHER = {"Fog", "Mist", "Haze", "Smoke", "Dust", "Sand"}
ADVERSE_WEATHER = {
    "Drizzle",
    "Fog",
    "Haze",
    "Mist",
    "Rain",
    "Sand",
    "Smoke",
    "Snow",
    "Squall",
    "Thunderstorm",
    "Tornado",
}


def _min_max_scale(values: pd.Series) -> tuple[pd.Series, float, float]:
    minimum = float(values.min())
    maximum = float(values.max())
    if maximum == minimum:
        return pd.Series(0.0, index=values.index), minimum, maximum
    return (values - minimum) / (maximum - minimum), minimum, maximum


def engineer_features(data: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of cleaned traffic data augmented with documented features."""
    missing_columns = REQUIRED_COLUMNS.difference(data.columns)
    if missing_columns:
        raise ValueError("Cleaned dataset is missing columns: " + ", ".join(sorted(missing_columns)))

    features = data.copy()
    before_shape = features.shape
    LOGGER.info("Feature engineering input shape: %d rows, %d columns", *before_shape)

    features["date_time"] = pd.to_datetime(features["date_time"], errors="coerce")
    invalid_datetime = features["date_time"].isna()
    if invalid_datetime.any():
        raise ValueError(f"Cannot engineer features: {int(invalid_datetime.sum())} invalid date_time values")

    features["hour"] = features["date_time"].dt.hour
    features["day_of_week"] = features["date_time"].dt.dayofweek
    features["is_weekend"] = features["day_of_week"].isin([5, 6]).astype("int8")
    features["hour_sin"] = np.sin(2 * np.pi * features["hour"] / 24)
    features["hour_cos"] = np.cos(2 * np.pi * features["hour"] / 24)
    features["day_of_week_sin"] = np.sin(2 * np.pi * features["day_of_week"] / 7)
    features["day_of_week_cos"] = np.cos(2 * np.pi * features["day_of_week"] / 7)
    holiday_values = features["holiday"].astype("string").str.strip().str.casefold()
    features["holiday_flag"] = (~holiday_values.isin({"", "none", "nan"}) & holiday_values.notna()).astype("int8")

    weather_main = features["weather_main"].fillna("Unknown").astype(str).str.strip().str.title()
    features["is_low_visibility"] = weather_main.isin(LOW_VISIBILITY_WEATHER).astype("int8")
    features["is_adverse_weather"] = weather_main.isin(ADVERSE_WEATHER).astype("int8")
    features["has_precipitation"] = (
        features["rain_1h"].fillna(0).gt(0) | features["snow_1h"].fillna(0).gt(0)
    ).astype("int8")

    weather_dummies = pd.get_dummies(
        weather_main,
        prefix="weather_main",
        dtype="int8",
    )
    features = pd.concat([features, weather_dummies], axis=1)

    for column in SCALED_COLUMNS:
        if column not in features:
            continue
        values = pd.to_numeric(features[column], errors="coerce")
        if values.isna().any():
            raise ValueError(f"Cannot scale {column}: cleaned data contains missing or non-numeric values")
        scaled, minimum, maximum = _min_max_scale(values)
        features[f"{column}_scaled"] = scaled
        LOGGER.debug("Min-max scaling for %s used minimum=%s maximum=%s", column, minimum, maximum)

    q1, q2, q3 = features["traffic_volume"].quantile([0.25, 0.5, 0.75]).to_numpy()
    LOGGER.debug("Congestion quartile thresholds: Q1=%s Q2=%s Q3=%s", q1, q2, q3)
    congestion_conditions = [
        features["traffic_volume"].le(q1),
        features["traffic_volume"].le(q2),
        features["traffic_volume"].le(q3),
    ]
    features["congestion_category"] = np.select(
        congestion_conditions,
        ["Low", "Medium", "High"],
        default="Severe",
    )

    LOGGER.info("Feature engineering output shape: %d rows, %d columns", *features.shape)
    LOGGER.info("Created time, weather, holiday, scaled numeric, and congestion features")
    return features


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_CLEANED_DATA, help="Path to cleaned traffic CSV")
    parser.add_argument("--output", type=Path, default=FEATURE_OUTPUT, help="Path for engineered feature CSV")
    parser.add_argument("--debug", action="store_true", help="Enable DEBUG-level logging")
    args = parser.parse_args(argv)
    configure_logging(logging.DEBUG if args.debug else logging.INFO, append=True)

    try:
        data = pd.read_csv(args.input)
        engineered = engineer_features(data)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        engineered.to_csv(args.output, index=False, date_format="%Y-%m-%d %H:%M:%S")
        LOGGER.info("Saved engineered feature dataset to %s", args.output)
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        LOGGER.error("Feature engineering failed: %s", exc, exc_info=True)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())