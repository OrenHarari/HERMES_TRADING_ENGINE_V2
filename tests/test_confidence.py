import unittest

from hermes.decision.confidence import compute_confidence


class TestConfidence(unittest.TestCase):
    def test_confidence_score_is_normalized(self) -> None:
        result = compute_confidence(
            {
                "sequence_value": 0.6,
                "amd_value": 0.7,
                "combined_value": 0.65,
                "agreement": 0.9,
                "momentum_score": 0.55,
                "volatility_score": 0.4,
                "regime": "trend_up",
            }
        )

        self.assertGreaterEqual(result["confidence_score"], 0.0)
        self.assertLessEqual(result["confidence_score"], 1.0)

    def test_deterministic_for_same_input(self) -> None:
        payload = {
            "sequence_value": 0.6,
            "amd_value": 0.7,
            "combined_value": 0.65,
            "agreement": 0.9,
            "momentum_score": 0.55,
            "volatility_score": 0.4,
            "regime": "trend_up",
        }

        first = compute_confidence(payload)
        second = compute_confidence(payload)
        self.assertEqual(first, second)

    def test_missing_required_field_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "missing required"):
            compute_confidence(
                {
                    "sequence_value": 0.6,
                    "amd_value": 0.7,
                    "combined_value": 0.65,
                    "agreement": 0.9,
                    "momentum_score": 0.55,
                    "regime": "trend_up",
                }
            )

    def test_rejects_implicit_string_casting(self) -> None:
        with self.assertRaisesRegex(ValueError, "must be numeric"):
            compute_confidence(
                {
                    "sequence_value": "0.6",
                    "amd_value": 0.7,
                    "combined_value": 0.65,
                    "agreement": 0.9,
                    "momentum_score": 0.55,
                    "volatility_score": 0.4,
                    "regime": "trend_up",
                }
            )

    def test_regime_weight_changes_score(self) -> None:
        base = {
            "sequence_value": 0.6,
            "amd_value": 0.7,
            "combined_value": 0.65,
            "agreement": 0.9,
            "momentum_score": 0.55,
            "volatility_score": 0.4,
        }

        trend_up = compute_confidence({**base, "regime": "trend_up"})
        chop = compute_confidence({**base, "regime": "chop"})

        self.assertGreater(trend_up["confidence_score"], chop["confidence_score"])
