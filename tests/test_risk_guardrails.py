import unittest

from hermes.risk.guardrails import evaluate_risk_guardrails


class TestRiskGuardrails(unittest.TestCase):
    def test_allows_when_limits_not_reached(self) -> None:
        result = evaluate_risk_guardrails(
            state={
                "trades_today": 1,
                "daily_pnl": -20.0,
                "consecutive_losses": 1,
                "last_trade_ts": 100,
                "current_ts": 500,
            },
            config={
                "max_trades_per_day": 5,
                "max_daily_loss": 200.0,
                "max_consecutive_losses": 3,
                "cooldown_between_trades": 60,
                "base_position_size": 1.0,
                "max_position_size": 2.0,
            },
            confidence_score=0.5,
        )

        self.assertTrue(result["allowed"])
        self.assertGreater(result["position_size"], 0.0)

    def test_blocks_max_trades_per_day(self) -> None:
        result = evaluate_risk_guardrails(
            state={
                "trades_today": 5,
                "daily_pnl": 0.0,
                "consecutive_losses": 0,
                "last_trade_ts": 0,
                "current_ts": 1000,
            },
            config={
                "max_trades_per_day": 5,
                "max_daily_loss": 200.0,
                "max_consecutive_losses": 3,
                "cooldown_between_trades": 60,
                "base_position_size": 1.0,
                "max_position_size": 2.0,
            },
            confidence_score=0.9,
        )

        self.assertFalse(result["allowed"])
        self.assertIn("max_trades_per_day", result["reason"])

    def test_blocks_max_daily_loss(self) -> None:
        result = evaluate_risk_guardrails(
            state={
                "trades_today": 1,
                "daily_pnl": -250.0,
                "consecutive_losses": 0,
                "last_trade_ts": 0,
                "current_ts": 1000,
            },
            config={
                "max_trades_per_day": 5,
                "max_daily_loss": 200.0,
                "max_consecutive_losses": 3,
                "cooldown_between_trades": 60,
                "base_position_size": 1.0,
                "max_position_size": 2.0,
            },
            confidence_score=0.9,
        )

        self.assertFalse(result["allowed"])
        self.assertIn("max_daily_loss", result["reason"])

    def test_blocks_consecutive_losses(self) -> None:
        result = evaluate_risk_guardrails(
            state={
                "trades_today": 1,
                "daily_pnl": -20.0,
                "consecutive_losses": 3,
                "last_trade_ts": 0,
                "current_ts": 1000,
            },
            config={
                "max_trades_per_day": 5,
                "max_daily_loss": 200.0,
                "max_consecutive_losses": 3,
                "cooldown_between_trades": 60,
                "base_position_size": 1.0,
                "max_position_size": 2.0,
            },
            confidence_score=0.9,
        )

        self.assertFalse(result["allowed"])
        self.assertIn("max_consecutive_losses", result["reason"])

    def test_blocks_cooldown_between_trades(self) -> None:
        result = evaluate_risk_guardrails(
            state={
                "trades_today": 1,
                "daily_pnl": -20.0,
                "consecutive_losses": 1,
                "last_trade_ts": 980,
                "current_ts": 1000,
            },
            config={
                "max_trades_per_day": 5,
                "max_daily_loss": 200.0,
                "max_consecutive_losses": 3,
                "cooldown_between_trades": 60,
                "base_position_size": 1.0,
                "max_position_size": 2.0,
            },
            confidence_score=0.9,
        )

        self.assertFalse(result["allowed"])
        self.assertIn("cooldown_between_trades", result["reason"])

    def test_recent_wins_do_not_increase_risk_by_themselves(self) -> None:
        base_state = {
            "trades_today": 1,
            "daily_pnl": 50.0,
            "consecutive_losses": 0,
            "last_trade_ts": 100,
            "current_ts": 500,
        }
        config = {
            "max_trades_per_day": 5,
            "max_daily_loss": 200.0,
            "max_consecutive_losses": 3,
            "cooldown_between_trades": 60,
            "base_position_size": 1.0,
            "max_position_size": 2.0,
        }

        without_wins = evaluate_risk_guardrails(base_state, config, confidence_score=0.7)
        with_wins = evaluate_risk_guardrails(
            {**base_state, "recent_wins": 10}, config, confidence_score=0.7
        )

        self.assertEqual(without_wins["position_size"], with_wins["position_size"])
