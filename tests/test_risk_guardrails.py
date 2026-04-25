"""Unit tests for Stage 5B risk guardrails."""

import unittest

from hermes.risk.guardrails import check_risk_limits


class TestRiskGuardrails(unittest.TestCase):
    def test_allowed_case(self) -> None:
        state = {
            "trades_today": 2,
            "daily_loss": 50.0,
            "consecutive_losses": 1,
            "last_trade_timestamp": 1_000,
            "current_time": 1_500,
        }
        config = {
            "max_trades_per_day": 5,
            "max_daily_loss": 100.0,
            "max_consecutive_losses": 3,
            "cooldown_seconds": 300,
        }

        result = check_risk_limits(state, config)

        self.assertEqual({"risk_allowed": True, "reason": "allowed"}, result)

    def test_blocked_by_max_trades(self) -> None:
        state = {
            "trades_today": 5,
            "daily_loss": 0.0,
            "consecutive_losses": 0,
            "last_trade_timestamp": 1_000,
            "current_time": 2_000,
        }
        config = {
            "max_trades_per_day": 5,
            "max_daily_loss": 100.0,
            "max_consecutive_losses": 3,
            "cooldown_seconds": 300,
        }

        result = check_risk_limits(state, config)

        self.assertEqual({"risk_allowed": False, "reason": "max_trades_reached"}, result)

    def test_blocked_by_daily_loss(self) -> None:
        state = {
            "trades_today": 1,
            "daily_loss": 100.0,
            "consecutive_losses": 0,
            "last_trade_timestamp": 1_000,
            "current_time": 2_000,
        }
        config = {
            "max_trades_per_day": 5,
            "max_daily_loss": 100.0,
            "max_consecutive_losses": 3,
            "cooldown_seconds": 300,
        }

        result = check_risk_limits(state, config)

        self.assertEqual({"risk_allowed": False, "reason": "daily_loss_limit"}, result)

    def test_blocked_by_consecutive_losses(self) -> None:
        state = {
            "trades_today": 1,
            "daily_loss": 10.0,
            "consecutive_losses": 3,
            "last_trade_timestamp": 1_000,
            "current_time": 2_000,
        }
        config = {
            "max_trades_per_day": 5,
            "max_daily_loss": 100.0,
            "max_consecutive_losses": 3,
            "cooldown_seconds": 300,
        }

        result = check_risk_limits(state, config)

        self.assertEqual({"risk_allowed": False, "reason": "loss_streak_limit"}, result)

    def test_blocked_by_cooldown(self) -> None:
        state = {
            "trades_today": 1,
            "daily_loss": 10.0,
            "consecutive_losses": 1,
            "last_trade_timestamp": 1_000,
            "current_time": 1_299,
        }
        config = {
            "max_trades_per_day": 5,
            "max_daily_loss": 100.0,
            "max_consecutive_losses": 3,
            "cooldown_seconds": 300,
        }

        result = check_risk_limits(state, config)

        self.assertEqual({"risk_allowed": False, "reason": "cooldown_active"}, result)

    def test_deterministic_output(self) -> None:
        state = {
            "trades_today": 4,
            "daily_loss": 20.0,
            "consecutive_losses": 2,
            "last_trade_timestamp": 1_000,
            "current_time": 1_500,
        }
        config = {
            "max_trades_per_day": 5,
            "max_daily_loss": 100.0,
            "max_consecutive_losses": 3,
            "cooldown_seconds": 300,
        }

        first = check_risk_limits(state, config)
        second = check_risk_limits(state, config)

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
