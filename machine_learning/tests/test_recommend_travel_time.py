"""Focused tests for weather/day-type recommendation construction and ranking."""

import unittest

import pandas as pd

from machine_learning.recommend_travel_time import build_candidate_features, recommend_for_conditions


class HourBasedModel:
    def predict(self, features):
        return features["hour"].to_numpy()


class TravelRecommendationTests(unittest.TestCase):
    def setUp(self):
        self.history = pd.DataFrame(
            {
                "weather_main": ["Clear", "Clear", "Rain"],
                "temp": [280.0, 300.0, 290.0],
                "rain_1h": [0.0, 0.0, 2.0],
                "snow_1h": [0.0, 0.0, 0.0],
                "clouds_all": [10.0, 30.0, 80.0],
            }
        )

    def test_candidate_features_average_typical_weather_and_day_type(self):
        candidates, weather_records = build_candidate_features(self.history, "weekday", "Clear", 6)

        self.assertEqual(len(candidates), 120)
        self.assertEqual(weather_records, 2)
        self.assertEqual(candidates["day_of_week"].unique().tolist(), [0, 1, 2, 3, 4])
        self.assertEqual(candidates["temp"].unique().tolist(), [290.0])
        self.assertEqual(candidates["weather_main"].unique().tolist(), ["Clear"])

    def test_recommendations_are_lowest_ranked_non_overlapping_windows(self):
        result = recommend_for_conditions(HourBasedModel(), self.history, "weekend", "Clear", top_n=2)

        self.assertEqual([item["window"] for item in result["windows"]], ["00:00-02:00", "02:00-04:00"])
        self.assertTrue(all(item["mean_predicted_traffic"] >= 0 for item in result["windows"]))


if __name__ == "__main__":
    unittest.main()