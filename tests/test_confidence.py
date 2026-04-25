"""Unit tests for Stage 5A confidence scoring."""

import unittest

from hermes.trading.confidence import compute_confidence


class ConfidenceTests(unittest.TestCase):
    def test_confidence_is_clamped_to_valid_range(self) -> None:
        signal = {
            "sequence_value": 0.0,
            "amd_value": 0.0,
            "combined_value": 2.0,
            "agreement": 2.0,
            "label": "strong",
            "momentum_score": 2.0,
            "volatility_score": -1.0,
            "regime": "trend_up",
        }

        confidence = compute_confidence(signal)

        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)

    def test_confidence_is_deterministic(self) -> None:
        signal = {
            "sequence_value": 0.4,
            "amd_value": 0.5,
            "combined_value": 0.6,
            "agreement": 0.7,
            "label": "medium",
            "momentum_score": 0.8,
            "volatility_score": 0.2,
            "regime": "low_volatility",
        }

        first = compute_confidence(signal)
        second = compute_confidence(signal)

        self.assertEqual(first, second)

    def test_higher_combined_value_increases_confidence(self) -> None:
        low_combined_signal = {
            "sequence_value": 0.5,
            "amd_value": 0.5,
            "combined_value": 0.2,
            "agreement": 0.6,
            "label": "weak",
            "momentum_score": 0.6,
            "volatility_score": 0.3,
            "regime": "trend_up",
        }
        high_combined_signal = dict(low_combined_signal)
        high_combined_signal["combined_value"] = 0.9

        low_confidence = compute_confidence(low_combined_signal)
        high_confidence = compute_confidence(high_combined_signal)

        self.assertGreater(high_confidence, low_confidence)


if __name__ == "__main__":
    unittest.main()
