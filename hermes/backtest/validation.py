"""Backtest validation gate (Stage 5C)."""


def validate_backtest(payload: dict) -> dict:
    """Validate backtest integrity checks with deterministic blocking order."""
    if payload["lookahead_bias_detected"]:
        return {
            "validation_passed": False,
            "reason": "lookahead_bias_detected",
        }

    if payload["data_leakage_detected"]:
        return {
            "validation_passed": False,
            "reason": "data_leakage_detected",
        }

    if payload["future_data_used"]:
        return {
            "validation_passed": False,
            "reason": "future_data_used",
        }

    if not payload["replay_deterministic"]:
        return {
            "validation_passed": False,
            "reason": "replay_not_deterministic",
        }

    if payload["outcome_used_in_signal_generation"]:
        return {
            "validation_passed": False,
            "reason": "outcome_used_in_signal_generation",
        }

    return {
        "validation_passed": True,
        "reason": "passed",
    }
