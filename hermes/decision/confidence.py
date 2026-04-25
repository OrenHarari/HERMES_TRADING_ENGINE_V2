"""Confidence scoring for Stage 5A."""


_REGIME_WEIGHTS = {
    "trend_up": 1.0,
    "trend_down": 0.8,
    "chop": 0.3,
    "high_volatility": 0.4,
    "low_volatility": 0.7,
}


def _clamp_01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


def compute_confidence(signal: dict) -> float:
    """Compute a deterministic confidence score clamped to [0, 1]."""
    combined_value = float(signal.get("combined_value", 0.0))
    agreement = float(signal.get("agreement", 0.0))
    momentum_score = float(signal.get("momentum_score", 0.0))
    volatility_score = float(signal.get("volatility_score", 0.0))
    regime = str(signal.get("regime", ""))

    regime_weight = _REGIME_WEIGHTS.get(regime, 0.0)

    confidence = (
        0.25 * combined_value
        + 0.20 * agreement
        + 0.20 * momentum_score
        + 0.15 * (1.0 - volatility_score)
        + 0.20 * regime_weight
    )

    return _clamp_01(confidence)
