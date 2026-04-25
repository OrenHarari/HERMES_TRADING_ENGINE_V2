"""Stage 5A confidence score computation."""

from typing import Mapping


_REGIME_WEIGHTS = {
    "trend_up": 1.0,
    "trend_down": 0.8,
    "chop": 0.3,
    "high_volatility": 0.4,
    "low_volatility": 0.7,
}


def _clamp(value: float, lower: float, upper: float) -> float:
    if value < lower:
        return lower
    if value > upper:
        return upper
    return value


def compute_confidence(signal: Mapping[str, object]) -> float:
    """Compute deterministic confidence score in the [0.0, 1.0] range."""
    combined_value = float(signal["combined_value"])
    agreement = float(signal["agreement"])
    momentum_score = float(signal["momentum_score"])
    volatility_score = float(signal["volatility_score"])
    regime = str(signal["regime"])

    regime_weight = _REGIME_WEIGHTS.get(regime, 0.0)

    confidence = (
        0.25 * combined_value
        + 0.20 * agreement
        + 0.20 * momentum_score
        + 0.15 * (1.0 - volatility_score)
        + 0.20 * regime_weight
    )
    return _clamp(confidence, 0.0, 1.0)
