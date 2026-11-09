"""Calculate congestion, weather, temperature, independence, and odds metrics."""

import csv
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "Metro_Interstate_Traffic_Volume.csv"
CONGESTION_THRESHOLD = 5500
HIGH_TEMPERATURE_THRESHOLD = 292


def load_rows() -> list[dict[str, str]]:
    with CSV_PATH.open("r", encoding="utf-8", newline="") as csv_file:
        return list(csv.DictReader(csv_file))


def probability(count: int, total: int) -> float:
    return count / total


def main() -> None:
    rows = load_rows()
    total = len(rows)
    congestion = [int(row["traffic_volume"]) > CONGESTION_THRESHOLD for row in rows]
    clear = [row["weather_main"].strip().casefold() == "clear" for row in rows]
    high_temperature = [float(row["temp"]) > HIGH_TEMPERATURE_THRESHOLD for row in rows]

    congestion_count = sum(congestion)
    clear_count = sum(clear)
    intersection_count = sum(is_congested and is_clear for is_congested, is_clear in zip(congestion, clear))
    high_temperature_and_congestion = sum(
        is_congested and is_high_temperature
        for is_congested, is_high_temperature in zip(congestion, high_temperature)
    )

    clear_congestion = sum(
        is_congested and is_clear for is_congested, is_clear in zip(congestion, clear)
    )
    clear_non_congestion = sum(
        not is_congested and is_clear for is_congested, is_clear in zip(congestion, clear)
    )
    cloudy = [row["weather_main"].strip().casefold() == "clouds" for row in rows]
    cloudy_congestion = sum(
        is_congested and is_cloudy for is_congested, is_cloudy in zip(congestion, cloudy)
    )
    cloudy_non_congestion = sum(
        not is_congested and is_cloudy for is_congested, is_cloudy in zip(congestion, cloudy)
    )

    clear_odds = clear_congestion / clear_non_congestion
    cloudy_odds = cloudy_congestion / cloudy_non_congestion
    odds_ratio = clear_odds / cloudy_odds
    p_congestion = probability(congestion_count, total)
    p_clear = probability(clear_count, total)
    p_intersection = probability(intersection_count, total)

    print(f"Rows analysed: {total}")
    print(f"P(Congestion): {p_congestion:.4f}")
    print(f"P(Clear Weather): {p_clear:.4f}")
    print(f"P(Congestion AND Clear Weather): {p_intersection:.4f}")
    print(f"P(Clear Weather | Congestion): {intersection_count / congestion_count:.4f}")
    print(f"P(High Temperature | Congestion): {high_temperature_and_congestion / congestion_count:.4f}")
    expected_intersection = p_congestion * p_clear
    print(f"P(Congestion) * P(Clear Weather): {expected_intersection:.4f}")
    print(f"Independence difference: {p_intersection - expected_intersection:.4f}")
    print(f"Clear-weather congestion odds: {clear_odds:.4f}")
    print(f"Cloudy-weather congestion odds: {cloudy_odds:.4f}")
    print(f"Clear-to-cloudy congestion odds ratio: {odds_ratio:.4f}")


if __name__ == "__main__":
    main()