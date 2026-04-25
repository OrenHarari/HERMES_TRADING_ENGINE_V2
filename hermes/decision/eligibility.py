"""Trade eligibility checks for Stage 5A."""


def check_trade_allowed(signal: dict, config: dict) -> dict:
    """Return deterministic trade-eligibility decision and reason."""
    confidence = float(signal.get("confidence", 0.0))
    agreement = float(signal.get("agreement", 0.0))
    regime = str(signal.get("regime", ""))
    volatility_score = float(signal.get("volatility_score", 0.0))

    min_confidence = float(config.get("min_confidence", 0.6))
    min_agreement = float(config.get("min_agreement", 0.5))
    allow_chop = bool(config.get("allow_chop", False))
    max_volatility = float(config.get("max_volatility", 0.8))

    if confidence < min_confidence:
        return {"trade_allowed": False, "reason": "low_confidence"}

    if agreement < min_agreement:
        return {"trade_allowed": False, "reason": "low_agreement"}

    if regime == "chop" and not allow_chop:
        return {"trade_allowed": False, "reason": "chop_blocked"}

    if volatility_score > max_volatility:
        return {"trade_allowed": False, "reason": "volatility_too_high"}

    return {"trade_allowed": True, "reason": "allowed"}
