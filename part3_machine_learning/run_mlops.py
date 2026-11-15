"""Track model performance and versions in a local MLflow experiment."""

from __future__ import annotations

import json
import hashlib
import logging
from pathlib import Path

import mlflow
import mlflow.sklearn
import sklearn
import joblib
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from mlflow.models import infer_signature

if __package__:
    from .train_supervised import _build_pipeline, _model_features, _regression_metrics, chronological_split
else:
    from train_supervised import _build_pipeline, _model_features, _regression_metrics, chronological_split


LOGGER = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "reports"
MODELS = ROOT / "models"
MLRUNS = ROOT / "mlruns"
MODEL_VERSION = "1.0.0"
CANDIDATE_MODEL_VERSION = "1.1.0"
CANDIDATE_MAX_ITER = 160
CANDIDATE_ARTIFACT = "traffic_volume_regressor_v1_1_0_candidate.joblib"


def _read_json(name: str) -> dict[str, object]:
    return json.loads((REPORTS / name).read_text(encoding="utf-8"))


def _model_catalog(candidate_metrics: dict[str, float]) -> dict[str, object]:
    supervised = _read_json("supervised_metrics.json")
    patterns = _read_json("pattern_analysis.json")
    neural = _read_json("neural_explainability.json")
    anomalies = _read_json("anomaly_monitoring.json")
    regression = supervised["regression"]
    classification = supervised["classification"]
    selected_regressor = regression["selected_model"]
    selected_classifier = classification["selected_model"]
    models = [
        {
            "name": "traffic_volume_regressor",
            "version": MODEL_VERSION,
            "artifact": "part3_machine_learning/models/traffic_volume_regressor.joblib",
            "algorithm": selected_regressor,
            "metrics": regression["models"][selected_regressor],
        },
        {
            "name": "traffic_risk_proxy_classifier",
            "version": MODEL_VERSION,
            "artifact": "part3_machine_learning/models/traffic_risk_classifier.joblib",
            "algorithm": selected_classifier,
            "metrics": classification["models"][selected_classifier],
        },
        {
            "name": "traffic_risk_neural_network",
            "version": MODEL_VERSION,
            "artifact": "part3_machine_learning/models/traffic_risk_neural_network.joblib",
            "algorithm": neural["model"]["algorithm"],
            "metrics": neural["model"]["metrics"],
        },
        {
            "name": "traffic_condition_kmeans",
            "version": MODEL_VERSION,
            "artifact": "part3_machine_learning/models/traffic_condition_kmeans.joblib",
            "algorithm": patterns["clustering"]["algorithm"],
            "metrics": {
                "clusters": patterns["clustering"]["clusters"],
                "inertia": patterns["clustering"]["inertia"],
            },
        },
        {
            "name": "traffic_condition_isolation_forest",
            "version": MODEL_VERSION,
            "artifact": "part3_machine_learning/models/traffic_condition_isolation_forest.joblib",
            "algorithm": anomalies["technique"],
            "metrics": {
                "holdout_anomaly_rate": anomalies["holdout"]["anomaly_rate"],
                "holdout_anomaly_count": anomalies["holdout"]["anomaly_count"],
            },
        },
    ]
    for model_entry in models:
        artifact_path = ROOT.parent / model_entry["artifact"]
        model_entry["artifact_sha256"] = hashlib.sha256(artifact_path.read_bytes()).hexdigest()

    regressor_versions = [
        {
            "name": "traffic_volume_regressor",
            "version": MODEL_VERSION,
            "status": "active",
            "artifact": "part3_machine_learning/models/traffic_volume_regressor.joblib",
            "algorithm": selected_regressor,
            "parameters": {"max_iter": 120, "l2_regularization": 1.0, "random_state": 42},
            "metrics": regression["models"][selected_regressor],
        },
        {
            "name": "traffic_volume_regressor",
            "version": CANDIDATE_MODEL_VERSION,
            "status": "candidate_not_promoted",
            "artifact": f"part3_machine_learning/models/{CANDIDATE_ARTIFACT}",
            "algorithm": "hist_gradient_boosting",
            "parameters": {
                "max_iter": CANDIDATE_MAX_ITER,
                "l2_regularization": 1.0,
                "random_state": 42,
            },
            "metrics": candidate_metrics,
        },
    ]
    for version in regressor_versions:
        artifact_path = ROOT.parent / version["artifact"]
        version["artifact_sha256"] = hashlib.sha256(artifact_path.read_bytes()).hexdigest()

    return {
        "schema_version": "1.0",
        "sklearn_version": sklearn.__version__,
        "versioning": {
            "scheme": "semantic version string",
            "active_traffic_regressor_version": MODEL_VERSION,
            "candidate_traffic_regressor_version": CANDIDATE_MODEL_VERSION,
            "candidate_status": "not promoted; evaluated on the same chronological holdout and requires independent validation",
            "policy": "Create a new version for a changed model artifact after evaluation; do not treat a repeated MLflow run as a new model version.",
        },
        "models": models,
        "traffic_volume_regressor_versions": regressor_versions,
    }


def _train_candidate_regressor(data: pd.DataFrame) -> tuple[object, dict[str, float]]:
    training, testing, _ = chronological_split(data)
    training_features = _model_features(training)
    testing_features = _model_features(testing)
    candidate = _build_pipeline(
        HistGradientBoostingRegressor(
            max_iter=CANDIDATE_MAX_ITER,
            l2_regularization=1.0,
            random_state=42,
        )
    )
    candidate.fit(training_features, training["traffic_volume"])
    metrics = _regression_metrics(candidate, testing_features, testing["traffic_volume"])
    return candidate, metrics


