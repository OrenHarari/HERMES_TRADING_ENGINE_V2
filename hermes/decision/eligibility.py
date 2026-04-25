"""Trade eligibility gate for Prompt 1 Step 5."""

from __future__ import annotations


_REQUIRED_SIGNAL_FIELDS: tuple[str, str, str] = ("agreement", "volatility_score", "regime")


def _validate_unit_interval(value: object, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be numeric and within [0, 1].")

    numeric = float(value)
    if numeric < 0.0 or numeric > 1.0:
        raise ValueError(f"{field_name} must be within [0, 1].")
    return numeric


def evaluate_trade_eligibility(
    signal_data: dict,
    confidence_score: float,
    min_confidence: float,
    min_agreement: float,
    allow_chop: bool,
    volatility_bounds: tuple[float, float],
    risk_result: dict,
    active_block_condition: bool,
) -> dict:
    """Evaluate whether a trade is allowed based on confidence, signals, and risk."""
    if not isinstance(signal_data, dict):
        return {"trade_allowed": False, "reason_if_blocked": "Blocked: missing required signal data."}

    missing = [field for field in _REQUIRED_SIGNAL_FIELDS if field not in signal_data]
    if missing:
        return {
            "trade_allowed": False,
            "reason_if_blocked": f"Blocked: missing required signal data: {', '.join(missing)}.",
        }

    if not isinstance(risk_result, dict) or "allowed" not in risk_result or "reason" not in risk_result:
        return {"trade_allowed": False, "reason_if_blocked": "Blocked: invalid risk guardrail result."}

    confidence = _validate_unit_interval(confidence_score, "confidence_score")
    min_conf = _validate_unit_interval(min_confidence, "min_confidence")
    min_agree = _validate_unit_interval(min_agreement, "min_agreement")

    agreement = _validate_unit_interval(signal_data["agreement"], "agreement")
    volatility_score = _validate_unit_interval(signal_data["volatility_score"], "volatility_score")
    regime = signal_data["regime"]

    if not isinstance(regime, str):
        return {"trade_allowed": False, "reason_if_blocked": "Blocked: regime must be a string."}

    min_volatility, max_volatility = volatility_bounds
    min_volatility_value = _validate_unit_interval(min_volatility, "volatility_bounds.min")
    max_volatility_value = _validate_unit_interval(max_volatility, "volatility_bounds.max")

    if confidence < min_conf:
        return {"trade_allowed": False, "reason_if_blocked": "Blocked: confidence_score below min_confidence."}

    if agreement < min_agree:
        return {"trade_allowed": False, "reason_if_blocked": "Blocked: agreement below min_agreement."}

    if regime == "chop" and not allow_chop:
        return {"trade_allowed": False, "reason_if_blocked": "Blocked: regime is chop and allow_chop is false."}

    if volatility_score < min_volatility_value or volatility_score > max_volatility_value:
        return {
            "trade_allowed": False,
            "reason_if_blocked": "Blocked: volatility_score outside safe bounds.",
        }

    if not risk_result["allowed"]:
        reason = risk_result["reason"] or "unknown risk constraint"
        return {"trade_allowed": False, "reason_if_blocked": f"Blocked: risk guardrail failed ({reason})."}

    if active_block_condition:
        return {"trade_allowed": False, "reason_if_blocked": "Blocked: active block condition present."}

    return {"trade_allowed": True, "reason_if_blocked": ""}
