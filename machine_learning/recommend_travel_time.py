"""Recommend low-traffic two-hour travel windows by day type and weather."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import joblib
import pandas as pd

if __package__:
    from .train_supervised import CATEGORICAL_FEATURES, DEFAULT_INPUT, NUMERIC_FEATURES
else:
    from train_supervised import CATEGORICAL_FEATURES, DEFAULT_INPUT, NUMERIC_FEATURES


LOGGER = logging.getLogger(__name__)
DEFAULT_OUTPUT = Path(__file__).resolve().parent
DEFAULT_MODEL = DEFAULT_OUTPUT / "models" / "traffic_volume_regressor.joblib"
WEATHER_NUMERIC_FEATURES = ("temp", "rain_1h", "snow_1h", "clouds_all")


def build_candidate_features(
    history: pd.DataFrame, day_type: str, weather: str, month: int
) -> tuple[pd.DataFrame, int]:
    if day_type not in {"weekday", "weekend"}:
        raise ValueError("day_type must be 'weekday' or 'weekend'")
    if not 1 <= month <= 12:
        raise ValueError("month must be between 1 and 12")
    required = {"weather_main", *WEATHER_NUMERIC_FEATURES}
    missing = required.difference(history.columns)
    if missing:
        raise ValueError("History is missing required columns: " + ", ".join(sorted(missing)))

    weather_values = history["weather_main"].fillna("Unknown").astype(str).str.strip().str.title()
    weather_name = weather.strip().title()
    weather_history = history.loc[weather_values == weather_name]
    if weather_history.empty:
        raise ValueError(f"No historical rows found for weather condition: {weather_name}")
    weather_medians = {
        column: float(pd.to_numeric(weather_history[column], errors="coerce").median())
        for column in WEATHER_NUMERIC_FEATURES
    }
    if any(pd.isna(value) for value in weather_medians.values()):
        raise ValueError(f"Weather condition {weather_name} has missing numeric weather values")

    day_numbers = range(5) if day_type == "weekday" else range(5, 7)
    candidates = []
    for day_number in day_numbers:
        for hour in range(24):
            candidates.append(
                {
                    "hour": hour,
                    "day_of_week": day_number,
                    "is_weekend": int(day_number >= 5),
                    "holiday_flag": 0,
                    "month": month,
                    **weather_medians,
                    "weather_main": weather_name,
                }
            )
    features = pd.DataFrame(candidates, columns=[*NUMERIC_FEATURES, *CATEGORICAL_FEATURES])
    return features, int(len(weather_history))


def recommend_for_conditions(
    model: object,
    history: pd.DataFrame,
    day_type: str,
    weather: str,
    month: int = 6,
    window_hours: int = 2,
    top_n: int = 3,
) -> dict[str, object]:
    if not 1 <= window_hours <= 24 or top_n < 1:
        raise ValueError("window_hours must be 1-24 and top_n must be positive")
    features, weather_records = build_candidate_features(history, day_type, weather, month)
    features["predicted_traffic"] = model.predict(features)
    hourly = features.groupby("hour", as_index=False)["predicted_traffic"].mean()
    windows = []
    for start_hour in range(24 - window_hours + 1):
        segment = hourly.iloc[start_hour : start_hour + window_hours]
        windows.append(
            {
                "start_hour": start_hour,
                "end_hour": start_hour + window_hours,
                "mean_predicted_traffic": float(segment["predicted_traffic"].mean()),
            }
        )
    windows.sort(key=lambda item: item["mean_predicted_traffic"])

    selected = []
    occupied_hours: set[int] = set()
    for window in windows:
        hours = set(range(window["start_hour"], window["end_hour"]))
        if hours.isdisjoint(occupied_hours):
            selected.append(
                {
                    "window": f"{window['start_hour']:02d}:00-{window['end_hour']:02d}:00",
                    "mean_predicted_traffic": window["mean_predicted_traffic"],
                }
            )
            occupied_hours.update(hours)
            if len(selected) == top_n:
                break
    return {
        "day_type": day_type,
        "weather": weather.strip().title(),
        "month": month,
        "weather_history_records": weather_records,
        "model": "hist_gradient_boosting traffic-volume regressor",
        "windows": selected,
    }


def generate_recommendation_report(
    model: object, history: pd.DataFrame, output_dir: Path, month: int = 6
) -> list[dict[str, object]]:
    common_weather = history["weather_main"].fillna("Unknown").astype(str).str.strip().str.title().value_counts().head(3)
    results = [
        recommend_for_conditions(model, history, day_type, weather, month)
        for day_type in ("weekday", "weekend")
        for weather in common_weather.index
    ]
    reports_dir = output_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.joinpath("travel_recommendations.json").write_text(
        json.dumps(results, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    markdown = [
        "# Model-Based Travel-Timing Recommendations",
        "",
        f"Recommendations use the trained traffic-volume model with June ({month}) conditions and median weather measurements for each observed weather class.",
        "",
        "| Day type | Weather | Historical weather rows | Recommended two-hour window | Mean predicted traffic/hour |",
        "|---|---|---:|---|---:|",
    ]
    for result in results:
        for window in result["windows"]:
            markdown.append(
                f"| {result['day_type']} | {result['weather']} | {result['weather_history_records']} | "
                f"{window['window']} | {window['mean_predicted_traffic']:.0f} |"
            )
    markdown.extend(
        [
            "",
            "These are model estimates, not real-time traffic forecasts. The model reflects the 2012-2018 corridor history, the chosen month, typical observed weather values, and a non-holiday assumption. Verify current conditions before travel.",
            "",
        ]
    )
    reports_dir.joinpath("travel_recommendations.md").write_text("\n".join(markdown), encoding="utf-8")
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Engineered traffic history CSV")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL, help="Trained traffic-volume model")
    parser.add_argument("--day-type", choices=("weekday", "weekend"), help="Day group to recommend")
    parser.add_argument("--weather", help="Observed weather category, e.g. Clear or Rain")
    parser.add_argument("--month", type=int, default=6, help="Representative month (1-12)")
    parser.add_argument("--top", type=int, default=3, help="Number of non-overlapping windows to return")
    parser.add_argument("--report", action="store_true", help="Generate batch recommendations for common weather")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT, help="Machine-learning output folder")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    try:
        history = pd.read_csv(args.input)
        model = joblib.load(args.model)
        if args.report:
            recommendations = generate_recommendation_report(model, history, args.output_dir, args.month)
            LOGGER.info("Saved recommendations for %d day-type/weather combinations", len(recommendations))
        else:
            if not args.day_type or not args.weather:
                parser.error("--day-type and --weather are required unless --report is used")
            result = recommend_for_conditions(model, history, args.day_type, args.weather, args.month, top_n=args.top)
            print(f"Low-traffic windows for {result['day_type']} / {result['weather']} in month {result['month']}:")
            for window in result["windows"]:
                print(f"  {window['window']}: estimated {window['mean_predicted_traffic']:.0f} vehicles/hour")
            print(f"Weather profile based on {result['weather_history_records']} historical records.")
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        LOGGER.error("Travel recommendation failed: %s", exc, exc_info=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())