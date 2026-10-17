"""Focused tests for supervised traffic targets and chronological splitting."""

import unittest

import pandas as pd

from machine_learning.train_supervised import add_proxy_targets, chronological_split


class SupervisedTargetTests(unittest.TestCase):
    def test_split_is_chronological_and_cutoffs_use_training_rows(self):
        data = pd.DataFrame(
            {
                "date_time": pd.date_range("2020-01-01", periods=10, freq="h").astype(str),
                "traffic_volume": list(range(1, 11)),
                "weather_main": ["Clear"] * 10,
                "hour": list(range(10)),
                "day_of_week": [0] * 10,
                "is_weekend": [0] * 10,
                "holiday_flag": [0] * 10,
                "temp": [280.0] * 10,
                "rain_1h": [0.0] * 10,
                "snow_1h": [0.0] * 10,
                "clouds_all": [0] * 10,
            }
        )
        data = data.iloc[::-1].reset_index(drop=True)

        training, testing, thresholds = chronological_split(data)

        self.assertEqual(len(training), 8)
        self.assertEqual(len(testing), 2)
        self.assertLess(training["date_time"].max(), testing["date_time"].min())
        self.assertEqual(thresholds["q2"], 4.5)

    def test_proxy_requires_upper_half_congestion_and_adverse_weather(self):
        data = pd.DataFrame(
            {
                "traffic_volume": [1, 2, 3, 4, 5, 6, 7, 8],
                "weather_main": ["Clear", "Fog", "Rain", "Clear", "Fog", "Clear", "Rain", "Clear"],
            }
        )

        labeled = add_proxy_targets(data, {"q1": 2.75, "q2": 4.5, "q3": 6.25})

        self.assertEqual(labeled["congestion_category"].tolist(), [
            "Low", "Low", "Medium", "Medium", "High", "High", "Severe", "Severe"
        ])
        self.assertEqual(labeled["high_risk_proxy"].tolist(), [0, 0, 0, 0, 1, 0, 1, 0])


if __name__ == "__main__":
    unittest.main()