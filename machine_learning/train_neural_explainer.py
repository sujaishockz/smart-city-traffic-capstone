"""Train a neural network for the traffic-risk proxy and explain it with LIME."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from lime.lime_tabular import LimeTabularExplainer
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

if __package__:
    from .train_supervised import (
        CATEGORICAL_FEATURES,
        DEFAULT_INPUT,
        NUMERIC_FEATURES,
        add_proxy_targets,
        chronological_split,
        _model_features,
    )
else:
    from train_supervised import (
        CATEGORICAL_FEATURES,
        DEFAULT_INPUT,
        NUMERIC_FEATURES,
        add_proxy_targets,
        chronological_split,
        _model_features,
    )


LOGGER = logging.getLogger(__name__)
DEFAULT_OUTPUT = Path(__file__).resolve().parent


def build_neural_model() -> Pipeline:
    numeric = Pipeline(
        [("imputer", SimpleImputer(strategy="median"))]
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
    network = MLPClassifier(
        hidden_layer_sizes=(64, 32),
        activation="relu",
        solver="adam",
        alpha=0.001,
        batch_size=256,
        learning_rate_init=0.001,
        max_iter=200,
        early_stopping=True,
        validation_fraction=0.1,
        n_iter_no_change=15,
        random_state=42,
    )
    return Pipeline(
        [("preprocess", preprocessing), ("scale", StandardScaler()), ("network", network)]
    )


def _explanation_indices(target: pd.Series, per_class: int = 5) -> list[int]:
    positive = np.flatnonzero(target.to_numpy() == 1)[:per_class].tolist()
    negative = np.flatnonzero(target.to_numpy() == 0)[:per_class].tolist()
    if not positive or not negative:
        raise ValueError("The holdout must contain positive and negative proxy-label examples")
    return positive + negative


def train_and_explain(data: pd.DataFrame, output_dir: Path, test_fraction: float = 0.2) -> dict[str, object]:
    training, testing, thresholds = chronological_split(data, test_fraction)
    training = add_proxy_targets(training, thresholds)
    testing = add_proxy_targets(testing, thresholds)
    training_features = _model_features(training)
    testing_features = _model_features(testing)
    training_target = training["high_risk_proxy"]
    testing_target = testing["high_risk_proxy"]
    if training_target.nunique() < 2 or testing_target.nunique() < 2:
        raise ValueError("Both train and test periods must contain both proxy-label classes")

    model = build_neural_model()
    LOGGER.info("Training MLP classifier with %d training records", len(training))
    model.fit(training_features, training_target)
    probabilities = model.predict_proba(testing_features)[:, 1]
    predictions = model.predict(testing_features)
    metrics = {
        "accuracy": float(accuracy_score(testing_target, predictions)),
        "precision": float(precision_score(testing_target, predictions, zero_division=0)),
        "recall": float(recall_score(testing_target, predictions, zero_division=0)),
        "f1": float(f1_score(testing_target, predictions, zero_division=0)),
        "roc_auc": float(roc_auc_score(testing_target, probabilities)),
    }

    transformed_training = model.named_steps["preprocess"].transform(training_features)
    transformed_testing = model.named_steps["preprocess"].transform(testing_features)
    feature_names = model.named_steps["preprocess"].get_feature_names_out().tolist()

    def predict_from_lime_features(values: np.ndarray) -> np.ndarray:
        scaled_values = model.named_steps["scale"].transform(values)
        return model.named_steps["network"].predict_proba(scaled_values)

    explainer = LimeTabularExplainer(
        training_data=transformed_training,
        feature_names=feature_names,
        class_names=["not_high_risk_proxy", "high_risk_proxy"],
        mode="classification",
        discretize_continuous=True,
        random_state=42,
    )
    explanation_rows = []
    for test_index in _explanation_indices(testing_target):
        explanation = explainer.explain_instance(
            transformed_testing[test_index],
            predict_from_lime_features,
            labels=(1,),
            num_features=min(10, transformed_training.shape[1]),
            num_samples=500,
        )
        explanation_rows.append(
            {
                "test_index": int(test_index),
                "date_time": pd.Timestamp(testing.iloc[test_index]["date_time"]).isoformat(),
                "actual_proxy_label": int(testing_target.iloc[test_index]),
                "predicted_proxy_probability": float(probabilities[test_index]),
                "local_explanation": [
                    {"feature_condition": str(feature), "weight": float(weight)}
                    for feature, weight in explanation.as_list(label=1)
                ],
            }
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    models_dir = output_dir / "models"
    reports_dir = output_dir / "reports"
    models_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, models_dir / "traffic_risk_neural_network.joblib")
    result: dict[str, object] = {
        "dataset": "python_pipeline/data/processed/traffic_features.csv",
        "model": {
            "algorithm": "MLPClassifier",
            "hidden_layer_sizes": [64, 32],
            "iterations": int(model.named_steps["network"].n_iter_),
            "train_rows": int(len(training)),
            "test_rows": int(len(testing)),
            "test_start": testing["date_time"].min().isoformat(),
            "test_end": testing["date_time"].max().isoformat(),
            "congestion_thresholds_from_training": thresholds,
            "metrics": metrics,
        },
        "explainability": {
            "method": "LIME Tabular",
            "instances_explained": len(explanation_rows),
            "local_explanations": explanation_rows,
            "interpretation_limit": (
                "LIME approximates this model locally; explanations are not causal and refer only to the constructed proxy label."
            ),
        },
        "proxy_label": (
            "high_risk_proxy = training-threshold upper-half congestion (High/Severe) "
            "AND adverse or low-visibility observed weather; not an accident label."
        ),
    }
    reports_dir.joinpath("neural_explainability.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    markdown = [
        "# Neural Network and LIME Analysis",
        "",
        "The MLPClassifier uses hidden layers of 64 and 32 units. Its target is the constructed `high_risk_proxy`, not observed accidents.",
        "",
        "## Chronological Holdout Metrics",
        "",
        "| Accuracy | Precision | Recall | F1 | ROC-AUC |",
        "|---:|---:|---:|---:|---:|",
        f"| {metrics['accuracy']:.3f} | {metrics['precision']:.3f} | {metrics['recall']:.3f} | {metrics['f1']:.3f} | {metrics['roc_auc']:.3f} |",
        "",
        "## Local Explanations",
        "",
        "LIME weights below approximate the model around selected holdout examples. Positive weights increase support for the high-risk proxy class; negative weights decrease it.",
        "",
    ]
    for row in explanation_rows:
        markdown.append(
            f"### {row['date_time']} (actual proxy={row['actual_proxy_label']}, "
            f"predicted probability={row['predicted_proxy_probability']:.3f})"
        )
        markdown.extend(
            f"- `{item['feature_condition']}`: {item['weight']:+.3f}"
            for item in row["local_explanation"]
        )
        markdown.append("")
    markdown.extend(
        [
            "LIME is a local surrogate rather than a causal explanation. Since observed weather is part of the proxy-label definition, weather-related weights partly explain label construction. This is not evidence about real accident risk.",
            "",
        ]
    )
    reports_dir.joinpath("neural_explainability.md").write_text("\n".join(markdown), encoding="utf-8")
    LOGGER.info("Saved MLP model and %d LIME explanations", len(explanation_rows))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Engineered traffic feature CSV")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT, help="Machine-learning output folder")
    parser.add_argument("--test-fraction", type=float, default=0.2, help="Latest fraction reserved for testing")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    try:
        result = train_and_explain(pd.read_csv(args.input), args.output_dir, args.test_fraction)
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        LOGGER.error("Neural network training failed: %s", exc, exc_info=True)
        return 1
    LOGGER.info("MLP holdout metrics: %s", result["model"]["metrics"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())