"""Signal normalization logic for Prompt 1 Step 1."""

from __future__ import annotations


_REQUIRED_KEYS: tuple[str, str, str] = ("sequence_value", "amd_value", "combined_value")


def _validate_unit_interval(value: object, field_name: str) -> float:
    """Validate numeric unit-interval values without implicit casting."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be a numeric value in [0, 1].")

    normalized_value = float(value)
    if normalized_value < 0.0 or normalized_value > 1.0:
        raise ValueError(f"{field_name} must be within [0, 1].")

    return normalized_value


def normalize_signals(input_signals: dict) -> dict:
    """Normalize and validate core signal values.

    Returns the validated values and an agreement score:
    agreement = 1 - abs(sequence_value - amd_value)
    """
    if not isinstance(input_signals, dict):
        raise ValueError("input_signals must be a dictionary.")

    missing_keys = [key for key in _REQUIRED_KEYS if key not in input_signals]
    if missing_keys:
        missing = ", ".join(missing_keys)
        raise KeyError(f"Missing required signal key(s): {missing}")

    sequence_value = _validate_unit_interval(input_signals["sequence_value"], "sequence_value")
    amd_value = _validate_unit_interval(input_signals["amd_value"], "amd_value")
    combined_value = _validate_unit_interval(input_signals["combined_value"], "combined_value")

    agreement = 1.0 - abs(sequence_value - amd_value)

    return {
        "sequence_value": sequence_value,
        "amd_value": amd_value,
        "combined_value": combined_value,
        "agreement": agreement,
    }
