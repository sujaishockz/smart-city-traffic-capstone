"""Focused tests for API model serving and distribution drift detection."""

import unittest

import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

from machine_learning.deployment.app import app
from machine_learning.monitor_drift import evaluate_drift, population_stability_index


class MLOpsTests(unittest.TestCase):
    def test_api_health_and_model_prediction(self):
        client = TestClient(app)
        health = client.get("/health")
        prediction = client.post(
            "/predict",
            json={
                "hour": 8,
                "day_of_week": 1,
                "is_weekend": 0,
                "holiday_flag": 0,
                "month": 6,
                "temp": 290.0,
                "rain_1h": 0.0,
                "snow_1h": 0.0,
                "clouds_all": 25.0,
                "weather_main": "Clear",
            },
        )

        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.json()["model_version"], "1.0.0")
        self.assertEqual(prediction.status_code, 200)
        self.assertGreater(prediction.json()["predicted_traffic_volume"], 0)

    def test_population_stability_and_alert_threshold(self):
        reference = pd.Series(np.arange(1000, dtype=float))
        same = pd.Series(np.arange(1000, dtype=float))
        shifted = pd.Series(np.arange(1000, dtype=float) * 2 + 500)

        self.assertAlmostEqual(population_stability_index(reference, same), 0.0, places=6)
        self.assertEqual(evaluate_drift(pd.DataFrame({"x": reference}), pd.DataFrame({"x": same}), ("x",))["status"], "PASS/Normal")
        self.assertEqual(
            evaluate_drift(pd.DataFrame({"x": reference}), pd.DataFrame({"x": shifted}), ("x",))["status"],
            "ALERT/Requires investigation",
        )


if __name__ == "__main__":
    unittest.main()