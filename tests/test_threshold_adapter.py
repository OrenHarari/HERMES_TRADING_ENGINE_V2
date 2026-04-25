import unittest

from hermes.learning.edge_decay import monitor_edge_decay
from hermes.learning.thresholds import propose_threshold_adaptation, run_walk_forward_validation


class TestThresholdAdapter(unittest.TestCase):
    def _trade(self, idx: int, outcome: str = "win", pnl: float = 5.0, regime: str = "trend_up") -> dict:
        return {
            "timestamp": idx,
            "confidence": 0.85 if outcome == "win" else 0.45,
            "regime": regime,
            "outcome": outcome,
            "net_pnl": pnl,
        }

    def test_threshold_adaptation_is_bounded(self) -> None:
        trades = [self._trade(i, outcome="loss", pnl=-3.0, regime="chop") for i in range(120)]
        result = propose_threshold_adaptation(
            trades,
            current_thresholds={"min_confidence": 0.9},
            min_trades_per_combination=50,
            isolated_test_mode=True,
            safety_hardening_active=False,
        )

        self.assertGreaterEqual(result["proposed_thresholds"]["min_confidence"], 0.4)
        self.assertLessEqual(result["proposed_thresholds"]["min_confidence"], 0.9)

    def test_threshold_adaptation_does_not_override_risk_guardrails(self) -> None:
        trades = [self._trade(i, outcome="loss", pnl=-3.0, regime="chop") for i in range(120)]
        result = propose_threshold_adaptation(
            trades,
            current_thresholds={"min_confidence": 0.6},
            min_trades_per_combination=50,
            isolated_test_mode=True,
            safety_hardening_active=False,
        )

        self.assertTrue(result["risk_guardrails_unchanged"])

    def test_walk_forward_windows_do_not_overlap_and_no_future_data(self) -> None:
        trades = [self._trade(i, outcome="win", pnl=5.0) for i in range(60)]
        report = run_walk_forward_validation(trades, train_size=20, test_size=10)

        self.assertGreater(len(report["windows"]), 0)
        for window in report["windows"]:
            self.assertLess(window["train_end"], window["test_start"])

    def test_rolling_win_rate_and_edge_decay_trigger(self) -> None:
        trades = []
        for i in range(40):
            outcome = "loss" if i < 36 else "win"
            pnl = -2.0 if outcome == "loss" else 1.0
            trades.append(self._trade(i, outcome=outcome, pnl=pnl))

        result = monitor_edge_decay(trades, current_min_confidence=0.6, existing_alert=False)

        self.assertEqual(result["rolling_win_rates"], [0.0, 0.2])
        self.assertTrue(result["edge_decay_alert"])
        self.assertEqual(result["proposed_min_confidence"], 0.65)

    def test_edge_decay_recovery_requires_valid_conditions(self) -> None:
        trades = [self._trade(i, outcome="win", pnl=1.0) for i in range(30)]

        result = monitor_edge_decay(trades, current_min_confidence=0.65, existing_alert=True)

        self.assertFalse(result["edge_decay_alert"])
        self.assertIn("recovery", " ".join(result["logs"]).lower())