def run_mlflow_experiment() -> dict[str, object]:
    if not (MODELS / "traffic_volume_regressor.joblib").exists():
        raise FileNotFoundError("Run Task 1 before logging the traffic-volume model")
    metrics_report = _read_json("supervised_metrics.json")
    selected = metrics_report["regression"]["selected_model"]
    metrics = metrics_report["regression"]["models"][selected]
    model = joblib.load(MODELS / "traffic_volume_regressor.joblib")
    dataset = pd.read_csv(ROOT.parent / "part2_python" / "data" / "processed" / "traffic_features.csv")
    candidate, candidate_metrics = _train_candidate_regressor(dataset)
    candidate_path = MODELS / CANDIDATE_ARTIFACT
    joblib.dump(candidate, candidate_path)
    sample = pd.read_csv(ROOT.parent / "part2_python" / "data" / "processed" / "traffic_features.csv", nrows=5)
    sample["date_time"] = pd.to_datetime(sample["date_time"])
    model_input = sample.loc[
        :,
        [
            "hour",
            "day_of_week",
            "is_weekend",
            "holiday_flag",
            "temp",
            "rain_1h",
            "snow_1h",
            "clouds_all",
            "weather_main",
        ],
    ].copy()
    model_input["month"] = sample["date_time"].dt.month
    model_input = model_input[
        [
            "hour",
            "day_of_week",
            "is_weekend",
            "holiday_flag",
            "month",
            "temp",
            "rain_1h",
            "snow_1h",
            "clouds_all",
            "weather_main",
        ]
    ]
    numeric_inputs = [column for column in model_input.columns if column != "weather_main"]
    model_input[numeric_inputs] = model_input[numeric_inputs].astype(float)
    signature = infer_signature(model_input, model.predict(model_input))
    candidate_signature = infer_signature(model_input, candidate.predict(model_input))
    MLRUNS.mkdir(parents=True, exist_ok=True)
    mlflow.set_tracking_uri(MLRUNS.as_uri())
    mlflow.set_experiment("traffic-volume-regression")
    with mlflow.start_run(run_name=f"{selected}-v{MODEL_VERSION}") as run:
        mlflow.set_tag("model_name", "traffic_volume_regressor")
        mlflow.set_tag("model_version", MODEL_VERSION)
        mlflow.set_tag("evaluation_split", "chronological-80-20")
        mlflow.log_params(
            {
                "algorithm": selected,
                "model_version": MODEL_VERSION,
                "train_rows": metrics_report["split"]["train_rows"],
                "test_rows": metrics_report["split"]["test_rows"],
                "random_state": 42,
            }
        )
        mlflow.log_metrics({name: float(value) for name, value in metrics.items()})
        mlflow.sklearn.log_model(
            model,
            artifact_path="traffic-volume-regressor",
            signature=signature,
            input_example=model_input,
        )
        active_run_id = run.info.run_id
    with mlflow.start_run(run_name=f"{selected}-v{CANDIDATE_MODEL_VERSION}-candidate") as candidate_run:
        mlflow.set_tag("model_name", "traffic_volume_regressor")
        mlflow.set_tag("model_version", CANDIDATE_MODEL_VERSION)
        mlflow.set_tag("release_status", "candidate_not_promoted")
        mlflow.set_tag("evaluation_split", "chronological-80-20-shared-holdout")
        mlflow.log_params(
            {
                "algorithm": "hist_gradient_boosting",
                "model_version": CANDIDATE_MODEL_VERSION,
                "max_iter": CANDIDATE_MAX_ITER,
                "l2_regularization": 1.0,
                "random_state": 42,
            }
        )
        mlflow.log_metrics({name: float(value) for name, value in candidate_metrics.items()})
        mlflow.sklearn.log_model(
            candidate,
            artifact_path="traffic-volume-regressor-v1-1-0-candidate",
            signature=candidate_signature,
            input_example=model_input,
        )
        evidence = {
            "experiment_name": "traffic-volume-regression",
            "run_id": active_run_id,
            "model_name": "traffic_volume_regressor",
            "model_version": MODEL_VERSION,
            "algorithm": selected,
            "metrics": metrics,
            "tracking_store": "part3_machine_learning/mlruns/",
            "run_artifact_path": "traffic-volume-regressor/",
            "candidate": {
                "run_id": candidate_run.info.run_id,
                "model_version": CANDIDATE_MODEL_VERSION,
                "algorithm": "hist_gradient_boosting",
                "status": "candidate_not_promoted",
                "parameters": {
                    "max_iter": CANDIDATE_MAX_ITER,
                    "l2_regularization": 1.0,
                    "random_state": 42,
                },
                "metrics": candidate_metrics,
                "artifact": f"part3_machine_learning/models/{CANDIDATE_ARTIFACT}",
            },
        }
    REPORTS.joinpath("mlflow_evidence.json").write_text(
        json.dumps(evidence, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    catalog = _model_catalog(candidate_metrics)
    REPORTS.joinpath("model_versions.json").write_text(
        json.dumps(catalog, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    LOGGER.info(
        "Logged active run %s and candidate run %s; catalogued %d model families and %d regressor versions",
        evidence["run_id"],
        evidence["candidate"]["run_id"],
        len(catalog["models"]),
        len(catalog["traffic_volume_regressor_versions"]),
    )
    return evidence


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    try:
        run_mlflow_experiment()
    except (OSError, ValueError, mlflow.exceptions.MlflowException) as exc:
        LOGGER.error("MLflow tracking failed: %s", exc, exc_info=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())