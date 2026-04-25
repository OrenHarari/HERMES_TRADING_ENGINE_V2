"""Unit tests for Stage 6C threshold adaptation baseline."""

import os
import inspect
import unittest

from hermes.learning.threshold_adapter import adapt_thresholds


class ThresholdAdapterTests(unittest.TestCase):
    def _trade(self, *, confidence: float, outcome: str, regime: str = "trend") -> dict:
        return {
            "confidence": confidence,
            "regime": regime,
            "outcome": outcome,
        }

    def _wins_losses(self, confidence: float, wins: int, losses: int, regime: str = "trend") -> list:
        trades = []
        for _ in range(wins):
            trades.append(self._trade(confidence=confidence, outcome="win", regime=regime))
        for _ in range(losses):
            trades.append(self._trade(confidence=confidence, outcome="loss", regime=regime))
        return trades

    def test_no_adaptation_below_100_completed_trades(self) -> None:
        trades = self._wins_losses(0.6, wins=60, losses=39)

        result = adapt_thresholds(trades, {"min_confidence": 0.5, "allow_chop": True})

        self.assertEqual(result, {"thresholds_adapted": False, "reason": "insufficient_sample_size"})

    def test_adaptation_respects_bucket_minimums(self) -> None:
        trades = []
        trades.extend(self._wins_losses(0.4, wins=19, losses=0))
        trades.extend(self._wins_losses(0.6, wins=40, losses=10))
        trades.extend(self._wins_losses(0.7, wins=16, losses=15))

        result = adapt_thresholds(trades, {"min_confidence": 0.8, "allow_chop": True})

        self.assertEqual(result["thresholds_adapted"], True)
        self.assertEqual(result["new_thresholds"]["min_confidence"], 0.6)

    def test_min_confidence_remains_within_bounds(self) -> None:
        trades = []
        trades.extend(self._wins_losses(0.0, wins=20, losses=0))
        trades.extend(self._wins_losses(0.8, wins=50, losses=30))

        result = adapt_thresholds(trades, {"min_confidence": 0.85, "allow_chop": True})

        self.assertEqual(result["thresholds_adapted"], True)
        self.assertEqual(result["new_thresholds"]["min_confidence"], 0.4)

    def test_lowest_qualifying_bucket_is_selected(self) -> None:
        trades = []
        trades.extend(self._wins_losses(0.3, wins=5, losses=15))
        trades.extend(self._wins_losses(0.5, wins=11, losses=9))
        trades.extend(self._wins_losses(0.7, wins=20, losses=0))
        trades.extend(self._wins_losses(0.8, wins=30, losses=10))

        result = adapt_thresholds(trades, {"min_confidence": 0.75, "allow_chop": True})

        self.assertEqual(result["thresholds_adapted"], True)
        self.assertEqual(result["new_thresholds"]["min_confidence"], 0.5)

    def test_chop_rule_sets_allow_chop_false_below_threshold(self) -> None:
        trades = []
        trades.extend(self._wins_losses(0.6, wins=40, losses=20, regime="trend"))
        trades.extend(self._wins_losses(0.6, wins=10, losses=30, regime="chop"))

        result = adapt_thresholds(trades, {"min_confidence": 0.7, "allow_chop": True})

        self.assertEqual(result["thresholds_adapted"], True)
        self.assertEqual(result["new_thresholds"]["allow_chop"], False)

    def test_chop_rule_sets_allow_chop_true_when_high_win_rate(self) -> None:
        trades = []
        trades.extend(self._wins_losses(0.6, wins=30, losses=10, regime="trend"))
        trades.extend(self._wins_losses(0.6, wins=20, losses=5, regime="range"))
        trades.extend(self._wins_losses(0.6, wins=24, losses=6, regime="chop"))
        trades.extend(self._wins_losses(0.8, wins=0, losses=5, regime="trend"))

        result = adapt_thresholds(trades, {"min_confidence": 0.7, "allow_chop": False})

        self.assertEqual(result["thresholds_adapted"], True)
        self.assertEqual(result["new_thresholds"]["allow_chop"], True)

    def test_no_chop_change_when_sample_is_insufficient(self) -> None:
        trades = []
        trades.extend(self._wins_losses(0.6, wins=40, losses=30, regime="trend"))
        trades.extend(self._wins_losses(0.6, wins=15, losses=14, regime="chop"))
        trades.extend(self._wins_losses(0.8, wins=0, losses=1, regime="trend"))

        result = adapt_thresholds(trades, {"min_confidence": 0.7, "allow_chop": True})

        self.assertEqual(result["thresholds_adapted"], True)
        self.assertEqual(result["new_thresholds"]["allow_chop"], True)

    def test_no_adaptation_when_no_bucket_qualifies(self) -> None:
        trades = []
        trades.extend(self._wins_losses(0.5, wins=9, losses=11, regime="trend"))
        trades.extend(self._wins_losses(0.6, wins=14, losses=16, regime="trend"))
        trades.extend(self._wins_losses(0.7, wins=20, losses=30, regime="range"))

        result = adapt_thresholds(trades, {"min_confidence": 0.7, "allow_chop": True})

        self.assertEqual(result["thresholds_adapted"], False)
        self.assertEqual(result["reason"], "no_qualifying_bucket")

    def test_same_input_produces_same_output(self) -> None:
        trades = []
        trades.extend(self._wins_losses(0.4, wins=25, losses=5, regime="trend"))
        trades.extend(self._wins_losses(0.7, wins=35, losses=35, regime="range"))

        first = adapt_thresholds(trades, {"min_confidence": 0.6, "allow_chop": True})
        second = adapt_thresholds(trades, {"min_confidence": 0.6, "allow_chop": True})

        self.assertEqual(first, second)

    def test_prompt2_files_are_not_created_or_required(self) -> None:
        trades = []
        trades.extend(self._wins_losses(0.6, wins=40, losses=20, regime="trend"))
        trades.extend(self._wins_losses(0.7, wins=30, losses=10, regime="range"))

        _ = adapt_thresholds(trades, {"min_confidence": 0.75, "allow_chop": True})

        self.assertEqual(os.path.exists("active_thresholds.json"), False)
        self.assertEqual(os.path.exists("candidate_thresholds.json"), False)

    def test_stage6c_api_does_not_expose_unused_combination_minimum(self) -> None:
        parameters = inspect.signature(adapt_thresholds).parameters
        self.assertNotIn("min_trades_per_combination", parameters)


if __name__ == "__main__":
    unittest.main()
