"""Evaluate proxy-model subgroup behavior and generate responsible-AI reports."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.metrics import accuracy_score, f1_score, precision_score

if __package__:
    from .train_supervised import (
        ADVERSE_WEATHER,
        DEFAULT_INPUT,
        LOW_VISIBILITY_WEATHER,
        add_proxy_targets,
        chronological_split,
        _model_features,
    )
else:
    from train_supervised import (
        ADVERSE_WEATHER,
        DEFAULT_INPUT,
        LOW_VISIBILITY_WEATHER,
        add_proxy_targets,
        chronological_split,
        _model_features,
    )


LOGGER = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT = ROOT / "reports" / "bias_fairness"
MODEL_PATH = ROOT / "models" / "traffic_risk_classifier.joblib"


def subgroup_metrics(actual: pd.Series | np.ndarray, predicted: pd.Series | np.ndarray) -> dict[str, object]:
    actual_values = np.asarray(actual, dtype=int)
    predicted_values = np.asarray(predicted, dtype=int)
    true_positive = int(np.sum((actual_values == 1) & (predicted_values == 1)))
    false_positive = int(np.sum((actual_values == 0) & (predicted_values == 1)))
    false_negative = int(np.sum((actual_values == 1) & (predicted_values == 0)))
    true_negative = int(np.sum((actual_values == 0) & (predicted_values == 0)))
    actual_positive = true_positive + false_negative
    actual_negative = true_negative + false_positive
    return {
        "support": int(len(actual_values)),
        "actual_positive": actual_positive,
        "predicted_positive": int(np.sum(predicted_values == 1)),
        "actual_positive_rate": float(np.mean(actual_values == 1)) if len(actual_values) else None,
        "predicted_positive_rate": float(np.mean(predicted_values == 1)) if len(predicted_values) else None,
        "accuracy": float(accuracy_score(actual_values, predicted_values)) if len(actual_values) else None,
        "precision": float(precision_score(actual_values, predicted_values, zero_division=0)) if len(actual_values) else None,
        "recall_tpr": float(true_positive / actual_positive) if actual_positive else None,
        "false_positive_rate": float(false_positive / actual_negative) if actual_negative else None,
        "f1": float(f1_score(actual_values, predicted_values, zero_division=0)) if len(actual_values) else None,
    }


def _evaluate_axis(
    groups: pd.Series, actual: pd.Series, predicted: np.ndarray, minimum_group_size: int
) -> tuple[dict[str, dict[str, object]], list[dict[str, object]]]:
    metrics: dict[str, dict[str, object]] = {}
    excluded = []
    for group_name in sorted(groups.astype(str).unique()):
        mask = groups.astype(str).to_numpy() == group_name
        group_size = int(mask.sum())
        if group_size < minimum_group_size:
            excluded.append({"group": group_name, "support": group_size})
            continue
        metrics[group_name] = subgroup_metrics(actual.to_numpy()[mask], predicted[mask])
    return metrics, excluded


def _metric_gap(groups: dict[str, dict[str, object]], metric: str) -> float | None:
    values = [float(group[metric]) for group in groups.values() if group[metric] is not None]
    return max(values) - min(values) if len(values) > 1 else None


def _format_rate(value: object) -> str:
    return "n/a" if value is None else f"{float(value):.3f}"


def _write_fairness_report(result: dict[str, object], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "bias_fairness_metrics.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    lines = [
        "# Bias, Fairness, Governance, and Sustainability",
        "",
        "## Scope and Fairness Assessment",
        "",
        "The dataset has no demographic or legally protected-group attributes. The results below are operational subgroup diagnostics for day type, an adverse-weather grouping, and observed weather classes; they are not a formal demographic fairness audit.",
        "",
        f"The Random Forest was evaluated on a chronological holdout of {result['split']['test_rows']:,} rows. The constructed proxy-positive rate was {result['overall']['actual_positive_rate']:.1%}; the predicted-positive rate was {result['overall']['predicted_positive_rate']:.1%}.",
        "",
    ]
    for axis_name, groups in result["subgroups"].items():
        lines.extend(
            [
                f"### {axis_name.replace('_', ' ').title()}",
                "",
                "| Group | N | Actual positive rate | Predicted positive rate | TPR/recall | FPR | Precision | F1 |",
                "|---|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for group_name, metrics in groups.items():
            lines.append(
                f"| {group_name} | {metrics['support']} | {_format_rate(metrics['actual_positive_rate'])} | "
                f"{_format_rate(metrics['predicted_positive_rate'])} | {_format_rate(metrics['recall_tpr'])} | "
                f"{_format_rate(metrics['false_positive_rate'])} | {_format_rate(metrics['precision'])} | "
                f"{_format_rate(metrics['f1'])} |"
            )
        lines.append("")
    lines.extend(
        [
            "Day type and weather are context variables, not protected attributes. Weather is also part of the proxy-label definition, so performance differences by weather are partly induced by target construction. Small weather groups below the configured support threshold are listed in the JSON and excluded from rate comparison.",
            "",
            "The high proxy-model scores do not establish accident-prediction ability. Do not use this model for enforcement, individual risk scoring, or safety-critical decisions. Any future deployment requires an actual incident dataset, stakeholder review, calibration, and fairness testing on appropriate protected-group data collected and governed lawfully.",
            "",
            "## Governance Controls",
            "",
            "- Intended purpose: educational traffic-pattern analysis and travel-timing exploration on the studied I-94 corridor.",
            "- Data provenance: public Metro Interstate Traffic Volume records, 2012-2018; no person-level or incident-level records were provided.",
            "- Human oversight: treat recommendations and anomaly flags as review aids; verify current traffic and weather before acting.",
            "- Versioning: model artifacts use version 1.0.0 in the model catalog; evaluation data, parameters, metrics, and model signature are recorded in MLflow.",
            "- Change control: retrain only after data-quality checks and chronological evaluation; compare new subgroup metrics and drift status before replacing a model.",
            "- Privacy and security: this dataset contains no direct personal identifiers; keep credentials out of artifacts and restrict writable access to model/report directories in any deployed environment.",
            "",
            "## Sustainability",
            "",
            f"The saved model artifacts total {result['sustainability']['total_model_bytes']:,} bytes ({result['sustainability']['total_model_megabytes']:.2f} MB). Training and inference were run on CPU; the available AMD GPU was not used. Energy and carbon emissions were not measured, so no environmental impact estimate is claimed.",
            "",
            "For a project of roughly 48,000 rows, the compact scikit-learn models avoid a continuously hosted GPU and can be reused rather than retrained for every prediction. Future runs should record wall time, hardware, memory, and energy where available, and retrain only when monitoring or new validated data justifies it.",
            "",
            "## Limitations",
            "",
            "- One westbound corridor and historical data limit geographic and temporal representativeness.",
            "- Congestion and weather define the proxy target; there is no observed accident outcome or causal evidence.",
            "- No demographic attributes means protected-group fairness remains unmeasurable from the supplied data.",
            "- Weather/day-type subgroup differences are diagnostic only and should not be treated as evidence of discrimination or its absence.",
            "",
        ]
    )
    (output_dir / "bias_fairness_governance_sustainability.md").write_text("\n".join(lines), encoding="utf-8")


def analyze_responsible_ai(
    data: pd.DataFrame,
    model_path: Path = MODEL_PATH,
    output_dir: Path = DEFAULT_OUTPUT,
    minimum_group_size: int = 200,
) -> dict[str, object]:
    if minimum_group_size < 1:
        raise ValueError("minimum_group_size must be positive")
    training, testing, thresholds = chronological_split(data)
    training = add_proxy_targets(training, thresholds)
    testing = add_proxy_targets(testing, thresholds)
    if not model_path.exists():
        raise FileNotFoundError(f"Classifier model not found: {model_path}")
    classifier = joblib.load(model_path)
    predictions = classifier.predict(_model_features(testing)).astype(int)
    actual = testing["high_risk_proxy"].astype(int)
    overall = subgroup_metrics(actual, predictions)
    weather = testing["weather_main"].fillna("Unknown").astype(str).str.strip().str.title()
    adverse_weather = weather.isin(ADVERSE_WEATHER | LOW_VISIBILITY_WEATHER)
    axes = {
        "day_type": testing["is_weekend"].map({0: "weekday", 1: "weekend"}),
        "weather_risk": adverse_weather.map({True: "adverse_or_low_visibility", False: "other_weather"}),
        "weather_main": weather,
    }
    subgroups = {}
    excluded_small_groups = {}
    for axis_name, labels in axes.items():
        groups, excluded = _evaluate_axis(labels, actual, predictions, minimum_group_size)
        subgroups[axis_name] = groups
        excluded_small_groups[axis_name] = excluded
    performance_gaps = {
        axis_name: {
            "recall_tpr_gap": _metric_gap(groups, "recall_tpr"),
            "false_positive_rate_gap": _metric_gap(groups, "false_positive_rate"),
            "predicted_positive_rate_gap": _metric_gap(groups, "predicted_positive_rate"),
        }
        for axis_name, groups in subgroups.items()
    }
    artifact_names = [
        "traffic_volume_regressor.joblib",
        "traffic_risk_classifier.joblib",
        "traffic_risk_neural_network.joblib",
        "traffic_condition_kmeans.joblib",
        "traffic_condition_isolation_forest.joblib",
    ]
    model_sizes = {
        name: (ROOT / "models" / name).stat().st_size
        for name in artifact_names
        if (ROOT / "models" / name).exists()
    }
    total_model_bytes = sum(model_sizes.values())
    result: dict[str, object] = {
        "model": "traffic_risk_proxy_classifier",
        "model_version": "1.0.0",
        "evaluation": "chronological holdout; training-only congestion thresholds",
        "split": {
            "train_rows": int(len(training)),
            "test_rows": int(len(testing)),
            "test_start": testing["date_time"].min().isoformat(),
            "test_end": testing["date_time"].max().isoformat(),
            "congestion_thresholds_from_training": thresholds,
        },
        "overall": overall,
        "subgroups": subgroups,
        "excluded_small_groups": excluded_small_groups,
        "minimum_group_size": minimum_group_size,
        "performance_gaps": performance_gaps,
        "fairness_scope": {
            "demographic_attributes_available": False,
            "formal_protected_group_audit_possible": False,
            "operational_segments": list(axes),
            "target_is_constructed_proxy": True,
        },
        "sustainability": {
            "runtime": "CPU; GPU acceleration not used",
            "python_version": "3.9",
            "scikit_learn_version": sklearn.__version__,
            "model_artifact_sizes_bytes": model_sizes,
            "total_model_bytes": total_model_bytes,
            "total_model_megabytes": total_model_bytes / (1024 * 1024),
            "energy_or_carbon_measured": False,
        },
    }
    _write_fairness_report(result, output_dir)
    LOGGER.info("Wrote responsible-AI report for %d holdout records", len(testing))
    return result


def _write_final_report(responsible_ai: dict[str, object]) -> None:
    regression = json.loads((ROOT / "reports" / "supervised_metrics.json").read_text(encoding="utf-8"))
    patterns = json.loads((ROOT / "reports" / "pattern_analysis.json").read_text(encoding="utf-8"))
    neural = json.loads((ROOT / "reports" / "neural_explainability.json").read_text(encoding="utf-8"))
    anomaly = json.loads((ROOT / "reports" / "anomaly_monitoring.json").read_text(encoding="utf-8"))
    recommendations = json.loads((ROOT / "reports" / "travel_recommendations.json").read_text(encoding="utf-8"))
    drift = json.loads((ROOT / "reports" / "drift_monitoring.json").read_text(encoding="utf-8"))
    mlflow_evidence = json.loads((ROOT / "reports" / "mlflow_evidence.json").read_text(encoding="utf-8"))
    selected_regression = regression["regression"]["models"][regression["regression"]["selected_model"]]
    selected_classification = regression["classification"]["models"][regression["classification"]["selected_model"]]
    largest_cluster = max(patterns["clustering"]["profiles"], key=lambda profile: profile["records"])
    strongest_rule = patterns["association_rules"]["top_rules"][0]
    best_recommendation = next(
        result for result in recommendations if result["day_type"] == "weekend" and result["weather"] == "Clear"
    )
    first_window = best_recommendation["windows"][0]
    report = [
        "# Part 3 Final Report: Machine Learning and AI",
        "",
        "## Executive Summary",
        "",
        "Part 3 adds supervised models, descriptive clustering and association rules, a neural network with LIME explanations, Isolation Forest anomaly scoring, model-based travel timing, and an MLOps simulation to the Part 2 I-94 traffic pipeline. All modeling was run locally on CPU; no CUDA GPU was available or required.",
        "",
        "The results demonstrate a reproducible workflow on approximately 48,000 historical hourly observations. They do not demonstrate actual accident prediction: the risk target is a constructed proxy, and the dataset contains no accident outcomes.",
        "",
        "## Results by Task",
        "",
        "### Task 1: Supervised Models",
        "",
        f"A chronological 80/20 split used {regression['split']['train_rows']:,} training and {regression['split']['test_rows']:,} test rows. The best proxy classifier was Random Forest (F1 {selected_classification['f1']:.3f}, ROC-AUC {selected_classification['roc_auc']:.3f}). Histogram Gradient Boosting was the best traffic regressor (MAE {selected_regression['mae']:.1f}, RMSE {selected_regression['rmse']:.1f} vehicles/hour, R-squared {selected_regression['r2']:.3f}).",
        "",
        "The proxy is positive for upper-half congestion combined with adverse or low-visibility weather, using congestion thresholds calculated from training data. Since observed weather is part of the target rule, the classifier metrics must be read as performance on that proxy only.",
        "",
        "### Task 2: Unsupervised Patterns",
        "",
        f"K-means formed four condition clusters. The largest contains {largest_cluster['records']:,} observations ({largest_cluster['traffic_level']}; mean volume {largest_cluster['mean_traffic_volume']:.0f}). The strongest association rule has lift {strongest_rule['lift']:.2f} and support {strongest_rule['support']:.3f}. These are descriptive co-occurrences, not causal rules.",
        "",
        "### Task 3: Neural Network and Explainability",
        "",
        f"The MLP classifier reached F1 {neural['model']['metrics']['f1']:.3f} and ROC-AUC {neural['model']['metrics']['roc_auc']:.3f} on the same chronological proxy task. LIME explanations are local approximations; they do not provide causal explanations or real accident-risk drivers.",
        "",
        "### Task 4: Advanced Anomaly Detection",
        "",
        f"An Isolation Forest trained on the earlier period flagged {anomaly['holdout']['anomaly_count']:,} of {anomaly['split']['test_rows']:,} later-period records ({anomaly['holdout']['anomaly_rate']:.1%}) using a 2% contamination assumption. Flags indicate unusual feature combinations, not incidents.",
        "",
        "### Task 5: Travel Recommendations",
        "",
        f"The traffic regressor ranks two-hour windows by day type, month, and observed weather class. For a June weekend with Clear weather, the model's first choice is {first_window['window']} (estimated {first_window['mean_predicted_traffic']:.0f} vehicles/hour). This reflects typical historical weather measurements and is not a real-time forecast.",
        "",
        "### Task 6: MLOps",
        "",
        f"Five artifacts are catalogued at version 1.0.0. MLflow run `{mlflow_evidence['run_id']}` tracks the traffic regressor and its chronological holdout metrics. A FastAPI simulation serves the regression model. PSI monitoring reports **{drift['status']}** for the recent holdout; `clouds_all_scaled` PSI is {drift['observed_holdout']['features']['clouds_all_scaled']:.3f} against a 0.2 threshold. A controlled +50% traffic shift also exercises the ALERT path.",
        "",
        "### Task 7: Responsible AI",
        "",
        f"Subgroup diagnostics compare weekday/weekend and weather segments. There are no demographic attributes, so a formal protected-group fairness audit is not possible. Combined model artifact size is {responsible_ai['sustainability']['total_model_megabytes']:.2f} MB; training ran on CPU. Energy and carbon were not measured.",
        "",
        "## Limitations and Use Boundaries",
        "",
        "- The source covers one westbound I-94 corridor and the 2012-2018 period; external validity is limited.",
        "- No accident, incident, or demographic data were provided. Proxy classification, fairness, and safety claims must remain constrained accordingly.",
        "- Distribution drift is not predictive error. The observed PSI ALERT is driven by feature shifts and needs investigation; it does not establish model failure or traffic danger.",
        "- Recommendations use historical averages/medians, assume no holiday, and do not include live traffic feeds.",
        "- No energy or carbon measurements were available, so sustainability discussion is qualitative except for artifact sizes and CPU-only execution.",
        "",
        "## Reproduction",
        "",
        "Install pinned packages with `python -m pip install -r machine_learning/requirements.txt`, then run the scripts documented in `machine_learning/README.md`. Run tests with `python -m unittest discover -s machine_learning/tests -v`. For local serving, use `uvicorn machine_learning.deployment.app:app --host 127.0.0.1 --port 8000`.",
        "",
        "Supporting metrics, models, configurations, and reports are stored under `machine_learning/models/` and `machine_learning/reports/`; the local MLflow run store is ignored by Git, with its run ID retained in the evidence JSON.",
        "",
    ]
    (ROOT / "reports" / "part3_final_report.md").write_text("\n".join(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Engineered traffic dataset")
    parser.add_argument("--minimum-group-size", type=int, default=200, help="Smallest subgroup included in rate comparisons")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    try:
        result = analyze_responsible_ai(pd.read_csv(args.input), minimum_group_size=args.minimum_group_size)
        _write_final_report(result)
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        LOGGER.error("Responsible-AI analysis failed: %s", exc, exc_info=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())