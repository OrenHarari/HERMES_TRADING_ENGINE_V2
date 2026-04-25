"""Trade memory storage helpers for completed trades."""

import json
import os

REQUIRED_FIELDS = (
    "timestamp",
    "date",
    "hour",
    "sequence_value",
    "amd_value",
    "combined_value",
    "agreement",
    "confidence",
    "regime",
    "momentum_score",
    "volatility_score",
    "outcome",
    "pnl",
    "entry_price",
    "exit_price",
)

VALID_OUTCOMES = {"win", "loss", "breakeven"}

NUMERIC_FIELDS = (
    "hour",
    "sequence_value",
    "amd_value",
    "combined_value",
    "agreement",
    "confidence",
    "momentum_score",
    "volatility_score",
    "pnl",
    "entry_price",
    "exit_price",
)


def _is_valid_numeric(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validate_completed_trade(trade: dict) -> None:
    """Validate that a completed trade has required fields and valid values."""
    for field in REQUIRED_FIELDS:
        if field not in trade:
            raise ValueError("Missing required field: {0}".format(field))

    outcome = trade["outcome"]
    if outcome not in VALID_OUTCOMES:
        raise ValueError("Invalid outcome: {0}".format(outcome))

    for field in NUMERIC_FIELDS:
        if not _is_valid_numeric(trade[field]):
            raise ValueError("Non-numeric field: {0}".format(field))


def load_trade_memory(path: str) -> list:
    """Load completed trades from JSON memory file."""
    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as file_obj:
            data = json.load(file_obj)
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid JSON in trade memory") from exc

    if not isinstance(data, list):
        raise ValueError("Trade memory JSON must be a list")

    return data


def append_completed_trade(path: str, trade: dict) -> None:
    """Append one validated completed trade to JSON memory file."""
    validate_completed_trade(trade)

    existing_trades = load_trade_memory(path)
    existing_trades.append(trade)

    with open(path, "w", encoding="utf-8") as file_obj:
        json.dump(existing_trades, file_obj, ensure_ascii=True, indent=2)
