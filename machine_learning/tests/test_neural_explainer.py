"""Focused tests for the neural-network model and explanation sampling."""

import unittest

import pandas as pd
from sklearn.neural_network import MLPClassifier

from machine_learning.train_neural_explainer import _explanation_indices, build_neural_model


class NeuralExplainabilityTests(unittest.TestCase):
    def test_model_pipeline_ends_in_a_neural_network(self):
        model = build_neural_model()

        self.assertIsInstance(model.named_steps["network"], MLPClassifier)
        self.assertEqual(model.named_steps["network"].hidden_layer_sizes, (64, 32))

    def test_explanation_sample_includes_both_target_classes(self):
        target = pd.Series([0, 1, 0, 1, 0, 1, 0])

        indices = _explanation_indices(target, per_class=2)

        self.assertEqual([target.iloc[index] for index in indices], [1, 1, 0, 0])


if __name__ == "__main__":
    unittest.main()