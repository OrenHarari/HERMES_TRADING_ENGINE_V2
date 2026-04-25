"""Trade memory storage for Prompt 1 Step 6."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path


_REQUIRED_ENTRY_FIELDS: tuple[str, ...] = (
    "timestamp",
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

_VALID_OUTCOMES: tuple[str, str, str] = ("win", "loss", "breakeven")


def _validate_numeric(value: object, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be numeric.")
    return float(value)


def load_trade_memory(path: Path | str) -> list[dict]:
    """Load completed trade memory from JSON file."""
    file_path = Path(path)
    if not file_path.exists():
        return []

    content = json.loads(file_path.read_text(encoding="utf-8"))
    if not isinstance(content, list):
        raise ValueError("Trade memory file must contain a JSON list.")

    return content


def log_completed_trade(path: Path | str, trade: dict) -> dict:
    """Append an immutable completed trade record to JSON storage."""
    if not isinstance(trade, dict):
        raise ValueError("trade must be a dictionary.")

    status = trade.get("status", "completed")
    if status != "completed":
        raise ValueError("Cannot log incomplete trade as completed.")

    missing = [field for field in _REQUIRED_ENTRY_FIELDS if field not in trade]
    if missing:
        raise ValueError(f"Trade missing required field(s): {', '.join(missing)}")

    timestamp_value = _validate_numeric(trade["timestamp"], "timestamp")
    dt = datetime.fromtimestamp(timestamp_value, tz=UTC)

    outcome = trade["outcome"]
    if not isinstance(outcome, str) or outcome not in _VALID_OUTCOMES:
        raise ValueError("outcome must be one of win, loss, breakeven.")

    record = {
        "timestamp": timestamp_value,
        "date": dt.date().isoformat(),
        "hour": dt.hour,
        "sequence_value": _validate_numeric(trade["sequence_value"], "sequence_value"),
        "amd_value": _validate_numeric(trade["amd_value"], "amd_value"),
        "combined_value": _validate_numeric(trade["combined_value"], "combined_value"),
        "agreement": _validate_numeric(trade["agreement"], "agreement"),
        "confidence": _validate_numeric(trade["confidence"], "confidence"),
        "regime": str(trade["regime"]),
        "momentum_score": _validate_numeric(trade["momentum_score"], "momentum_score"),
        "volatility_score": _validate_numeric(trade["volatility_score"], "volatility_score"),
        "outcome": outcome,
        "pnl": _validate_numeric(trade["pnl"], "pnl"),
        "entry_price": _validate_numeric(trade["entry_price"], "entry_price"),
        "exit_price": _validate_numeric(trade["exit_price"], "exit_price"),
        "notes": str(trade.get("notes", "")),
    }

    if "net_pnl" in trade and trade["net_pnl"] is not None:
        record["net_pnl"] = _validate_numeric(trade["net_pnl"], "net_pnl")
    else:
        record["net_pnl"] = record["pnl"]

    file_path = Path(path)
    existing = load_trade_memory(file_path)
    existing.append(record)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(existing, indent=2, sort_keys=True), encoding="utf-8")

    return record
