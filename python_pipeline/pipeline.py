"""Load, validate, and clean the Metro Interstate Traffic Volume dataset."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Iterable

import pandas as pd


LOGGER = logging.getLogger(__name__)
PIPELINE_DIR = Path(__file__).resolve().parent
REPOSITORY_DIR = PIPELINE_DIR.parent
DEFAULT_INPUT = (
    REPOSITORY_DIR
    / "data_analytics"
    / "data"
    / "Metro_Interstate_Traffic_Volume.csv"
)
DEFAULT_OUTPUT = PIPELINE_DIR / "data" / "processed" / "traffic_cleaned.csv"
LOG_PATH = PIPELINE_DIR / "logs" / "pipeline.log"

EXPECTED_COLUMNS = {
    "holiday",
    "temp",
    "rain_1h",
    "snow_1h",
    "clouds_all",
    "weather_main",
    "weather_description",
    "date_time",
    "traffic_volume",
}
NUMERIC_COLUMNS = (
    "temp",
    "rain_1h",
    "snow_1h",
    "clouds_all",
    "traffic_volume",
)
MONTHLY_IMPUTE_COLUMNS = ("temp", "rain_1h", "snow_1h", "clouds_all")


def configure_logging(level: int = logging.INFO) -> None:
    """Configure console and file handlers for an executable entry point."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler(LOG_PATH, mode="w")],
        force=True,
    )


def _log_change(step: str, count: int, reason: str) -> None:
    if count:
        LOGGER.warning("%s affected %d rows: %s", step, count, reason)
    else:
        LOGGER.info("%s completed; no rows affected", step)


def load_raw_data(input_path: Path) -> pd.DataFrame:
    """Read the CSV and validate its schema before any data transformations."""
    try:
        data = pd.read_csv(input_path)
    except (OSError, UnicodeError, pd.errors.ParserError) as exc:
        raise ValueError(f"Unable to read CSV file {input_path}: {exc}") from exc

    missing_columns = EXPECTED_COLUMNS.difference(data.columns)
    if missing_columns:
        raise ValueError(
            "CSV schema is missing expected columns: "
            + ", ".join(sorted(missing_columns))
        )

    LOGGER.info(
        "Loaded raw CSV %s with %d rows and %d columns",
        input_path,
        len(data),
        len(data.columns),
    )
    LOGGER.info("Validated raw CSV schema: all %d required columns are present", len(EXPECTED_COLUMNS))
    return data


def _standardize_categories(data: pd.DataFrame) -> pd.DataFrame:
    cleaned = data.copy()
    changed_rows = pd.Series(False, index=cleaned.index)

    for column in ("holiday", "weather_main", "weather_description"):
        original = cleaned[column].copy()
        normalized = original.astype("string").str.strip()
        if column == "weather_main":
            normalized = normalized.str.title()
        elif column == "weather_description":
            normalized = normalized.str.lower()
        else:
            normalized = normalized.str.title()
            no_holiday = normalized.isna() | normalized.str.casefold().isin(
                {"", "none", "no holiday", "nan"}
            )
            normalized = normalized.mask(no_holiday, "None")

        changed_rows |= original.astype("string").fillna("<NA>") != normalized.fillna("<NA>")
        cleaned[column] = normalized.astype("object")

    _log_change(
        "Categorical standardization",
        int(changed_rows.sum()),
        "trimmed whitespace, normalized weather labels, and restored the no-holiday sentinel",
    )
    return cleaned


def _parse_and_validate_datetime(data: pd.DataFrame) -> pd.DataFrame:
    cleaned = data.copy()
    cleaned["date_time"] = pd.to_datetime(cleaned["date_time"], errors="coerce")
    invalid = cleaned["date_time"].isna()
    _log_change(
        "Datetime parsing",
        int(invalid.sum()),
        "removed rows with missing or invalid date_time values",
    )
    return cleaned.loc[~invalid].copy()


