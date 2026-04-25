"""Stage 5A trade eligibility gate."""

from typing import Mapping

from hermes.trading.confidence import compute_confidence


def check_trade_allowed(signal: Mapping[str, object], config: Mapping[str, object]) -> dict[str, object]:
    """Return whether trade is allowed and the first blocking reason if denied."""
    confidence = compute_confidence(signal)
    min_confidence = float(config["min_confidence"])
    min_agreement = float(config["min_agreement"])
    allow_chop = bool(config["allow_chop"])
    max_volatility = float(config["max_volatility"])

    agreement = float(signal["agreement"])
    regime = str(signal["regime"])
    volatility_score = float(signal["volatility_score"])

    if confidence < min_confidence:
        return {"trade_allowed": False, "reason": "low_confidence"}
    if agreement < min_agreement:
        return {"trade_allowed": False, "reason": "low_agreement"}
    if regime == "chop" and not allow_chop:
        return {"trade_allowed": False, "reason": "chop_blocked"}
    if volatility_score > max_volatility:
        return {"trade_allowed": False, "reason": "volatility_too_high"}

    return {"trade_allowed": True, "reason": "allowed"}
