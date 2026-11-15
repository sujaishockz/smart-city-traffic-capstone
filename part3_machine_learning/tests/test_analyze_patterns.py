"""Focused tests for discretized association-rule inputs."""

import unittest
import tempfile
from pathlib import Path

import pandas as pd

from part3_machine_learning.analyze_patterns import analyze_patterns, discretize_conditions, encode_transactions


class PatternPreparationTests(unittest.TestCase):
    def setUp(self):
        self.data = pd.DataFrame(
            {
                "hour": [7, 12, 20, 2],
                "is_weekend": [0, 1, 0, 1],
                "weather_main": ["Rain", "Clouds", "Clear", "Fog"],
                "congestion_category": ["Severe", "Low", "High", "Medium"],
            }
        )

    def test_conditions_map_to_readable_bins(self):
        categories = discretize_conditions(self.data)

        self.assertEqual(categories["hour_band"].tolist(), ["morning_peak", "midday", "late_evening", "overnight"])
        self.assertEqual(categories["day_type"].tolist(), ["weekday", "weekend", "weekday", "weekend"])
        self.assertEqual(categories["weather_category"].tolist(), ["adverse", "cloudy", "clear", "adverse"])

    def test_transactions_are_boolean_named_items(self):
        transactions = encode_transactions(self.data)

        self.assertIn("hour_band_morning_peak", transactions.columns)
        self.assertIn("weather_category_adverse", transactions.columns)
        self.assertTrue(all(dtype == bool for dtype in transactions.dtypes))
        self.assertTrue(bool(transactions.iloc[0]["congestion_category_Severe"]))

    def test_analysis_reports_silhouette_for_sampled_clusters(self):
        rows = []
        for index in range(12):
            group = index // 6
            rows.append(
                {
                    "date_time": f"2017-01-{index + 1:02d} 08:00:00",
                    "hour": 8 + group,
                    "is_weekend": group,
                    "weather_main": "Clear" if group == 0 else "Rain",
                    "congestion_category": "Low" if group == 0 else "High",
                    "traffic_volume": 100 + group * 1000 + index,
                    "hour_sin": float(group * 10 + index / 100),
                    "hour_cos": float(group * 10 + index / 100),
                    "day_of_week_sin": float(group * 10 + index / 100),
                    "day_of_week_cos": float(group * 10 + index / 100),
                    "holiday_flag": group,
                    "temp_scaled": float(group + index / 100),
                    "rain_1h_scaled": float(group + index / 100),
                    "snow_1h_scaled": float(group + index / 100),
                    "clouds_all_scaled": float(group + index / 100),
                }
            )
        dataset = pd.DataFrame(rows)

        with tempfile.TemporaryDirectory() as temporary_directory:
            result = analyze_patterns(
                dataset,
                Path(temporary_directory),
                n_clusters=2,
                min_support=0.1,
                min_lift=1.0,
                max_rules=5,
            )

        clustering = result["clustering"]
        self.assertGreaterEqual(clustering["silhouette_score"], -1.0)
        self.assertLessEqual(clustering["silhouette_score"], 1.0)
        self.assertEqual(clustering["silhouette_sample_rows"], len(dataset))


if __name__ == "__main__":
    unittest.main()