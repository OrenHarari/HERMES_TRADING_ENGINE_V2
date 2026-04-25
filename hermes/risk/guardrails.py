"""Risk guardrails for Stage 5B."""


def check_risk_limits(state: dict, config: dict) -> dict:
    """Evaluate deterministic risk limits and return allow/block decision."""
    if state["trades_today"] >= config["max_trades_per_day"]:
        return {"risk_allowed": False, "reason": "max_trades_reached"}

    if state["daily_loss"] >= config["max_daily_loss"]:
        return {"risk_allowed": False, "reason": "daily_loss_limit"}

    if state["consecutive_losses"] >= config["max_consecutive_losses"]:
        return {"risk_allowed": False, "reason": "loss_streak_limit"}

    if (state["current_time"] - state["last_trade_timestamp"]) < config["cooldown_seconds"]:
        return {"risk_allowed": False, "reason": "cooldown_active"}

    return {"risk_allowed": True, "reason": "allowed"}
