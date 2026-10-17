"""Detect unusual traffic/weather conditions with a chronological Isolation Forest."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


LOGGER = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "python_pipeline" / "data" / "processed" / "traffic_features.csv"
DEFAULT_OUTPUT = Path(__file__).resolve().parent
ANOMALY_FEATURES = (
    "traffic_volume",
    "hour_sin",
    "hour_cos",
    "day_of_week_sin",
    "day_of_week_cos",
    "is_weekend",
    "holiday_flag",
    "temp_scaled",
    "rain_1h_scaled",
    "snow_1h_scaled",
    "clouds_all_scaled",
    "is_adverse_weather",
    "is_low_visibility",
)


def chronological_anomaly_split(
    data: pd.DataFrame, test_fraction: float = 0.2
) -> tuple[pd.DataFrame, pd.DataFrame]:
    required = {"date_time", *ANOMALY_FEATURES, "weather_main", "congestion_category"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError("Input is missing required columns: " + ", ".join(sorted(missing)))
    if not 0 < test_fraction < 1:
        raise ValueError("test_fraction must be between 0 and 1")
    ordered = data.copy()
    ordered["date_time"] = pd.to_datetime(ordered["date_time"], errors="coerce")
    if ordered["date_time"].isna().any():
        raise ValueError("Input contains invalid date_time values")
    ordered = ordered.sort_values("date_time", kind="stable").reset_index(drop=True)
    split_index = int(len(ordered) * (1 - test_fraction))
    if split_index < 10 or len(ordered) - split_index < 2:
        raise ValueError("At least 12 rows are required for chronological anomaly scoring")
    return ordered.iloc[:split_index].copy(), ordered.iloc[split_index:].copy()


def _validate_contamination(contamination: float) -> None:
    if not 0 < contamination <= 0.5:
        raise ValueError("contamination must be in (0, 0.5]")


def detect_anomalies(
    data: pd.DataFrame, output_dir: Path, test_fraction: float = 0.2, contamination: float = 0.02
) -> dict[str, object]:
    _validate_contamination(contamination)
    training, testing = chronological_anomaly_split(data, test_fraction)
    model = Pipeline(
        [
            ("scale", StandardScaler()),
            (
                "isolation_forest",
                IsolationForest(
                    n_estimators=200,
                    contamination=contamination,
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ]
    )
    LOGGER.info("Fitting Isolation Forest on %d chronological training rows", len(training))
    model.fit(training.loc[:, ANOMALY_FEATURES])
    scores = -model.decision_function(testing.loc[:, ANOMALY_FEATURES])
    predictions = model.predict(testing.loc[:, ANOMALY_FEATURES])
    scored = testing.loc[:, ["date_time", "traffic_volume", "hour", "weather_main", "congestion_category"]].copy()
    scored["anomaly_score"] = scores
    scored["is_anomaly"] = predictions == -1
    scored = scored.sort_values("anomaly_score", ascending=False).reset_index(drop=True)

    weekly = (
        scored.assign(week=scored["date_time"].dt.to_period("W").astype(str))
        .groupby("week", as_index=False)
        .agg(records=("is_anomaly", "size"), anomalies=("is_anomaly", "sum"), anomaly_rate=("is_anomaly", "mean"))
    )
    top_rows = scored.head(25)
    result: dict[str, object] = {
        "dataset": "python_pipeline/data/processed/traffic_features.csv",
        "technique": "Isolation Forest",
        "rationale": "Identify traffic/weather feature combinations that differ from the earlier historical baseline without requiring accident labels.",
        "split": {
            "strategy": "chronological",
            "train_rows": int(len(training)),
            "test_rows": int(len(testing)),
            "training_end": training["date_time"].max().isoformat(),
            "test_start": testing["date_time"].min().isoformat(),
        },
        "configuration": {"contamination": contamination, "n_estimators": 200, "random_state": 42},
        "holdout": {
            "anomaly_count": int(scored["is_anomaly"].sum()),
            "anomaly_rate": float(scored["is_anomaly"].mean()),
            "weekly_rates": [
                {
                    "week": str(row.week),
                    "records": int(row.records),
                    "anomalies": int(row.anomalies),
                    "anomaly_rate": float(row.anomaly_rate),
                }
                for row in weekly.itertuples(index=False)
            ],
            "most_anomalous_records": [
                {
                    "date_time": row.date_time.isoformat(),
                    "traffic_volume": int(row.traffic_volume),
                    "hour": int(row.hour),
                    "weather_main": str(row.weather_main),
                    "congestion_category": str(row.congestion_category),
                    "anomaly_score": float(row.anomaly_score),
                }
                for row in top_rows.itertuples(index=False)
            ],
        },
        "limitations": [
            "No accident or incident ground-truth labels are available; an anomaly is not an accident prediction.",
            "The model is trained on an earlier period, so a high holdout anomaly rate may reflect seasonality, concept drift, or data-quality changes.",
            "The 2% contamination setting is a modeling assumption, not a measured incident prevalence.",
        ],
    }

    models_dir = output_dir / "models"
    reports_dir = output_dir / "reports"
    models_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, models_dir / "traffic_condition_isolation_forest.joblib")
    scored.to_csv(reports_dir / "anomaly_scores.csv", index=False)
    (reports_dir / "anomaly_monitoring.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    markdown = [
        "# Traffic Anomaly Detection",
        "",
        "## Method",
        "",
        "Isolation Forest was fit on the first 80% of the time-ordered data and applied to the latest 20%. The contamination value of 0.02 is an explicit modeling assumption.",
        "",
        "## Holdout Result",
        "",
        f"- Records scored: {len(scored)}",
        f"- Anomalies: {int(scored['is_anomaly'].sum())} ({scored['is_anomaly'].mean():.1%})",
        f"- Training period ends: {training['date_time'].max().isoformat(sep=' ')}",
        f"- Holdout period begins: {testing['date_time'].min().isoformat(sep=' ')}",
        "",
        "The highest-scoring observations are in `anomaly_scores.csv`; weekly flag rates are in `anomaly_monitoring.json`.",
        "",
        "## Value and Limitations",
        "",
        "This unsupervised score can prioritize unusual records for data-quality or operations review without requiring labels. It does not identify accidents. A shift from the earlier period can also reflect seasonality, concept drift, or sensor changes, and the configured contamination is not an observed event rate.",
        "",
    ]
    reports_dir.joinpath("anomaly_detection.md").write_text("\n".join(markdown), encoding="utf-8")
    LOGGER.info("Flagged %d of %d holdout rows", int(scored["is_anomaly"].sum()), len(scored))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Engineered traffic feature CSV")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT, help="Machine-learning output folder")
    parser.add_argument("--test-fraction", type=float, default=0.2, help="Latest fraction reserved for scoring")
    parser.add_argument("--contamination", type=float, default=0.02, help="Assumed training anomaly fraction")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    try:
        result = detect_anomalies(pd.read_csv(args.input), args.output_dir, args.test_fraction, args.contamination)
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        LOGGER.error("Anomaly detection failed: %s", exc, exc_info=True)
        return 1
    LOGGER.info("Holdout anomaly rate: %.3f", result["holdout"]["anomaly_rate"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())