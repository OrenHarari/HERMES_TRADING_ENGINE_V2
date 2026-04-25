"""Unit tests for Stage 6B signal attribution."""

import unittest

from hermes.learning.attribution import build_signal_attribution


class AttributionTests(unittest.TestCase):
    def _trade(
        self,
        *,
        confidence: float,
        regime: str,
        outcome: str,
        pnl: float,
    ) -> dict:
        return {
            "confidence": confidence,
            "regime": regime,
            "outcome": outcome,
            "pnl": pnl,
        }

    def test_conditions_below_minimum_sample_size_are_excluded(self) -> None:
        trades = [
            self._trade(confidence=0.05, regime="trend", outcome="win", pnl=10.0),
            self._trade(confidence=0.05, regime="trend", outcome="loss", pnl=-8.0),
            self._trade(confidence=0.25, regime="range", outcome="win", pnl=6.0),
        ]

        result = build_signal_attribution(
            trades,
            min_trades_per_bucket=3,
            min_trades_per_regime=3,
            min_trades_per_combination=3,
        )

        self.assertEqual(result["thresholds_adapted"], False)
        self.assertEqual(result["reason"], "insufficient_sample_size")

    def test_completed_trades_group_into_correct_confidence_buckets(self) -> None:
        trades = [
            self._trade(confidence=0.05, regime="trend", outcome="win", pnl=10.0),
            self._trade(confidence=0.09, regime="trend", outcome="loss", pnl=-5.0),
            self._trade(confidence=0.10, regime="trend", outcome="win", pnl=4.0),
            self._trade(confidence=0.19, regime="trend", outcome="win", pnl=3.0),
            self._trade(confidence=1.00, regime="trend", outcome="loss", pnl=-2.0),
        ]

        result = build_signal_attribution(
            trades,
            min_trades_per_bucket=1,
            min_trades_per_regime=1,
            min_trades_per_combination=1,
        )

        conditions = {
            item["condition"]: item for item in result["best_conditions"] + result["worst_conditions"]
        }
        self.assertIn("confidence:0.0-0.1", conditions)
        self.assertIn("confidence:0.1-0.2", conditions)
        self.assertIn("confidence:0.9-1.0", conditions)
        self.assertEqual(conditions["confidence:0.0-0.1"]["trade_count"], 2)
        self.assertEqual(conditions["confidence:0.1-0.2"]["trade_count"], 2)
        self.assertEqual(conditions["confidence:0.9-1.0"]["trade_count"], 1)

    def test_regime_attribution_is_calculated_correctly(self) -> None:
        trades = [
            self._trade(confidence=0.21, regime="trend", outcome="win", pnl=5.0),
            self._trade(confidence=0.23, regime="trend", outcome="loss", pnl=-4.0),
            self._trade(confidence=0.24, regime="range", outcome="win", pnl=3.0),
            self._trade(confidence=0.26, regime="range", outcome="win", pnl=2.0),
        ]

        result = build_signal_attribution(
            trades,
            min_trades_per_bucket=1,
            min_trades_per_regime=2,
            min_trades_per_combination=1,
        )

        all_conditions = result["best_conditions"] + result["worst_conditions"]
        regime_map = {
            item["condition"]: item
            for item in all_conditions
            if item["condition"].startswith("regime:")
        }
        self.assertEqual(regime_map["regime:trend"]["win_rate"], 0.5)
        self.assertEqual(regime_map["regime:range"]["win_rate"], 1.0)

    def test_cross_analysis_is_calculated_correctly(self) -> None:
        trades = [
            self._trade(confidence=0.45, regime="trend", outcome="win", pnl=6.0),
            self._trade(confidence=0.49, regime="trend", outcome="loss", pnl=-6.0),
            self._trade(confidence=0.45, regime="range", outcome="win", pnl=4.0),
        ]

        result = build_signal_attribution(
            trades,
            min_trades_per_bucket=1,
            min_trades_per_regime=1,
            min_trades_per_combination=2,
        )

        all_conditions = result["best_conditions"] + result["worst_conditions"]
        cross_map = {
            item["condition"]: item
            for item in all_conditions
            if "|regime:" in item["condition"]
        }
        self.assertIn("confidence:0.4-0.5|regime:trend", cross_map)
        self.assertNotIn("confidence:0.4-0.5|regime:range", cross_map)
        self.assertEqual(cross_map["confidence:0.4-0.5|regime:trend"]["win_rate"], 0.5)

    def test_incomplete_trades_are_ignored(self) -> None:
        trades = [
            self._trade(confidence=0.33, regime="trend", outcome="win", pnl=5.0),
            {"confidence": 0.33, "regime": "trend", "outcome": "win"},
            {"confidence": 0.33, "regime": "trend", "pnl": 2.0},
            {"regime": "trend", "outcome": "loss", "pnl": -2.0},
        ]

        result = build_signal_attribution(
            trades,
            min_trades_per_bucket=1,
            min_trades_per_regime=1,
            min_trades_per_combination=1,
        )

        self.assertEqual(result["total_trades"], 1)
        self.assertEqual(result["overall_win_rate"], 1.0)

    def test_avg_net_pnl_is_calculated_when_pnl_exists(self) -> None:
        trades = [
            self._trade(confidence=0.12, regime="trend", outcome="win", pnl=10.0),
            self._trade(confidence=0.14, regime="trend", outcome="loss", pnl=-6.0),
        ]

        result = build_signal_attribution(
            trades,
            min_trades_per_bucket=1,
            min_trades_per_regime=1,
            min_trades_per_combination=1,
        )

        all_conditions = result["best_conditions"] + result["worst_conditions"]
        bucket_condition = next(
            item for item in all_conditions if item["condition"] == "confidence:0.1-0.2"
        )
        self.assertEqual(bucket_condition["avg_net_pnl"], 2.0)

    def test_profit_factor_is_calculated_when_wins_and_losses_exist(self) -> None:
        trades = [
            self._trade(confidence=0.62, regime="trend", outcome="win", pnl=10.0),
            self._trade(confidence=0.68, regime="trend", outcome="win", pnl=5.0),
            self._trade(confidence=0.66, regime="trend", outcome="loss", pnl=-5.0),
        ]

        result = build_signal_attribution(
            trades,
            min_trades_per_bucket=1,
            min_trades_per_regime=1,
            min_trades_per_combination=1,
        )

        all_conditions = result["best_conditions"] + result["worst_conditions"]
        bucket_condition = next(
            item for item in all_conditions if item["condition"] == "confidence:0.6-0.7"
        )
        self.assertEqual(bucket_condition["profit_factor"], 3.0)

    def test_same_input_produces_same_output(self) -> None:
        trades = [
            self._trade(confidence=0.71, regime="trend", outcome="win", pnl=7.0),
            self._trade(confidence=0.72, regime="trend", outcome="loss", pnl=-3.0),
            self._trade(confidence=0.75, regime="range", outcome="loss", pnl=-2.0),
        ]

        first = build_signal_attribution(
            trades,
            min_trades_per_bucket=1,
            min_trades_per_regime=1,
            min_trades_per_combination=1,
        )
        second = build_signal_attribution(
            trades,
            min_trades_per_bucket=1,
            min_trades_per_regime=1,
            min_trades_per_combination=1,
        )

        self.assertEqual(first, second)

    def test_thresholds_adapted_is_always_false(self) -> None:
        trades = [
            self._trade(confidence=0.50, regime="trend", outcome="win", pnl=5.0),
            self._trade(confidence=0.55, regime="trend", outcome="loss", pnl=-5.0),
        ]

        result = build_signal_attribution(
            trades,
            min_trades_per_bucket=1,
            min_trades_per_regime=1,
            min_trades_per_combination=1,
        )

        self.assertEqual(result["thresholds_adapted"], False)

    def test_production_defaults_can_be_overridden_in_tests(self) -> None:
        trades = [
            self._trade(confidence=0.82, regime="trend", outcome="win", pnl=8.0),
            self._trade(confidence=0.84, regime="trend", outcome="loss", pnl=-2.0),
        ]

        default_result = build_signal_attribution(trades)
        injected_result = build_signal_attribution(
            trades,
            min_trades_per_bucket=1,
            min_trades_per_regime=1,
            min_trades_per_combination=1,
        )

        self.assertEqual(default_result["reason"], "insufficient_sample_size")
        self.assertNotIn("reason", injected_result)


if __name__ == "__main__":
    unittest.main()
