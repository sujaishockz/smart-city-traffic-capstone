"""Integration checks for the Part 2 cleaning-to-visualization workflow."""

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from part2_python.feature_engineering import engineer_features
from part2_python.pipeline import clean_data
from part2_python.visualizations import create_visualizations, write_interpretations


class AnalyticsIntegrationTests(unittest.TestCase):
    def test_cleaned_data_flows_through_features_and_visualizations(self):
        records = []
        for hour in range(8):
            records.append(
                {
                    "holiday": "None",
                    "temp": 0.0 if hour == 0 else 270.0 + hour,
                    "rain_1h": 9001.0 if hour == 1 else float(hour % 3),
                    "snow_1h": -1.0 if hour == 3 else 0.0,
                    "clouds_all": 101.0 if hour == 2 else float(hour * 10),
                    "weather_main": ("Clear", "Rain", "Clouds", "Snow")[hour % 4],
                    "weather_description": "sample",
                    "date_time": f"2017-01-{hour + 1:02d} {hour:02d}:00:00",
                    "traffic_volume": 10000.0 if hour == 7 else float((hour + 1) * 100),
                }
            )
        records.append(records[0].copy())
        repeated_timestamp = records[2].copy()
        repeated_timestamp["weather_main"] = "Fog"
        records.append(repeated_timestamp)

        raw = pd.DataFrame(records)
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory)
            cleaned = clean_data(raw)
            features = engineer_features(cleaned)
            figures = output / "figures"
            report = output / "visualization_interpretations.md"

            interpretations = create_visualizations(features, figures)
            write_interpretations(interpretations, report)

            self.assertEqual(len(cleaned), 9)
            self.assertEqual(len(features), len(cleaned))
            self.assertTrue(cleaned["temp"].gt(0).all())
            self.assertTrue(cleaned["rain_1h"].le(9000).all())
            self.assertTrue(cleaned["snow_1h"].ge(0).all())
            self.assertTrue(cleaned["clouds_all"].between(0, 100).all())
            self.assertIn(10000.0, cleaned["traffic_volume"].to_numpy())
            self.assertIn("hour_sin", features.columns)
            self.assertIn("congestion_category", features.columns)
            self.assertEqual(len(list(figures.glob("*.png"))), 4)
            self.assertTrue(report.is_file())
            self.assertEqual(len(interpretations), 4)


if __name__ == "__main__":
    unittest.main()