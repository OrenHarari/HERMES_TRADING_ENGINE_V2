"""Deterministic confidence model for Prompt 1 Step 5."""

from __future__ import annotations


_REQUIRED_NUMERIC_FIELDS: tuple[str, ...] = (
    "sequence_value",
    "amd_value",
    "combined_value",
    "agreement",
    "momentum_score",
    "volatility_score",
)

_REGIME_WEIGHTS: dict[str, float] = {
    "trend_up": 1.00,
    "trend_down": 0.95,
    "chop": 0.70,
    "high_volatility": 0.80,
    "low_volatility": 0.90,
}


def _validate_unit_interval(value: object, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be numeric and within [0, 1].")

    numeric = float(value)
    if numeric < 0.0 or numeric > 1.0:
        raise ValueError(f"{field_name} must be within [0, 1].")

    return numeric


def compute_confidence(features: dict) -> dict:
    """Compute an explainable confidence score in [0,1] from normalized inputs."""
    if not isinstance(features, dict):
        raise ValueError("features must be a dictionary.")

    missing = [field for field in _REQUIRED_NUMERIC_FIELDS if field not in features]
    if "regime" not in features:
        missing.append("regime")
    if missing:
        raise ValueError(f"missing required field(s): {', '.join(missing)}")

    numeric_fields = {
        field: _validate_unit_interval(features[field], field) for field in _REQUIRED_NUMERIC_FIELDS
    }

    regime = features["regime"]
    if not isinstance(regime, str) or regime not in _REGIME_WEIGHTS:
        raise ValueError("regime must be one of trend_up, trend_down, chop, high_volatility, low_volatility.")

    regime_weight = _REGIME_WEIGHTS[regime]

    base_score = (
        0.20 * numeric_fields["sequence_value"]
        + 0.20 * numeric_fields["amd_value"]
        + 0.20 * numeric_fields["combined_value"]
        + 0.20 * numeric_fields["agreement"]
        + 0.15 * numeric_fields["momentum_score"]
        + 0.05 * (1.0 - numeric_fields["volatility_score"])
    )

    confidence_score = base_score * regime_weight
    if confidence_score < 0.0:
        confidence_score = 0.0
    if confidence_score > 1.0:
        confidence_score = 1.0

    return {
        "confidence_score": confidence_score,
        "regime_weight": regime_weight,
        "components": {
            **numeric_fields,
            "volatility_safety": 1.0 - numeric_fields["volatility_score"],
        },
    }
