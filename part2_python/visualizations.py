"""Generate and interpret traffic visualizations from engineered data."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from feature_engineering import FEATURE_OUTPUT
from pipeline import configure_logging


LOGGER = logging.getLogger(__name__)
PIPELINE_DIR = Path(__file__).resolve().parent
FIGURES_DIR = PIPELINE_DIR / "figures"
INTERPRETATION_PATH = PIPELINE_DIR / "reports" / "visualization_interpretations.md"
REQUIRED_COLUMNS = {"date_time", "traffic_volume", "temp", "weather_main"}


def _save_figure(figure: plt.Figure, path: Path, interpretation: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(figure)
    LOGGER.info("Saved figure to %s", path)
    return interpretation


def create_visualizations(data: pd.DataFrame, output_dir: Path = FIGURES_DIR) -> list[str]:
    """Save four traffic visualizations and return their interpretations."""
    missing_columns = REQUIRED_COLUMNS.difference(data.columns)
    if missing_columns:
        raise ValueError("Feature dataset is missing columns: " + ", ".join(sorted(missing_columns)))

    frame = data.copy()
    frame["date_time"] = pd.to_datetime(frame["date_time"], errors="coerce")
    frame["traffic_volume"] = pd.to_numeric(frame["traffic_volume"], errors="coerce")
    frame["temp"] = pd.to_numeric(frame["temp"], errors="coerce")
    frame = frame.dropna(subset=["date_time", "traffic_volume", "temp"])
    if frame.empty:
        raise ValueError("No valid traffic observations are available to plot")

    frame["hour"] = frame["date_time"].dt.hour
    frame["day_of_week"] = frame["date_time"].dt.dayofweek
    frame["day_type"] = np.where(frame["day_of_week"].ge(5), "Weekend", "Weekday")
    frame["temp_celsius"] = frame["temp"] - 273.15
    output_dir = Path(output_dir)
    interpretations: list[str] = []

    hourly = frame.groupby(["day_type", "hour"], observed=True)["traffic_volume"].mean().unstack("day_type")
    figure, axis = plt.subplots(figsize=(10, 5.5))
    for day_type in ("Weekday", "Weekend"):
        if day_type in hourly:
            axis.plot(hourly.index, hourly[day_type], marker="o", linewidth=2, label=day_type)
    axis.set(title="Average Traffic by Hour and Day Type", xlabel="Hour of day", ylabel="Vehicles per hour")
    axis.set_xticks(range(0, 24, 2))
    axis.grid(axis="y", alpha=0.25)
    axis.legend(frameon=False)
    weekday_peak = int(hourly["Weekday"].idxmax()) if "Weekday" in hourly else -1
    weekend_peak = int(hourly["Weekend"].idxmax()) if "Weekend" in hourly else -1
    interpretation = (
        f"Average weekday traffic peaks around {weekday_peak:02d}:00 ({hourly.loc[weekday_peak, 'Weekday']:.1f} "
        f"vehicles per hour), while weekend traffic peaks around {weekend_peak:02d}:00 "
        f"({hourly.loc[weekend_peak, 'Weekend']:.1f} vehicles per hour). The curves show how demand timing differs by day type."
    )
    interpretations.append(_save_figure(figure, output_dir / "traffic_by_hour_and_day_type.png", interpretation))

    weather_summary = (
        frame.groupby("weather_main", dropna=False)["traffic_volume"]
        .agg(["mean", "count"])
        .sort_values("mean")
    )
    figure, axis = plt.subplots(figsize=(10, max(5.5, 0.38 * len(weather_summary))))
    axis.barh(weather_summary.index.astype(str), weather_summary["mean"], color="#187C72")
    axis.set(title="Average Traffic by Weather Condition", xlabel="Average vehicles per hour", ylabel="Weather")
    axis.grid(axis="x", alpha=0.25)
    lowest_weather = str(weather_summary.index[0])
    highest_weather = str(weather_summary.index[-1])
    lowest_average = float(weather_summary["mean"].iloc[0])
    highest_average = float(weather_summary["mean"].iloc[-1])
    interpretations.append(
        _save_figure(
            figure,
            output_dir / "average_traffic_by_weather.png",
            f"{highest_weather} has the highest observed average traffic ({highest_average:.1f}) and "
            f"{lowest_weather} the lowest ({lowest_average:.1f}), a difference of "
            f"{highest_average - lowest_average:.1f} vehicles per hour. These means are based on "
            f"{int(weather_summary['count'].iloc[-1])} {highest_weather} and "
            f"{int(weather_summary['count'].iloc[0])} {lowest_weather} observations, respectively; "
            "the rare-category estimate should be interpreted cautiously.",
        )
    )

    scatter_data = frame.sample(n=min(10000, len(frame)), random_state=42)
    correlation = float(frame["temp_celsius"].corr(frame["traffic_volume"]))
    trend_x = np.linspace(float(scatter_data["temp_celsius"].min()), float(scatter_data["temp_celsius"].max()), 100)
    slope, intercept = np.polyfit(scatter_data["temp_celsius"], scatter_data["traffic_volume"], 1)
    figure, axis = plt.subplots(figsize=(9, 5.5))
    axis.scatter(scatter_data["temp_celsius"], scatter_data["traffic_volume"], s=10, alpha=0.22, color="#D46A3A")
    axis.plot(trend_x, slope * trend_x + intercept, color="#243B53", linewidth=2, label="Linear trend")
    axis.set(title="Temperature and Traffic Volume", xlabel="Temperature (°C)", ylabel="Vehicles per hour")
    axis.grid(alpha=0.2)
    axis.legend(frameon=False)
    interpretations.append(
        _save_figure(
            figure,
            output_dir / "temperature_vs_traffic.png",
            f"Temperature and traffic have a Pearson correlation of {correlation:.3f} in the cleaned observations. "
            "The scatter shows substantial variation at similar temperatures; this is association, not evidence that temperature causes traffic changes.",
        )
    )

    traffic_counts = frame["traffic_volume"].describe()
    figure, axis = plt.subplots(figsize=(9, 5.5))
    axis.hist(frame["traffic_volume"], bins=35, color="#315C8C", edgecolor="white")
    axis.axvline(traffic_counts["50%"], color="#D46A3A", linestyle="--", linewidth=2, label="Median")
    axis.set(title="Distribution of Hourly Traffic Volume", xlabel="Vehicles per hour", ylabel="Number of observations")
    axis.grid(axis="y", alpha=0.2)
    axis.legend(frameon=False)
    interpretations.append(
        _save_figure(
            figure,
            output_dir / "traffic_volume_distribution.png",
            f"Traffic volume ranges from {traffic_counts['min']:.0f} to {traffic_counts['max']:.0f} vehicles per hour; "
            f"the median is {traffic_counts['50%']:.0f}. The distribution includes both quiet overnight periods and busy commute periods.",
        )
    )

    return interpretations


def write_interpretations(interpretations: list[str], report_path: Path = INTERPRETATION_PATH) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Traffic Visualization Interpretations",
        "",
        "Figures are generated from the cleaned and engineered dataset. Weather averages are descriptive and can be affected by differences in time-of-day and day-type coverage.",
        "",
    ]
    for interpretation in interpretations:
        lines.extend([f"- {interpretation}", ""])
    report_path.write_text("\n".join(lines), encoding="utf-8")
    LOGGER.info("Saved visualization interpretations to %s", report_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=FEATURE_OUTPUT, help="Path to engineered traffic CSV")
    parser.add_argument("--output-dir", type=Path, default=FIGURES_DIR, help="Directory for saved figures")
    parser.add_argument("--report", type=Path, default=INTERPRETATION_PATH, help="Path for interpretation report")
    parser.add_argument("--debug", action="store_true", help="Enable DEBUG-level logging")
    args = parser.parse_args(argv)
    configure_logging(logging.DEBUG if args.debug else logging.INFO, append=True)

    try:
        data = pd.read_csv(args.input)
        interpretations = create_visualizations(data, args.output_dir)
        write_interpretations(interpretations, args.report)
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        LOGGER.error("Visualization generation failed: %s", exc, exc_info=True)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())