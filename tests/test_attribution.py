import unittest

from hermes.learning.attribution import analyze_signal_attribution


class TestAttribution(unittest.TestCase):
    def _trade(self, confidence: float, regime: str, outcome: str, net_pnl: float) -> dict:
        return {
            "confidence": confidence,
            "regime": regime,
            "outcome": outcome,
            "net_pnl": net_pnl,
        }

    def test_attribution_respects_minimum_sample_sizes(self) -> None:
        trades = [self._trade(0.8, "trend_up", "win", 10.0) for _ in range(10)]

        result = analyze_signal_attribution(trades)
        self.assertEqual(result["best_conditions"], [])
        self.assertEqual(result["worst_conditions"], [])
        self.assertTrue(result["insufficient_data"])

    def test_best_and_worst_conditions_are_generated(self) -> None:
        trades = []
        trades.extend([self._trade(0.85, "trend_up", "win", 15.0) for _ in range(30)])
        trades.extend([self._trade(0.82, "trend_up", "loss", -8.0) for _ in range(20)])
        trades.extend([self._trade(0.45, "chop", "loss", -5.0) for _ in range(35)])
        trades.extend([self._trade(0.48, "chop", "win", 6.0) for _ in range(25)])

        result = analyze_signal_attribution(
            trades,
            min_trades_per_bucket=20,
            min_trades_per_regime=30,
            min_trades_per_combination=50,
        )

        self.assertGreater(len(result["best_conditions"]), 0)
        self.assertGreater(len(result["worst_conditions"]), 0)

        for item in result["best_conditions"] + result["worst_conditions"]:
            self.assertIn("condition", item)
            self.assertIn("win_rate", item)
            self.assertIn("trade_count", item)
            self.assertIn("avg_net_pnl", item)
            self.assertIn("profit_factor", item)

    def test_same_input_produces_same_output(self) -> None:
        trades = [self._trade(0.85, "trend_up", "win", 10.0) for _ in range(60)]

        first = analyze_signal_attribution(
            trades,
            min_trades_per_bucket=20,
            min_trades_per_regime=30,
            min_trades_per_combination=50,
        )
        second = analyze_signal_attribution(
            trades,
            min_trades_per_bucket=20,
            min_trades_per_regime=30,
            min_trades_per_combination=50,
        )

        self.assertEqual(first, second)
