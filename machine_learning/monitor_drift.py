"""Compare historical and recent feature distributions and simulate injected drift."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd


LOGGER = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "python_pipeline" / "data" / "processed" / "traffic_features.csv"
DEFAULT_OUTPUT = Path(__file__).resolve().parent
DRIFT_FEATURES = ("traffic_volume", "temp_scaled", "rain_1h_scaled", "clouds_all_scaled", "hour_sin")
PSI_THRESHOLD = 0.2


def population_stability_index(reference: pd.Series, current: pd.Series, bins: int = 10) -> float:
    reference_values = pd.to_numeric(reference, errors="coerce").dropna().to_numpy()
    current_values = pd.to_numeric(current, errors="coerce").dropna().to_numpy()
    if len(reference_values) == 0 or len(current_values) == 0 or bins < 2:
        raise ValueError("PSI requires non-empty numeric samples and at least two bins")
    edges = np.unique(np.quantile(reference_values, np.linspace(0, 1, bins + 1)))
    if len(edges) < 2:
        return 0.0
    edges[0] = -np.inf
    edges[-1] = np.inf
    reference_counts = np.histogram(reference_values, bins=edges)[0].astype(float)
    current_counts = np.histogram(current_values, bins=edges)[0].astype(float)
    reference_share = (reference_counts + 0.5) / (reference_counts.sum() + 0.5 * len(reference_counts))
    current_share = (current_counts + 0.5) / (current_counts.sum() + 0.5 * len(current_counts))
    return float(np.sum((current_share - reference_share) * np.log(current_share / reference_share)))


def evaluate_drift(
    reference: pd.DataFrame, current: pd.DataFrame, features: tuple[str, ...] = DRIFT_FEATURES
) -> dict[str, object]:
    missing = set(features).difference(reference.columns).union(set(features).difference(current.columns))
    if missing:
        raise ValueError("Drift inputs are missing features: " + ", ".join(sorted(missing)))
    psi_by_feature = {
        feature: population_stability_index(reference[feature], current[feature]) for feature in features
    }
    status = "ALERT/Requires investigation" if any(value >= PSI_THRESHOLD for value in psi_by_feature.values()) else "PASS/Normal"
    return {"status": status, "psi_threshold": PSI_THRESHOLD, "features": psi_by_feature}


def monitor_drift(data: pd.DataFrame, output_dir: Path, test_fraction: float = 0.2) -> dict[str, object]:
    required = {"date_time", *DRIFT_FEATURES}
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
        raise ValueError("At least 12 rows are required for drift monitoring")
    reference = ordered.iloc[:split_index]
    recent = ordered.iloc[split_index:]
    observed = evaluate_drift(reference, recent)

    injected = recent.copy()
    injected["traffic_volume"] = injected["traffic_volume"] * 1.5
    simulated = evaluate_drift(reference, injected)
    result: dict[str, object] = {
        "method": "Population Stability Index (PSI)",
        "threshold": PSI_THRESHOLD,
        "split": {
            "baseline_rows": int(len(reference)),
            "recent_rows": int(len(recent)),
            "baseline_end": reference["date_time"].max().isoformat(),
            "recent_start": recent["date_time"].min().isoformat(),
        },
        "observed_holdout": observed,
        "controlled_shift_simulation": {
            "injected_change": "traffic_volume multiplied by 1.5 in the recent sample",
            **simulated,
        },
        "status": observed["status"],
        "interpretation": (
            "PASS/Normal means no monitored feature crossed the configured PSI threshold; "
            "ALERT/Requires investigation means at least one feature distribution changed materially."
        ),
        "limitations": [
            "PSI detects distribution change, not predictive error or operational impact.",
            "The threshold is a heuristic; alerts require human investigation and may reflect seasonality.",
            "The injected 50% traffic shift is a controlled test, not an observed event.",
        ],
    }
    reports_dir = output_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.joinpath("drift_monitoring.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    markdown = [
        "# Feature-Distribution Drift Monitoring",
        "",
        f"- PSI threshold: {PSI_THRESHOLD:.2f}",
        f"- Observed holdout status: **{observed['status']}**",
        f"- Controlled +50% traffic shift status: **{simulated['status']}**",
        "",
        "## Observed PSI by Feature",
        "",
        "| Feature | PSI | Status |",
        "|---|---:|---|",
    ]
    for feature, value in observed["features"].items():
        markdown.append(f"| {feature} | {value:.3f} | {'ALERT' if value >= PSI_THRESHOLD else 'PASS'} |")
    markdown.extend(
        [
            "",
            "The controlled scenario multiplies recent traffic volume by 1.5 to exercise the alert path. PSI is a distribution monitor, not a performance or incident metric; review alerts for seasonality and data-quality changes.",
            "",
        ]
    )
    reports_dir.joinpath("drift_monitoring.md").write_text("\n".join(markdown), encoding="utf-8")
    LOGGER.info("Observed drift status: %s; controlled shift status: %s", observed["status"], simulated["status"])
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Engineered traffic feature CSV")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT, help="Machine-learning output folder")
    parser.add_argument("--test-fraction", type=float, default=0.2, help="Latest fraction treated as recent data")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    try:
        result = monitor_drift(pd.read_csv(args.input), args.output_dir, args.test_fraction)
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        LOGGER.error("Drift monitoring failed: %s", exc, exc_info=True)
        return 1
    LOGGER.info("Drift monitoring status: %s", result["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())