import unittest

from hermes.backtest.validation import validate_backtest


class TestBacktestValidation(unittest.TestCase):
    def test_validation_passes_for_clean_deterministic_run(self) -> None:
        result = validate_backtest(
            {
                "lookahead_bias": False,
                "data_leakage": False,
                "future_data_used": False,
                "outcome_used_in_signals": False,
                "future_candles_visible": False,
                "same_input_same_output": True,
                "replay_outputs": [
                    {"signal": "a", "value": 1},
                    {"signal": "a", "value": 1},
                ],
            }
        )

        self.assertTrue(result["validation_passed"])
        self.assertEqual(result["reason"], "")

    def test_fails_when_lookahead_bias_exists(self) -> None:
        result = validate_backtest(
            {
                "lookahead_bias": True,
                "data_leakage": False,
                "future_data_used": False,
                "outcome_used_in_signals": False,
                "future_candles_visible": False,
                "same_input_same_output": True,
                "replay_outputs": [{"signal": "a"}],
            }
        )
        self.assertFalse(result["validation_passed"])
        self.assertIn("lookahead bias", result["reason"])

    def test_fails_when_replay_not_deterministic(self) -> None:
        result = validate_backtest(
            {
                "lookahead_bias": False,
                "data_leakage": False,
                "future_data_used": False,
                "outcome_used_in_signals": False,
                "future_candles_visible": False,
                "same_input_same_output": True,
                "replay_outputs": [
                    {"signal": "a", "value": 1},
                    {"signal": "a", "value": 2},
                ],
            }
        )
        self.assertFalse(result["validation_passed"])
        self.assertIn("deterministic", result["reason"])

    def test_fails_when_required_fields_missing(self) -> None:
        result = validate_backtest({"lookahead_bias": False})
        self.assertFalse(result["validation_passed"])
        self.assertIn("missing required", result["reason"])
