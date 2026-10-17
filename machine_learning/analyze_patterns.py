"""Cluster traffic conditions and mine association rules from discretized data."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import joblib
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from sklearn.cluster import KMeans
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


LOGGER = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "python_pipeline" / "data" / "processed" / "traffic_features.csv"
DEFAULT_OUTPUT = Path(__file__).resolve().parent
CLUSTER_FEATURES = (
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
    "traffic_volume",
)
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


def discretize_conditions(data: pd.DataFrame) -> pd.DataFrame:
    """Create compact, interpretable transaction categories for rule mining."""
    required = {"hour", "is_weekend", "weather_main", "congestion_category"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError("Input is missing required columns: " + ", ".join(sorted(missing)))

    hour = pd.to_numeric(data["hour"], errors="coerce")
    if hour.isna().any() or not hour.between(0, 23).all():
        raise ValueError("hour must contain values from 0 through 23")
    weather = data["weather_main"].fillna("Unknown").astype(str).str.strip().str.title()
    weather_category = weather.map(
        lambda value: "adverse"
        if value in ADVERSE_WEATHER
        else "clear"
        if value == "Clear"
        else "cloudy"
        if value == "Clouds"
        else "other"
    )
    hour_band = pd.cut(
        hour,
        bins=[-1, 5, 9, 15, 19, 23],
        labels=["overnight", "morning_peak", "midday", "evening_peak", "late_evening"],
    ).astype("string")
    day_type = data["is_weekend"].astype(bool).map({True: "weekend", False: "weekday"})
    return pd.DataFrame(
        {
            "hour_band": hour_band,
            "day_type": day_type,
            "weather_category": weather_category,
            "congestion_category": data["congestion_category"].astype(str),
        },
        index=data.index,
    )


def encode_transactions(data: pd.DataFrame) -> pd.DataFrame:
    """Return one-hot transaction indicators with stable, named item columns."""
    categories = discretize_conditions(data)
    transactions = pd.get_dummies(categories, prefix=categories.columns, dtype=bool)
    return transactions


def _cluster_profiles(data: pd.DataFrame, labels: pd.Series) -> list[dict[str, object]]:
    grouped = data.assign(cluster=labels).groupby("cluster", sort=True)
    traffic_q1, traffic_q3 = data["traffic_volume"].quantile([0.25, 0.75]).to_numpy()
    profiles = []
    for cluster_id, rows in grouped:
        mean_volume = float(rows["traffic_volume"].mean())
        traffic_level = "low-volume" if mean_volume <= traffic_q1 else "high-volume" if mean_volume >= traffic_q3 else "moderate-volume"
        dominant_weather = str(rows["weather_main"].fillna("Unknown").mode().iloc[0])
        dominant_congestion = str(rows["congestion_category"].mode().iloc[0])
        mean_hour = float(rows["hour"].mean())
        weekend_share = float(rows["is_weekend"].mean())
        profiles.append(
            {
                "cluster": int(cluster_id),
                "records": int(len(rows)),
                "share": float(len(rows) / len(data)),
                "traffic_level": traffic_level,
                "mean_traffic_volume": mean_volume,
                "median_traffic_volume": float(rows["traffic_volume"].median()),
                "mean_hour": mean_hour,
                "weekend_share": weekend_share,
                "dominant_weather": dominant_weather,
                "dominant_congestion": dominant_congestion,
                "interpretation": (
                    f"{traffic_level} conditions centered near hour {mean_hour:.1f}, "
                    f"most often {dominant_congestion} congestion with {dominant_weather} weather."
                ),
            }
        )
    return profiles


def _mine_rules(
    transactions: pd.DataFrame, min_support: float, min_lift: float, max_rules: int
) -> list[dict[str, object]]:
    itemsets = apriori(transactions, min_support=min_support, use_colnames=True, max_len=3)
    if itemsets.empty or not itemsets["itemsets"].map(len).ge(2).any():
        return []
    rules = association_rules(itemsets, metric="lift", min_threshold=min_lift)
    if rules.empty:
        return []
    rules = rules.sort_values(["lift", "confidence", "support"], ascending=False).head(max_rules)
    return [
        {
            "antecedents": sorted(str(item) for item in row.antecedents),
            "consequents": sorted(str(item) for item in row.consequents),
            "support": float(row.support),
            "confidence": float(row.confidence),
            "lift": float(row.lift),
        }
        for row in rules.itertuples(index=False)
    ]


def analyze_patterns(
    data: pd.DataFrame,
    output_dir: Path,
    n_clusters: int = 4,
    min_support: float = 0.03,
    min_lift: float = 1.2,
    max_rules: int = 20,
) -> dict[str, object]:
    missing = set(CLUSTER_FEATURES).union(
        {"date_time", "traffic_volume", "hour", "is_weekend", "weather_main", "congestion_category"}
    ).difference(data.columns)
    if missing:
        raise ValueError("Input is missing required columns: " + ", ".join(sorted(missing)))
    if not 2 <= n_clusters < len(data):
        raise ValueError("n_clusters must be at least 2 and less than the number of rows")
    if not 0 < min_support <= 1 or min_lift < 1 or max_rules < 1:
        raise ValueError("min_support must be in (0, 1], min_lift at least 1, and max_rules positive")

    clusterer = Pipeline(
        [
            ("scale", StandardScaler()),
            ("kmeans", KMeans(n_clusters=n_clusters, n_init=10, random_state=42)),
        ]
    )
    LOGGER.info("Fitting K-means with %d clusters over %d rows", n_clusters, len(data))
    labels = pd.Series(clusterer.fit_predict(data.loc[:, CLUSTER_FEATURES]), index=data.index, name="cluster")
    profiles = _cluster_profiles(data, labels)
    transactions = encode_transactions(data)
    LOGGER.info("Mining association rules with support >= %.3f and lift >= %.2f", min_support, min_lift)
    rules = _mine_rules(transactions, min_support, min_lift, max_rules)

    output_dir.mkdir(parents=True, exist_ok=True)
    models_dir = output_dir / "models"
    reports_dir = output_dir / "reports"
    models_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(clusterer, models_dir / "traffic_condition_kmeans.joblib")
    pd.DataFrame({"date_time": data["date_time"], "cluster": labels}).to_csv(
        reports_dir / "cluster_assignments.csv", index=False
    )

    result: dict[str, object] = {
        "dataset": "python_pipeline/data/processed/traffic_features.csv",
        "clustering": {
            "algorithm": "KMeans",
            "clusters": n_clusters,
            "features": list(CLUSTER_FEATURES),
            "inertia": float(clusterer.named_steps["kmeans"].inertia_),
            "profiles": profiles,
        },
        "association_rules": {
            "transaction_fields": ["hour_band", "day_type", "weather_category", "congestion_category"],
            "minimum_support": min_support,
            "minimum_lift": min_lift,
            "rules_returned": len(rules),
            "top_rules": rules,
        },
        "limitations": [
            "Clusters are descriptive groups, not causal or predictive classes.",
            "Association rules describe co-occurrence in this single-corridor dataset and do not imply causality.",
            "The congestion categories were derived in the Part 2 feature pipeline from this dataset.",
        ],
    }
    report_path = reports_dir / "pattern_analysis.json"
    report_path.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    markdown = [
        "# Traffic Pattern Analysis",
        "",
        "## K-means Clusters",
        "",
        "| Cluster | Records | Traffic level | Mean volume | Mean hour | Weekend share | Dominant weather | Dominant congestion |",
        "|---:|---:|---|---:|---:|---:|---|---|",
    ]
    for profile in profiles:
        markdown.append(
            f"| {profile['cluster']} | {profile['records']} | {profile['traffic_level']} | "
            f"{profile['mean_traffic_volume']:.1f} | {profile['mean_hour']:.1f} | "
            f"{profile['weekend_share']:.1%} | {profile['dominant_weather']} | {profile['dominant_congestion']} |"
        )
        markdown.append(f"\n{profile['interpretation']}\n")
    markdown.extend(["## Highest-Lift Association Rules", ""])
    if rules:
        markdown.extend(
            [
                "| If these conditions occur | Then this condition occurs | Support | Confidence | Lift |",
                "|---|---|---:|---:|---:|",
            ]
        )
        for rule in rules:
            antecedent = " + ".join(rule["antecedents"])
            consequent = " + ".join(rule["consequents"])
            markdown.append(
                f"| {antecedent} | {consequent} | {rule['support']:.3f} | "
                f"{rule['confidence']:.3f} | {rule['lift']:.2f} |"
            )
    else:
        markdown.append("No rules met the configured support and lift thresholds.")
    markdown.extend(
        [
            "",
            "These clusters and rules are descriptive, not causal. The dataset covers one traffic corridor, and its congestion bands are dataset-derived.",
            "",
        ]
    )
    (reports_dir / "pattern_analysis.md").write_text("\n".join(markdown), encoding="utf-8")
    LOGGER.info("Saved %d association rules and %d cluster profiles", len(rules), len(profiles))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Engineered traffic feature CSV")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT, help="Machine-learning output folder")
    parser.add_argument("--clusters", type=int, default=4, help="Number of K-means clusters")
    parser.add_argument("--min-support", type=float, default=0.03, help="Minimum association-rule support")
    parser.add_argument("--min-lift", type=float, default=1.2, help="Minimum association-rule lift")
    parser.add_argument("--max-rules", type=int, default=20, help="Maximum rules included in the report")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    try:
        dataset = pd.read_csv(args.input)
        result = analyze_patterns(
            dataset, args.output_dir, args.clusters, args.min_support, args.min_lift, args.max_rules
        )
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        LOGGER.error("Pattern analysis failed: %s", exc, exc_info=True)
        return 1
    LOGGER.info(
        "K-means inertia=%.2f; high-lift rules=%d",
        result["clustering"]["inertia"],
        result["association_rules"]["rules_returned"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())