def _convert_numeric_columns(data: pd.DataFrame) -> pd.DataFrame:
    cleaned = data.copy()
    for column in NUMERIC_COLUMNS:
        original = cleaned[column].copy()
        converted = pd.to_numeric(original, errors="coerce")
        invalid = converted.isna() & original.notna()
        _log_change(
            f"Numeric parsing for {column}",
            int(invalid.sum()),
            "converted non-numeric values to missing values for subsequent validation",
        )
        cleaned[column] = converted
    return cleaned


def _remove_exact_duplicates(data: pd.DataFrame) -> pd.DataFrame:
    duplicate_rows = data.duplicated(keep="first")
    _log_change(
        "Exact duplicate removal",
        int(duplicate_rows.sum()),
        "removed only rows identical across every source column; repeated timestamps with different observations were retained",
    )
    return data.loc[~duplicate_rows].copy()


def _impute_monthly_medians(data: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    cleaned = data.copy()
    months = cleaned["date_time"].dt.month

    for column in columns:
        missing = cleaned[column].isna()
        affected = int(missing.sum())
        if affected:
            global_median = cleaned[column].median()
            for month in range(1, 13):
                month_mask = missing & months.eq(month)
                if not month_mask.any():
                    continue
                month_values = cleaned.loc[(months == month) & cleaned[column].notna(), column]
                median = month_values.median() if not month_values.empty else global_median
                if pd.isna(median):
                    raise ValueError(f"Cannot impute {column}: no valid values are available")
                cleaned.loc[month_mask, column] = median

        _log_change(
            f"Monthly median imputation for {column}",
            affected,
            "filled missing or physically impossible sensor values using that calendar month's median, with a global median fallback",
        )

    return cleaned


def _clean_numeric_values(data: pd.DataFrame) -> pd.DataFrame:
    cleaned = data.copy()
    invalid_rules = {
        "temp": cleaned["temp"] <= 0,
        "rain_1h": (cleaned["rain_1h"] < 0) | (cleaned["rain_1h"] > 9000),
        "snow_1h": cleaned["snow_1h"] < 0,
        "clouds_all": ~cleaned["clouds_all"].between(0, 100),
    }
    for column, invalid in invalid_rules.items():
        count = int(invalid.sum())
        cleaned.loc[invalid, column] = pd.NA
        _log_change(
            f"Physical-range validation for {column}",
            count,
            "marked physically impossible sensor readings for monthly median imputation",
        )

    invalid_target = cleaned["traffic_volume"].isna() | (cleaned["traffic_volume"] < 0)
    dropped_targets = int(invalid_target.sum())
    cleaned = cleaned.loc[~invalid_target].copy()
    _log_change(
        "Traffic target validation",
        dropped_targets,
        "removed rows with missing or negative traffic_volume because the target cannot be safely imputed",
    )

    return _impute_monthly_medians(cleaned, MONTHLY_IMPUTE_COLUMNS)


def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    """Apply documented cleaning steps while retaining non-identical timestamps."""
    cleaned = _standardize_categories(data)
    cleaned = _parse_and_validate_datetime(cleaned)
    cleaned = _convert_numeric_columns(cleaned)
    cleaned = _remove_exact_duplicates(cleaned)
    cleaned = _clean_numeric_values(cleaned)

    LOGGER.info("Cleaned dataset contains %d rows and %d columns", len(cleaned), len(cleaned.columns))
    return cleaned


def run_pipeline(input_path: Path = DEFAULT_INPUT, output_path: Path = DEFAULT_OUTPUT) -> Path:
    """Run the end-to-end CSV cleaning pipeline and return its output path."""
    raw_data = load_raw_data(Path(input_path))
    cleaned_data = clean_data(raw_data)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned_data.to_csv(output_path, index=False, date_format="%Y-%m-%d %H:%M:%S")
    LOGGER.info("Saved cleaned dataset to %s", output_path)
    return output_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Path to the raw traffic CSV")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Path for the cleaned CSV")
    parser.add_argument("--debug", action="store_true", help="Enable DEBUG-level logging")
    args = parser.parse_args(argv)

    configure_logging(logging.DEBUG if args.debug else logging.INFO)
    try:
        run_pipeline(args.input, args.output)
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        LOGGER.error("Pipeline failed: %s", exc, exc_info=True)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())