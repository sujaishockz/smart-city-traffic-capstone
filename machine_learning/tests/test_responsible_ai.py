"""Focused tests for responsible-AI subgroup metric calculations."""

import unittest

import numpy as np

from machine_learning.analyze_responsible_ai import subgroup_metrics


class ResponsibleAIMetricTests(unittest.TestCase):
    def test_subgroup_metrics_report_tpr_fpr_precision_and_f1(self):
        metrics = subgroup_metrics(np.array([1, 1, 0, 0]), np.array([1, 0, 1, 0]))

        self.assertEqual(metrics["support"], 4)
        self.assertEqual(metrics["recall_tpr"], 0.5)
        self.assertEqual(metrics["false_positive_rate"], 0.5)
        self.assertEqual(metrics["precision"], 0.5)
        self.assertEqual(metrics["f1"], 0.5)

    def test_rates_are_none_when_group_has_no_positive_examples(self):
        metrics = subgroup_metrics(np.array([0, 0]), np.array([0, 1]))

        self.assertIsNone(metrics["recall_tpr"])
        self.assertEqual(metrics["false_positive_rate"], 0.5)


if __name__ == "__main__":
    unittest.main()