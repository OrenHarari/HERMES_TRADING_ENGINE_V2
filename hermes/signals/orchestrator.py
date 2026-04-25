"""Signal orchestration for Stage 2."""

from hermes.signals.normalization import normalize_signals


def orchestrate_signals(input_signals: dict) -> dict:
    """Normalize signals and assign a confidence label."""
    normalized = normalize_signals(input_signals)

    sequence_value = normalized["sequence_value"]
    amd_value = normalized["amd_value"]
    combined_value = normalized["combined_value"]
    agreement = normalized["agreement"]

    if combined_value >= 0.7 and agreement >= 0.7:
        label = "strong"
    elif combined_value >= 0.5:
        label = "medium"
    else:
        label = "weak"

    return {
        "sequence_value": sequence_value,
        "amd_value": amd_value,
        "combined_value": combined_value,
        "agreement": agreement,
        "label": label,
    }
