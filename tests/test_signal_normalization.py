import unittest

from hermes.signals.normalization import normalize_signals


class TestSignalNormalization(unittest.TestCase):
    def test_valid_normalized_values(self) -> None:
        result = normalize_signals(
            {"sequence_value": 0.20, "amd_value": 0.70, "combined_value": 0.45}
        )

        self.assertEqual(result["sequence_value"], 0.20)
        self.assertEqual(result["amd_value"], 0.70)
        self.assertEqual(result["combined_value"], 0.45)
        self.assertEqual(result["agreement"], 0.50)

    def test_invalid_value_below_zero_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "sequence_value"):
            normalize_signals(
                {"sequence_value": -0.01, "amd_value": 0.70, "combined_value": 0.45}
            )

    def test_invalid_value_above_one_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "amd_value"):
            normalize_signals(
                {"sequence_value": 0.10, "amd_value": 1.01, "combined_value": 0.45}
            )

    def test_missing_required_key_raises(self) -> None:
        with self.assertRaisesRegex(KeyError, "combined_value"):
            normalize_signals({"sequence_value": 0.10, "amd_value": 0.20})

    def test_agreement_formula_correctness(self) -> None:
        result = normalize_signals(
            {"sequence_value": 0.10, "amd_value": 0.65, "combined_value": 0.40}
        )
        self.assertEqual(result["agreement"], 1.0 - abs(0.10 - 0.65))

    def test_deterministic_outputs(self) -> None:
        input_signals = {"sequence_value": 0.33, "amd_value": 0.66, "combined_value": 0.50}

        first = normalize_signals(input_signals)
        second = normalize_signals(input_signals)

        self.assertEqual(first, second)

    def test_no_implicit_casting_from_strings(self) -> None:
        with self.assertRaisesRegex(ValueError, "sequence_value"):
            normalize_signals(
                {"sequence_value": "0.25", "amd_value": 0.60, "combined_value": 0.42}
            )
