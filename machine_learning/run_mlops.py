"""Track model performance and versions in a local MLflow experiment."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import mlflow
import mlflow.sklearn
import sklearn
import joblib
import pandas as pd
from mlflow.models import infer_signature


LOGGER = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "reports"
MODELS = ROOT / "models"
MLRUNS = ROOT / "mlruns"
MODEL_VERSION = "1.0.0"


def _read_json(name: str) -> dict[str, object]:
    return json.loads((REPORTS / name).read_text(encoding="utf-8"))


def _model_catalog() -> dict[str, object]:
    supervised = _read_json("supervised_metrics.json")
    patterns = _read_json("pattern_analysis.json")
    neural = _read_json("neural_explainability.json")
    anomalies = _read_json("anomaly_monitoring.json")
    regression = supervised["regression"]
    classification = supervised["classification"]
    selected_regressor = regression["selected_model"]
    selected_classifier = classification["selected_model"]
    return {
        "schema_version": "1.0",
        "sklearn_version": sklearn.__version__,
        "models": [
            {
                "name": "traffic_volume_regressor",
                "version": MODEL_VERSION,
                "artifact": "machine_learning/models/traffic_volume_regressor.joblib",
                "algorithm": selected_regressor,
                "metrics": regression["models"][selected_regressor],
            },
            {
                "name": "traffic_risk_proxy_classifier",
                "version": MODEL_VERSION,
                "artifact": "machine_learning/models/traffic_risk_classifier.joblib",
                "algorithm": selected_classifier,
                "metrics": classification["models"][selected_classifier],
            },
            {
                "name": "traffic_risk_neural_network",
                "version": MODEL_VERSION,
                "artifact": "machine_learning/models/traffic_risk_neural_network.joblib",
                "algorithm": neural["model"]["algorithm"],
                "metrics": neural["model"]["metrics"],
            },
            {
                "name": "traffic_condition_kmeans",
                "version": MODEL_VERSION,
                "artifact": "machine_learning/models/traffic_condition_kmeans.joblib",
                "algorithm": patterns["clustering"]["algorithm"],
                "metrics": {
                    "clusters": patterns["clustering"]["clusters"],
                    "inertia": patterns["clustering"]["inertia"],
                },
            },
            {
                "name": "traffic_condition_isolation_forest",
                "version": MODEL_VERSION,
                "artifact": "machine_learning/models/traffic_condition_isolation_forest.joblib",
                "algorithm": anomalies["technique"],
                "metrics": {
                    "holdout_anomaly_rate": anomalies["holdout"]["anomaly_rate"],
                    "holdout_anomaly_count": anomalies["holdout"]["anomaly_count"],
                },
            },
        ],
    }


def run_mlflow_experiment() -> dict[str, object]:
    if not (MODELS / "traffic_volume_regressor.joblib").exists():
        raise FileNotFoundError("Run Task 1 before logging the traffic-volume model")
    metrics_report = _read_json("supervised_metrics.json")
    selected = metrics_report["regression"]["selected_model"]
    metrics = metrics_report["regression"]["models"][selected]
    model = joblib.load(MODELS / "traffic_volume_regressor.joblib")
    sample = pd.read_csv(ROOT.parent / "python_pipeline" / "data" / "processed" / "traffic_features.csv", nrows=5)
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
        evidence = {
            "experiment_name": "traffic-volume-regression",
            "run_id": run.info.run_id,
            "model_name": "traffic_volume_regressor",
            "model_version": MODEL_VERSION,
            "algorithm": selected,
            "metrics": metrics,
            "tracking_store": "machine_learning/mlruns/",
            "run_artifact_path": "traffic-volume-regressor/",
        }
    REPORTS.joinpath("mlflow_evidence.json").write_text(
        json.dumps(evidence, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    catalog = _model_catalog()
    REPORTS.joinpath("model_versions.json").write_text(
        json.dumps(catalog, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    LOGGER.info("Logged MLflow run %s and catalogued %d model artifacts", evidence["run_id"], len(catalog["models"]))
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