"""Signal normalization for Stage 1."""

from __future__ import annotations

REQUIRED_KEYS = ("sequence_value", "amd_value", "combined_value")


def _validate_signal_value(key: str, value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{key} must be an int or float in [0, 1], bool is not allowed")

    value_float = float(value)

    if value_float < 0.0 or value_float > 1.0:
        raise ValueError(f"{key} must be within [0, 1]")

    return value_float


def normalize_signals(input_signals: dict) -> dict:
    """Validate and normalize Stage 1 signal inputs.

    Args:
        input_signals: Mapping containing sequence_value, amd_value, combined_value.

    Returns:
        Dictionary with normalized float values and agreement score.
    """
    for key in REQUIRED_KEYS:
        if key not in input_signals:
            raise KeyError(f"Missing required key: {key}")

    sequence_value = _validate_signal_value("sequence_value", input_signals["sequence_value"])
    amd_value = _validate_signal_value("amd_value", input_signals["amd_value"])
    combined_value = _validate_signal_value("combined_value", input_signals["combined_value"])

    agreement = 1.0 - abs(sequence_value - amd_value)

    return {
        "sequence_value": sequence_value,
        "amd_value": amd_value,
        "combined_value": combined_value,
        "agreement": agreement,
    }
