"""Train supervised traffic and proxy-risk models on a chronological split."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


LOGGER = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "python_pipeline" / "data" / "processed" / "traffic_features.csv"
DEFAULT_OUTPUT = Path(__file__).resolve().parent
NUMERIC_FEATURES = (
    "hour",
    "day_of_week",
    "is_weekend",
    "holiday_flag",
    "month",
    "temp",
    "rain_1h",
    "snow_1h",
    "clouds_all",
)
CATEGORICAL_FEATURES = ("weather_main",)
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
LOW_VISIBILITY_WEATHER = {"Dust", "Fog", "Haze", "Mist", "Sand", "Smoke"}


def chronological_split(
    data: pd.DataFrame, test_fraction: float = 0.2
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, float]]:
    """Sort by time, split, then calculate congestion cutoffs on training rows only."""
    required = {
        "date_time",
        "traffic_volume",
        "weather_main",
        *(column for column in NUMERIC_FEATURES if column != "month"),
    }
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
    if split_index < 4 or len(ordered) - split_index < 2:
        raise ValueError("At least 6 rows are required for a chronological train/test split")

    training = ordered.iloc[:split_index].copy()
    testing = ordered.iloc[split_index:].copy()
    q1, q2, q3 = training["traffic_volume"].quantile([0.25, 0.5, 0.75]).to_numpy()
    thresholds = {"q1": float(q1), "q2": float(q2), "q3": float(q3)}
    return training, testing, thresholds


def add_proxy_targets(data: pd.DataFrame, thresholds: dict[str, float]) -> pd.DataFrame:
    """Add train-threshold congestion bands and an explicitly non-accident proxy."""
    result = data.copy()
    traffic = pd.to_numeric(result["traffic_volume"], errors="coerce")
    if traffic.isna().any():
        raise ValueError("traffic_volume must contain numeric values")
    result["congestion_category"] = np.select(
        [traffic.le(thresholds["q1"]), traffic.le(thresholds["q2"]), traffic.le(thresholds["q3"])],
        ["Low", "Medium", "High"],
        default="Severe",
    )
    weather = result["weather_main"].fillna("Unknown").astype(str).str.strip().str.title()
    adverse_or_low_visibility = weather.isin(ADVERSE_WEATHER | LOW_VISIBILITY_WEATHER)
    upper_half_congestion = result["congestion_category"].isin({"High", "Severe"})
    result["high_risk_proxy"] = (upper_half_congestion & adverse_or_low_visibility).astype("int8")
    return result


def _model_features(data: pd.DataFrame) -> pd.DataFrame:
    source_numeric = [column for column in NUMERIC_FEATURES if column != "month"]
    features = data.loc[:, [*source_numeric, *CATEGORICAL_FEATURES]].copy()
    features["month"] = pd.to_datetime(data["date_time"]).dt.month
    features["weather_main"] = features["weather_main"].fillna("Unknown").astype(str)
    return features


def _build_pipeline(estimator: object) -> Pipeline:
    numeric = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    preprocessing = ColumnTransformer(
        [("numeric", numeric, NUMERIC_FEATURES), ("categorical", categorical, CATEGORICAL_FEATURES)],
        verbose_feature_names_out=False,
    )
    return Pipeline([("preprocess", preprocessing), ("model", estimator)])


def _classification_metrics(model: Pipeline, features: pd.DataFrame, target: pd.Series) -> dict[str, float | None]:
    predictions = model.predict(features)
    probabilities = model.predict_proba(features)[:, 1]
    auc = roc_auc_score(target, probabilities) if target.nunique() == 2 else None
    return {
        "accuracy": float(accuracy_score(target, predictions)),
        "precision": float(precision_score(target, predictions, zero_division=0)),
        "recall": float(recall_score(target, predictions, zero_division=0)),
        "f1": float(f1_score(target, predictions, zero_division=0)),
        "roc_auc": float(auc) if auc is not None else None,
    }


def _regression_metrics(model: Pipeline, features: pd.DataFrame, target: pd.Series) -> dict[str, float]:
    predictions = model.predict(features)
    return {
        "mae": float(mean_absolute_error(target, predictions)),
        "rmse": float(np.sqrt(mean_squared_error(target, predictions))),
        "r2": float(r2_score(target, predictions)),
    }


def train_and_evaluate(data: pd.DataFrame, output_dir: Path, test_fraction: float = 0.2) -> dict[str, object]:
    training, testing, thresholds = chronological_split(data, test_fraction)
    training = add_proxy_targets(training, thresholds)
    testing = add_proxy_targets(testing, thresholds)
    if training["high_risk_proxy"].nunique() < 2:
        raise ValueError("Training period must contain both classes for high_risk_proxy")

    training_features = _model_features(training)
    testing_features = _model_features(testing)
    classification_train = training["high_risk_proxy"]
    classification_test = testing["high_risk_proxy"]
    traffic_train = training["traffic_volume"]
    traffic_test = testing["traffic_volume"]

    classifiers = {
        "logistic_regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "random_forest": RandomForestClassifier(
            n_estimators=120,
            min_samples_leaf=3,
            class_weight="balanced_subsample",
            random_state=42,
            n_jobs=-1,
        ),
    }
    regressors = {
        "random_forest": RandomForestRegressor(
            n_estimators=120,
            min_samples_leaf=3,
            random_state=42,
            n_jobs=-1,
        ),
        "hist_gradient_boosting": HistGradientBoostingRegressor(
            max_iter=120,
            l2_regularization=1.0,
            random_state=42,
        ),
    }

    classifier_results: dict[str, dict[str, float | None]] = {}
    fitted_classifiers: dict[str, Pipeline] = {}
    for name, estimator in classifiers.items():
        model = _build_pipeline(estimator)
        LOGGER.info("Training %s classifier", name)
        model.fit(training_features, classification_train)
        fitted_classifiers[name] = model
        classifier_results[name] = _classification_metrics(model, testing_features, classification_test)

    regressor_results: dict[str, dict[str, float]] = {}
    fitted_regressors: dict[str, Pipeline] = {}
    for name, estimator in regressors.items():
        model = _build_pipeline(estimator)
        LOGGER.info("Training %s regressor", name)
        model.fit(training_features, traffic_train)
        fitted_regressors[name] = model
        regressor_results[name] = _regression_metrics(model, testing_features, traffic_test)

    best_classifier = max(classifier_results, key=lambda name: classifier_results[name]["f1"] or 0.0)
    best_regressor = min(regressor_results, key=lambda name: regressor_results[name]["rmse"])
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "models").mkdir(parents=True, exist_ok=True)
    joblib.dump(fitted_classifiers[best_classifier], output_dir / "models" / "traffic_risk_classifier.joblib")
    joblib.dump(fitted_regressors[best_regressor], output_dir / "models" / "traffic_volume_regressor.joblib")

    result: dict[str, object] = {
        "dataset": "python_pipeline/data/processed/traffic_features.csv",
        "split": {
            "strategy": "chronological",
            "train_rows": int(len(training)),
            "test_rows": int(len(testing)),
            "test_start": testing["date_time"].min().isoformat(),
            "test_end": testing["date_time"].max().isoformat(),
            "congestion_thresholds_from_training": thresholds,
        },
        "proxy_label": (
            "high_risk_proxy = training-threshold upper-half congestion (High/Severe) "
            "AND adverse or low-visibility observed weather; not an accident label."
        ),
        "classification": {
            "target": "high_risk_proxy",
            "positive_test_rows": int(classification_test.sum()),
            "models": classifier_results,
            "selected_model": best_classifier,
        },
        "regression": {
            "target": "traffic_volume",
            "models": regressor_results,
            "selected_model": best_regressor,
        },
    }
    metrics_path = output_dir / "reports" / "supervised_metrics.json"
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    LOGGER.info("Saved metrics to %s", metrics_path)
    LOGGER.info("Selected classifier=%s and regressor=%s", best_classifier, best_regressor)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Engineered traffic feature CSV")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT, help="Machine-learning output folder")
    parser.add_argument("--test-fraction", type=float, default=0.2, help="Latest fraction reserved for testing")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    try:
        dataset = pd.read_csv(args.input)
        results = train_and_evaluate(dataset, args.output_dir, args.test_fraction)
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        LOGGER.error("Supervised training failed: %s", exc, exc_info=True)
        return 1

    LOGGER.info("Classification metrics: %s", results["classification"]["models"])
    LOGGER.info("Regression metrics: %s", results["regression"]["models"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())