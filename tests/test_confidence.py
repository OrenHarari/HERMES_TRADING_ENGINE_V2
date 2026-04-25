"""Unit tests for Stage 5A confidence scoring."""

import unittest

from hermes.decision.confidence import compute_confidence


class TestComputeConfidence(unittest.TestCase):
    def test_confidence_range(self) -> None:
        low_signal = {
            "combined_value": -0.5,
            "agreement": 0.0,
            "momentum_score": 0.0,
            "volatility_score": 2.0,
            "regime": "chop",
        }
        high_signal = {
            "combined_value": 2.0,
            "agreement": 1.0,
            "momentum_score": 1.0,
            "volatility_score": -1.0,
            "regime": "trend_up",
        }

        self.assertGreaterEqual(compute_confidence(low_signal), 0.0)
        self.assertLessEqual(compute_confidence(low_signal), 1.0)
        self.assertGreaterEqual(compute_confidence(high_signal), 0.0)
        self.assertLessEqual(compute_confidence(high_signal), 1.0)

    def test_deterministic_confidence(self) -> None:
        signal = {
            "combined_value": 0.62,
            "agreement": 0.71,
            "momentum_score": 0.44,
            "volatility_score": 0.30,
            "regime": "trend_down",
        }

        first = compute_confidence(signal)
        second = compute_confidence(signal)

        self.assertEqual(first, second)

    def test_higher_combined_value_increases_confidence(self) -> None:
        low_combined = {
            "combined_value": 0.20,
            "agreement": 0.60,
            "momentum_score": 0.50,
            "volatility_score": 0.20,
            "regime": "trend_up",
        }
        high_combined = {
            "combined_value": 0.80,
            "agreement": 0.60,
            "momentum_score": 0.50,
            "volatility_score": 0.20,
            "regime": "trend_up",
        }

        self.assertGreater(compute_confidence(high_combined), compute_confidence(low_combined))


if __name__ == "__main__":
    unittest.main()
