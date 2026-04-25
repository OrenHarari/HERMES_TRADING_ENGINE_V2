import unittest

from hermes.signals.orchestrator import orchestrate_signals


class TestOrchestrator(unittest.TestCase):
    def test_output_contains_required_keys(self) -> None:
        result = orchestrate_signals(
            {"sequence_value": 0.20, "amd_value": 0.80, "combined_value": 0.50}
        )

        self.assertEqual(
            set(result.keys()),
            {"sequence_value", "amd_value", "combined_value", "agreement", "label"},
        )

    def test_numeric_outputs_are_normalized(self) -> None:
        result = orchestrate_signals(
            {"sequence_value": 0.25, "amd_value": 0.75, "combined_value": 0.60}
        )

        for key in ("sequence_value", "amd_value", "combined_value", "agreement"):
            self.assertGreaterEqual(result[key], 0.0)
            self.assertLessEqual(result[key], 1.0)

    def test_label_is_derived_from_normalized_values(self) -> None:
        bullish = orchestrate_signals(
            {"sequence_value": 0.90, "amd_value": 0.90, "combined_value": 0.90}
        )
        bearish = orchestrate_signals(
            {"sequence_value": 0.10, "amd_value": 0.10, "combined_value": 0.10}
        )
        neutral = orchestrate_signals(
            {"sequence_value": 0.40, "amd_value": 0.80, "combined_value": 0.60}
        )

        self.assertEqual(bullish["label"], "bullish")
        self.assertEqual(bearish["label"], "bearish")
        self.assertEqual(neutral["label"], "neutral")

    def test_deterministic_output_for_same_input(self) -> None:
        input_signals = {"sequence_value": 0.33, "amd_value": 0.66, "combined_value": 0.50}

        first = orchestrate_signals(input_signals)
        second = orchestrate_signals(input_signals)

        self.assertEqual(first, second)

    def test_no_implicit_casting_from_strings(self) -> None:
        with self.assertRaisesRegex(ValueError, "sequence_value"):
            orchestrate_signals(
                {"sequence_value": "0.50", "amd_value": 0.60, "combined_value": 0.55}
            )
