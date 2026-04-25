"""Unit tests for Stage 5D performance report metrics."""

import unittest

from hermes.backtest.report import generate_performance_report


class TestPerformanceReport(unittest.TestCase):
    def test_basic_mixed_trades_case(self) -> None:
        trades = [
            {"net_pnl": 10.0, "outcome": "win", "regime": "bull"},
            {"net_pnl": -5.0, "outcome": "loss", "regime": "bear"},
            {"net_pnl": 0.0, "outcome": "breakeven", "regime": "chop"},
            {"net_pnl": 20.0, "outcome": "win", "regime": "bull"},
            {"net_pnl": -15.0, "outcome": "loss", "regime": "bear"},
        ]

        report = generate_performance_report(trades)

        self.assertEqual(report["net_pnl"], 10.0)
        self.assertEqual(report["win_rate"], 0.4)
        self.assertEqual(report["avg_win"], 15.0)
        self.assertEqual(report["avg_loss"], 10.0)
        self.assertEqual(report["profit_factor"], 1.5)
        self.assertEqual(report["max_drawdown"], 15.0)
        self.assertEqual(report["trade_count"], 5)
        self.assertEqual(report["trades_per_regime"], {"bull": 2, "bear": 2, "chop": 1})
        self.assertAlmostEqual(report["stability_score"], 0.6)

    def test_only_wins(self) -> None:
        trades = [
            {"net_pnl": 5.0, "outcome": "win", "regime": "bull"},
            {"net_pnl": 10.0, "outcome": "win", "regime": "bull"},
        ]

        report = generate_performance_report(trades)

        self.assertEqual(report["avg_loss"], 0.0)
        self.assertEqual(report["profit_factor"], 999.0)
        self.assertEqual(report["max_drawdown"], 0.0)

    def test_only_losses(self) -> None:
        trades = [
            {"net_pnl": -5.0, "outcome": "loss", "regime": "bear"},
            {"net_pnl": -10.0, "outcome": "loss", "regime": "bear"},
        ]

        report = generate_performance_report(trades)

        self.assertEqual(report["win_rate"], 0.0)
        self.assertEqual(report["avg_win"], 0.0)
        self.assertEqual(report["avg_loss"], 7.5)
        self.assertEqual(report["profit_factor"], 0.0)
        self.assertEqual(report["max_drawdown"], 15.0)

    def test_empty_trades_list(self) -> None:
        report = generate_performance_report([])

        self.assertEqual(
            report,
            {
                "net_pnl": 0.0,
                "win_rate": 0.0,
                "avg_win": 0.0,
                "avg_loss": 0.0,
                "profit_factor": 0.0,
                "max_drawdown": 0.0,
                "trade_count": 0,
                "trades_per_regime": {},
                "stability_score": 0.0,
            },
        )

    def test_correct_win_rate(self) -> None:
        trades = [
            {"net_pnl": 1.0, "outcome": "win", "regime": "bull"},
            {"net_pnl": 0.0, "outcome": "breakeven", "regime": "chop"},
            {"net_pnl": -1.0, "outcome": "loss", "regime": "bear"},
            {"net_pnl": 2.0, "outcome": "win", "regime": "bull"},
        ]

        report = generate_performance_report(trades)
        self.assertEqual(report["win_rate"], 0.5)

    def test_correct_profit_factor(self) -> None:
        trades = [
            {"net_pnl": 30.0, "outcome": "win", "regime": "bull"},
            {"net_pnl": -10.0, "outcome": "loss", "regime": "bear"},
            {"net_pnl": -5.0, "outcome": "loss", "regime": "chop"},
        ]

        report = generate_performance_report(trades)
        self.assertEqual(report["profit_factor"], 2.0)

    def test_correct_max_drawdown(self) -> None:
        trades = [
            {"net_pnl": 20.0, "outcome": "win", "regime": "bull"},
            {"net_pnl": -5.0, "outcome": "loss", "regime": "bear"},
            {"net_pnl": -10.0, "outcome": "loss", "regime": "bear"},
            {"net_pnl": 2.0, "outcome": "win", "regime": "bull"},
        ]

        report = generate_performance_report(trades)
        self.assertEqual(report["max_drawdown"], 15.0)

    def test_trades_per_regime_counts(self) -> None:
        trades = [
            {"net_pnl": 1.0, "outcome": "win", "regime": "bull"},
            {"net_pnl": -1.0, "outcome": "loss", "regime": "bear"},
            {"net_pnl": 2.0, "outcome": "win", "regime": "bull"},
            {"net_pnl": 0.0, "outcome": "breakeven", "regime": "chop"},
        ]

        report = generate_performance_report(trades)
        self.assertEqual(report["trades_per_regime"], {"bull": 2, "bear": 1, "chop": 1})

    def test_deterministic_output(self) -> None:
        trades = [
            {"net_pnl": 10.0, "outcome": "win", "regime": "bull"},
            {"net_pnl": -2.0, "outcome": "loss", "regime": "bear"},
            {"net_pnl": -3.0, "outcome": "loss", "regime": "bear"},
        ]

        first = generate_performance_report(trades)
        second = generate_performance_report(trades)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
