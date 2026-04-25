"""Unit tests for Stage 1 signal normalization."""

import unittest

from hermes.signals.normalization import normalize_signals


class SignalNormalizationTests(unittest.TestCase):
    def test_valid_values(self) -> None:
        result = normalize_signals(
            {
                "sequence_value": 0.2,
                "amd_value": 0.8,
                "combined_value": 0.5,
            }
        )

        self.assertAlmostEqual(result["sequence_value"], 0.2)
        self.assertAlmostEqual(result["amd_value"], 0.8)
        self.assertAlmostEqual(result["combined_value"], 0.5)
        self.assertAlmostEqual(result["agreement"], 0.4)

    def test_value_below_zero_raises(self) -> None:
        with self.assertRaises(ValueError):
            normalize_signals(
                {
                    "sequence_value": -0.01,
                    "amd_value": 0.8,
                    "combined_value": 0.5,
                }
            )

    def test_value_above_one_raises(self) -> None:
        with self.assertRaises(ValueError):
            normalize_signals(
                {
                    "sequence_value": 0.2,
                    "amd_value": 1.01,
                    "combined_value": 0.5,
                }
            )

    def test_missing_key_raises(self) -> None:
        with self.assertRaises(KeyError):
            normalize_signals(
                {
                    "sequence_value": 0.2,
                    "amd_value": 0.8,
                }
            )

    def test_string_input_rejected(self) -> None:
        with self.assertRaises(ValueError):
            normalize_signals(
                {
                    "sequence_value": "0.2",
                    "amd_value": 0.8,
                    "combined_value": 0.5,
                }
            )

    def test_bool_rejected(self) -> None:
        with self.assertRaises(ValueError):
            normalize_signals(
                {
                    "sequence_value": True,
                    "amd_value": 0.8,
                    "combined_value": 0.5,
                }
            )

    def test_agreement_formula_correctness(self) -> None:
        result = normalize_signals(
            {
                "sequence_value": 0.95,
                "amd_value": 0.25,
                "combined_value": 0.6,
            }
        )

        expected_agreement = 1 - abs(0.95 - 0.25)
        self.assertAlmostEqual(result["agreement"], expected_agreement)

    def test_deterministic_output(self) -> None:
        input_signals = {
            "sequence_value": 0.31,
            "amd_value": 0.77,
            "combined_value": 0.54,
        }

        result_one = normalize_signals(input_signals)
        result_two = normalize_signals(input_signals)

        self.assertAlmostEqual(result_one["sequence_value"], result_two["sequence_value"])
        self.assertAlmostEqual(result_one["amd_value"], result_two["amd_value"])
        self.assertAlmostEqual(result_one["combined_value"], result_two["combined_value"])
        self.assertAlmostEqual(result_one["agreement"], result_two["agreement"])


if __name__ == "__main__":
    unittest.main()
