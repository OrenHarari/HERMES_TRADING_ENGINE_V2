import unittest

from hermes.backtest.performance import generate_performance_report


class TestPerformanceReport(unittest.TestCase):
    def test_report_contains_required_fields(self) -> None:
        report = generate_performance_report(
            [
                {"pnl": 100.0, "regime": "trend_up"},
                {"pnl": -40.0, "regime": "chop"},
            ],
            fees_available=False,
        )

        expected_keys = {
            "net_pnl",
            "win_rate",
            "avg_win",
            "avg_loss",
            "profit_factor",
            "max_drawdown",
            "trade_count",
            "trades_per_regime",
            "stability_score",
            "cost_model_applied",
            "notes",
        }
        self.assertEqual(set(report.keys()), expected_keys)

    def test_cost_model_flag_is_false_when_fees_missing(self) -> None:
        report = generate_performance_report([{"pnl": 10.0}], fees_available=False)
        self.assertFalse(report["cost_model_applied"])

    def test_fees_are_applied_when_available(self) -> None:
        report = generate_performance_report(
            [{"pnl": 100.0, "fee": 2.5}, {"pnl": -50.0, "fee": 2.5}], fees_available=True
        )
        self.assertEqual(report["net_pnl"], 45.0)
        self.assertTrue(report["cost_model_applied"])

    def test_trades_per_regime_counts(self) -> None:
        report = generate_performance_report(
            [
                {"pnl": 10.0, "regime": "trend_up"},
                {"pnl": 20.0, "regime": "trend_up"},
                {"pnl": -5.0, "regime": "chop"},
            ],
            fees_available=False,
        )

        self.assertEqual(report["trades_per_regime"]["trend_up"], 2)
        self.assertEqual(report["trades_per_regime"]["chop"], 1)

    def test_win_rate_alone_not_marked_as_success(self) -> None:
        report = generate_performance_report(
            [{"pnl": 1.0}, {"pnl": 1.0}, {"pnl": -5.0}], fees_available=False
        )
        self.assertIn("win rate alone is not enough", report["notes"].lower())
