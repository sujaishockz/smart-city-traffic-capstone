"""Focused tests for chronological anomaly scoring setup."""

import unittest

import pandas as pd

from machine_learning.detect_anomalies import ANOMALY_FEATURES, _validate_contamination, chronological_anomaly_split


class AnomalyDetectionTests(unittest.TestCase):
    def test_split_uses_earlier_rows_for_training(self):
        data = pd.DataFrame({"date_time": pd.date_range("2024-01-01", periods=20, freq="h").astype(str)})
        for column in ANOMALY_FEATURES:
            data[column] = 1.0
        data["weather_main"] = "Clear"
        data["congestion_category"] = "Low"

        training, testing = chronological_anomaly_split(data)

        self.assertEqual(len(training), 16)
        self.assertEqual(len(testing), 4)
        self.assertLess(training["date_time"].max(), testing["date_time"].min())

    def test_contamination_must_be_a_fraction_up_to_half(self):
        _validate_contamination(0.02)
        with self.assertRaises(ValueError):
            _validate_contamination(0.6)


if __name__ == "__main__":
    unittest.main()