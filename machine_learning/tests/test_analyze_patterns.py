"""Focused tests for discretized association-rule inputs."""

import unittest

import pandas as pd

from machine_learning.analyze_patterns import discretize_conditions, encode_transactions


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


if __name__ == "__main__":
    unittest.main()