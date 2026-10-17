"""Query cleaned traffic data from the command line."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Sequence

import pandas as pd

PIPELINE_DIR = Path(__file__).resolve().parents[1]
REPOSITORY_DIR = PIPELINE_DIR.parent
DEFAULT_DATA = PIPELINE_DIR / "data" / "processed" / "traffic_features.csv"
LOG_PATH = PIPELINE_DIR / "logs" / "pipeline.log"
LOGGER = logging.getLogger(__name__)


class LoggingArgumentParser(argparse.ArgumentParser):
    """Report argument errors through logging instead of a traceback."""

    def error(self, message: str) -> None:
        LOGGER.error("Invalid command-line input: %s", message)
        raise ValueError(message)


def _build_parser() -> argparse.ArgumentParser:
    parser = LoggingArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA, help="Path to engineered traffic CSV")
    commands = parser.add_subparsers(dest="command", required=True, parser_class=LoggingArgumentParser)

    lookup = commands.add_parser("lookup", help="Look up traffic observations at an exact timestamp")
    lookup.add_argument("datetime", help="Timestamp in YYYY-MM-DD HH:MM:SS format")

    busiest = commands.add_parser("high-traffic", help="Show the highest traffic observations")
    busiest.add_argument("--limit", type=int, default=10, help="Number of observations to display")

    commands.add_parser("compare-days", help="Compare average traffic on weekdays and weekends")

    recommend = commands.add_parser("recommend", help="Recommend a low-traffic two-hour travel window")
    recommend.add_argument("--day-type", choices=("weekday", "weekend"), default="weekday")
    recommend.add_argument("--weather", help="Optional weather category, such as Clear or Rain")

    return parser


def _load_data(path: Path) -> pd.DataFrame:
    data = pd.read_csv(path)
    required = {"date_time", "traffic_volume", "weather_main", "holiday"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError("Traffic data is missing columns: " + ", ".join(sorted(missing)))

    data["date_time"] = pd.to_datetime(data["date_time"], errors="coerce")
    data["traffic_volume"] = pd.to_numeric(data["traffic_volume"], errors="coerce")
    invalid = data["date_time"].isna() | data["traffic_volume"].isna()
    if invalid.any():
        LOGGER.warning("Ignored %d rows with an invalid timestamp or traffic volume", int(invalid.sum()))
        data = data.loc[~invalid].copy()
    data["hour"] = data["date_time"].dt.hour
    data["day_type"] = data["date_time"].dt.dayofweek.map(
        lambda day: "weekend" if day >= 5 else "weekday"
    )
    if "congestion_category" not in data:
        quartiles = data["traffic_volume"].quantile([0.25, 0.5, 0.75]).to_numpy()
        data["congestion_category"] = pd.cut(
            data["traffic_volume"],
            bins=[-float("inf"), *quartiles, float("inf")],
            labels=["Low", "Medium", "High", "Severe"],
            include_lowest=True,
            duplicates="drop",
        ).astype("string")
    return data


def _format_table(data: pd.DataFrame, columns: Sequence[str]) -> str:
    available = [column for column in columns if column in data.columns]
    if data.empty:
        return "No matching traffic observations were found."
    return data[available].to_string(index=False)


def _lookup(data: pd.DataFrame, value: str) -> str:
    try:
        timestamp = pd.to_datetime(value, format="%Y-%m-%d %H:%M:%S", exact=True)
    except (TypeError, ValueError) as exc:
        raise ValueError("datetime must use YYYY-MM-DD HH:MM:SS, for example '2017-01-01 08:00:00'") from exc
    matches = data.loc[data["date_time"].eq(timestamp)].sort_values("traffic_volume", ascending=False)
    return _format_table(matches, ["date_time", "traffic_volume", "weather_main", "congestion_category"])


def _high_traffic(data: pd.DataFrame, limit: int) -> str:
    if limit < 1:
        raise ValueError("--limit must be a positive integer")
    busiest = data.nlargest(limit, "traffic_volume")
    return _format_table(busiest, ["date_time", "traffic_volume", "weather_main", "congestion_category"])


def _compare_days(data: pd.DataFrame) -> str:
    summary = data.groupby("day_type")["traffic_volume"].agg(["count", "mean", "median"])
    summary["mean"] = summary["mean"].round(1)
    summary["median"] = summary["median"].round(1)
    return summary.to_string()


def _recommend(data: pd.DataFrame, day_type: str, weather: str | None) -> str:
    subset = data.loc[data["day_type"].eq(day_type)].copy()
    weather_label = "any weather"
    if weather:
        matches = subset["weather_main"].astype("string").str.casefold().eq(weather.strip().casefold())
        subset = subset.loc[matches]
        weather_label = f"{weather.strip()} conditions"
    if subset.empty:
        raise ValueError(f"No observations found for {day_type}s under {weather_label}")

    hourly = subset.groupby("hour")["traffic_volume"].agg(["mean", "count"])
    eligible_starts = []
    for start_hour in range(23):
        if start_hour in hourly.index and (start_hour + 1) in hourly.index:
            if hourly.loc[start_hour, "count"] >= 5 and hourly.loc[start_hour + 1, "count"] >= 5:
                window_mean = (hourly.loc[start_hour, "mean"] + hourly.loc[start_hour + 1, "mean"]) / 2
                eligible_starts.append((float(window_mean), start_hour))
    if not eligible_starts:
        raise ValueError("Not enough observations to recommend a two-hour window for these filters")

    average_volume, start_hour = min(eligible_starts)
    end_hour = start_hour + 2
    return (
        f"For a {day_type} journey during {weather_label}, consider travelling between "
        f"{start_hour:02d}:00 and {end_hour:02d}:00. Historical average traffic across that "
        f"two-hour window is approximately {average_volume:.0f} vehicles per hour. "
        "This timing recommendation reflects one I-94 corridor and is not a route recommendation."
    )


def dispatch(args: argparse.Namespace, data: pd.DataFrame) -> str:
    if args.command == "lookup":
        return _lookup(data, args.datetime)
    if args.command == "high-traffic":
        return _high_traffic(data, args.limit)
    if args.command == "compare-days":
        return _compare_days(data)
    if args.command == "recommend":
        return _recommend(data, args.day_type, args.weather)
    raise ValueError(f"Unsupported command: {args.command}")


def main(argv: list[str] | None = None) -> int:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler(LOG_PATH, mode="w")],
        force=True,
    )
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
        LOGGER.info("CLI command=%s arguments=%s", args.command, vars(args))
        data = _load_data(args.data)
        result = dispatch(args, data)
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        LOGGER.error("Traffic analytics request failed: %s", exc)
        return 2
    print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())