"""Unit tests for Stage 5B risk guardrails."""

import unittest

from hermes.risk.guardrails import check_risk_limits


class TestRiskGuardrails(unittest.TestCase):
    def setUp(self) -> None:
        self.base_state = {
            "trades_today": 2,
            "daily_loss": 25.0,
            "consecutive_losses": 1,
            "last_trade_timestamp": 1_000,
            "current_time": 1_400,
        }
        self.base_config = {
            "max_trades_per_day": 5,
            "max_daily_loss": 100.0,
            "max_consecutive_losses": 3,
            "cooldown_seconds": 300,
        }

    def test_allowed_case(self) -> None:
        result = check_risk_limits(self.base_state, self.base_config)
        self.assertEqual(result, {"risk_allowed": True, "reason": "allowed"})

    def test_blocked_by_max_trades(self) -> None:
        state = dict(self.base_state)
        state["trades_today"] = 5

        result = check_risk_limits(state, self.base_config)
        self.assertEqual(result, {"risk_allowed": False, "reason": "max_trades_reached"})

    def test_blocked_by_daily_loss(self) -> None:
        state = dict(self.base_state)
        state["daily_loss"] = 100.0

        result = check_risk_limits(state, self.base_config)
        self.assertEqual(result, {"risk_allowed": False, "reason": "daily_loss_limit"})

    def test_blocked_by_consecutive_losses(self) -> None:
        state = dict(self.base_state)
        state["consecutive_losses"] = 3

        result = check_risk_limits(state, self.base_config)
        self.assertEqual(result, {"risk_allowed": False, "reason": "loss_streak_limit"})

    def test_blocked_by_cooldown(self) -> None:
        state = dict(self.base_state)
        state["last_trade_timestamp"] = 1_250
        state["current_time"] = 1_500

        result = check_risk_limits(state, self.base_config)
        self.assertEqual(result, {"risk_allowed": False, "reason": "cooldown_active"})

    def test_deterministic_output(self) -> None:
        first = check_risk_limits(self.base_state, self.base_config)
        second = check_risk_limits(self.base_state, self.base_config)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
