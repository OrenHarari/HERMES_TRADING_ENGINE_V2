"""Tests for backtest validation gate (Stage 5C)."""

import unittest

from hermes.backtest.validation import validate_backtest


class TestBacktestValidation(unittest.TestCase):
    def test_passed_validation_case(self) -> None:
        payload = {
            "lookahead_bias_detected": False,
            "data_leakage_detected": False,
            "future_data_used": False,
            "replay_deterministic": True,
            "outcome_used_in_signal_generation": False,
        }

        result = validate_backtest(payload)

        self.assertEqual(
            result,
            {
                "validation_passed": True,
                "reason": "passed",
            },
        )

    def test_blocked_by_lookahead_bias(self) -> None:
        payload = {
            "lookahead_bias_detected": True,
            "data_leakage_detected": False,
            "future_data_used": False,
            "replay_deterministic": True,
            "outcome_used_in_signal_generation": False,
        }

        result = validate_backtest(payload)

        self.assertEqual(
            result,
            {
                "validation_passed": False,
                "reason": "lookahead_bias_detected",
            },
        )

    def test_blocked_by_data_leakage(self) -> None:
        payload = {
            "lookahead_bias_detected": False,
            "data_leakage_detected": True,
            "future_data_used": False,
            "replay_deterministic": True,
            "outcome_used_in_signal_generation": False,
        }

        result = validate_backtest(payload)

        self.assertEqual(
            result,
            {
                "validation_passed": False,
                "reason": "data_leakage_detected",
            },
        )

    def test_blocked_by_future_data(self) -> None:
        payload = {
            "lookahead_bias_detected": False,
            "data_leakage_detected": False,
            "future_data_used": True,
            "replay_deterministic": True,
            "outcome_used_in_signal_generation": False,
        }

        result = validate_backtest(payload)

        self.assertEqual(
            result,
            {
                "validation_passed": False,
                "reason": "future_data_used",
            },
        )

    def test_blocked_by_non_deterministic_replay(self) -> None:
        payload = {
            "lookahead_bias_detected": False,
            "data_leakage_detected": False,
            "future_data_used": False,
            "replay_deterministic": False,
            "outcome_used_in_signal_generation": False,
        }

        result = validate_backtest(payload)

        self.assertEqual(
            result,
            {
                "validation_passed": False,
                "reason": "replay_not_deterministic",
            },
        )

    def test_blocked_by_outcome_used_in_signal_generation(self) -> None:
        payload = {
            "lookahead_bias_detected": False,
            "data_leakage_detected": False,
            "future_data_used": False,
            "replay_deterministic": True,
            "outcome_used_in_signal_generation": True,
        }

        result = validate_backtest(payload)

        self.assertEqual(
            result,
            {
                "validation_passed": False,
                "reason": "outcome_used_in_signal_generation",
            },
        )

    def test_deterministic_output(self) -> None:
        payload = {
            "lookahead_bias_detected": False,
            "data_leakage_detected": False,
            "future_data_used": False,
            "replay_deterministic": True,
            "outcome_used_in_signal_generation": False,
        }

        first = validate_backtest(payload)
        second = validate_backtest(payload)

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
