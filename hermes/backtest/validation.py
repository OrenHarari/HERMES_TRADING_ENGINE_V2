"""Backtest validation gate for Prompt 1 Step 5."""

from __future__ import annotations


_REQUIRED_FIELDS: tuple[str, ...] = (
    "lookahead_bias",
    "data_leakage",
    "future_data_used",
    "outcome_used_in_signals",
    "future_candles_visible",
    "same_input_same_output",
    "replay_outputs",
)


def _fail(reason: str) -> dict:
    return {"validation_passed": False, "reason": reason}


def validate_backtest(payload: dict) -> dict:
    """Validate that backtest execution is deterministic and leakage-free."""
    if not isinstance(payload, dict):
        return _fail("Validation failed: payload must be a dictionary.")

    missing = [field for field in _REQUIRED_FIELDS if field not in payload]
    if missing:
        return _fail(f"Validation failed: missing required field(s): {', '.join(missing)}")

    if payload["lookahead_bias"]:
        return _fail("Validation failed: lookahead bias detected.")

    if payload["data_leakage"]:
        return _fail("Validation failed: data leakage detected.")

    if payload["future_data_used"] or payload["future_candles_visible"]:
        return _fail("Validation failed: future data visibility detected in signal logic.")

    if payload["outcome_used_in_signals"]:
        return _fail("Validation failed: trade outcome used inside signal generation.")

    if not payload["same_input_same_output"]:
        return _fail("Validation failed: same input did not produce same output.")

    replay_outputs = payload["replay_outputs"]
    if not isinstance(replay_outputs, list) or len(replay_outputs) == 0:
        return _fail("Validation failed: replay_outputs must be a non-empty list.")

    baseline = replay_outputs[0]
    for replay in replay_outputs[1:]:
        if replay != baseline:
            return _fail("Validation failed: replay is not deterministic.")

    return {"validation_passed": True, "reason": ""}
