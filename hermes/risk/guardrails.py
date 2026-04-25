"""Core deterministic risk guardrails for Prompt 1 Step 5."""

from __future__ import annotations


def _validate_number(value: object, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be numeric.")
    return float(value)


def evaluate_risk_guardrails(state: dict, config: dict, confidence_score: float) -> dict:
    """Evaluate core risk limits and return permission + reason + position size."""
    if not isinstance(state, dict) or not isinstance(config, dict):
        raise ValueError("state and config must be dictionaries.")

    confidence = _validate_number(confidence_score, "confidence_score")
    if confidence < 0.0 or confidence > 1.0:
        raise ValueError("confidence_score must be within [0, 1].")

    required_state = ("trades_today", "daily_pnl", "consecutive_losses", "last_trade_ts", "current_ts")
    required_config = (
        "max_trades_per_day",
        "max_daily_loss",
        "max_consecutive_losses",
        "cooldown_between_trades",
        "base_position_size",
        "max_position_size",
    )

    missing_state = [key for key in required_state if key not in state]
    missing_config = [key for key in required_config if key not in config]
    if missing_state or missing_config:
        raise ValueError(
            "missing required keys: "
            + ", ".join([*(f"state.{k}" for k in missing_state), *(f"config.{k}" for k in missing_config)])
        )

    trades_today = int(_validate_number(state["trades_today"], "state.trades_today"))
    daily_pnl = _validate_number(state["daily_pnl"], "state.daily_pnl")
    consecutive_losses = int(_validate_number(state["consecutive_losses"], "state.consecutive_losses"))
    last_trade_ts = _validate_number(state["last_trade_ts"], "state.last_trade_ts")
    current_ts = _validate_number(state["current_ts"], "state.current_ts")

    max_trades_per_day = int(_validate_number(config["max_trades_per_day"], "config.max_trades_per_day"))
    max_daily_loss = _validate_number(config["max_daily_loss"], "config.max_daily_loss")
    max_consecutive_losses = int(
        _validate_number(config["max_consecutive_losses"], "config.max_consecutive_losses")
    )
    cooldown_between_trades = _validate_number(
        config["cooldown_between_trades"], "config.cooldown_between_trades"
    )
    base_position_size = _validate_number(config["base_position_size"], "config.base_position_size")
    max_position_size = _validate_number(config["max_position_size"], "config.max_position_size")

    if trades_today >= max_trades_per_day:
        return {"allowed": False, "reason": "Blocked: max_trades_per_day reached.", "position_size": 0.0}

    if daily_pnl <= -abs(max_daily_loss):
        return {"allowed": False, "reason": "Blocked: max_daily_loss reached.", "position_size": 0.0}

    if consecutive_losses >= max_consecutive_losses:
        return {
            "allowed": False,
            "reason": "Blocked: max_consecutive_losses reached.",
            "position_size": 0.0,
        }

    if current_ts - last_trade_ts < cooldown_between_trades:
        return {
            "allowed": False,
            "reason": "Blocked: cooldown_between_trades not satisfied.",
            "position_size": 0.0,
        }

    position_size = base_position_size * confidence
    if position_size > max_position_size:
        position_size = max_position_size
    if position_size < 0.0:
        position_size = 0.0

    return {"allowed": True, "reason": "", "position_size": position_size}
