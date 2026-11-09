"""Calculate descriptive statistics and temperature/traffic correlation."""

import csv
import math
import statistics
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "Metro_Interstate_Traffic_Volume.csv"


def load_values() -> tuple[list[float], list[float]]:
    traffic: list[float] = []
    temperatures: list[float] = []
    with CSV_PATH.open("r", encoding="utf-8", newline="") as csv_file:
        for row in csv.DictReader(csv_file):
            traffic.append(float(row["traffic_volume"]))
            temperatures.append(float(row["temp"]))
    return traffic, temperatures


def pearson_correlation(first: list[float], second: list[float]) -> float:
    first_mean = statistics.mean(first)
    second_mean = statistics.mean(second)
    numerator = sum(
        (first_value - first_mean) * (second_value - second_mean)
        for first_value, second_value in zip(first, second)
    )
    first_sum = sum((value - first_mean) ** 2 for value in first)
    second_sum = sum((value - second_mean) ** 2 for value in second)
    return numerator / math.sqrt(first_sum * second_sum)


def main() -> None:
    traffic, temperatures = load_values()
    print("Traffic volume statistics")
    print(f"Count: {len(traffic)}")
    print(f"Mean: {statistics.mean(traffic):.2f}")
    print(f"Median: {statistics.median(traffic):.2f}")
    print(f"Standard deviation: {statistics.stdev(traffic):.2f}")
    print(f"Variance: {statistics.variance(traffic):.2f}")
    print(f"Range: {min(traffic):.2f} to {max(traffic):.2f} ({max(traffic) - min(traffic):.2f})")
    print()
    print("Temperature and traffic correlation")
    print(f"Pearson correlation: {pearson_correlation(temperatures, traffic):.4f}")


if __name__ == "__main__":
    main()
