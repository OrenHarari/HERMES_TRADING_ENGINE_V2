"""Stage 2 orchestrator tests."""

import unittest

from hermes.signals.orchestrator import orchestrate_signals


class TestOrchestrateSignals(unittest.TestCase):
    def test_strong_label_case(self) -> None:
        result = orchestrate_signals(
            {"sequence_value": 0.9, "amd_value": 0.9, "combined_value": 0.7}
        )

        self.assertAlmostEqual(result["sequence_value"], 0.9)
        self.assertAlmostEqual(result["amd_value"], 0.9)
        self.assertAlmostEqual(result["combined_value"], 0.7)
        self.assertAlmostEqual(result["agreement"], 1.0)
        self.assertEqual(result["label"], "strong")

    def test_medium_label_case(self) -> None:
        result = orchestrate_signals(
            {"sequence_value": 0.2, "amd_value": 0.2, "combined_value": 0.5}
        )

        self.assertAlmostEqual(result["sequence_value"], 0.2)
        self.assertAlmostEqual(result["amd_value"], 0.2)
        self.assertAlmostEqual(result["combined_value"], 0.5)
        self.assertAlmostEqual(result["agreement"], 1.0)
        self.assertEqual(result["label"], "medium")

    def test_weak_label_case(self) -> None:
        result = orchestrate_signals(
            {"sequence_value": 0.1, "amd_value": 0.9, "combined_value": 0.49}
        )

        self.assertAlmostEqual(result["sequence_value"], 0.1)
        self.assertAlmostEqual(result["amd_value"], 0.9)
        self.assertAlmostEqual(result["combined_value"], 0.49)
        self.assertAlmostEqual(result["agreement"], 0.2)
        self.assertEqual(result["label"], "weak")

    def test_deterministic_output(self) -> None:
        input_signals = {"sequence_value": 0.33, "amd_value": 0.23, "combined_value": 0.61}

        first = orchestrate_signals(input_signals)
        second = orchestrate_signals(input_signals)

        self.assertEqual(first, second)

    def test_label_depends_only_on_values(self) -> None:
        strong_by_both = orchestrate_signals(
            {"sequence_value": 0.8, "amd_value": 0.8, "combined_value": 0.7}
        )
        medium_by_combined_only = orchestrate_signals(
            {"sequence_value": 0.9, "amd_value": 0.2, "combined_value": 0.69}
        )

        self.assertEqual(strong_by_both["label"], "strong")
        self.assertEqual(medium_by_combined_only["label"], "medium")

    def test_normalization_errors_propagate(self) -> None:
        with self.assertRaises(KeyError):
            orchestrate_signals({"sequence_value": 0.1, "amd_value": 0.2})


if __name__ == "__main__":
    unittest.main()
