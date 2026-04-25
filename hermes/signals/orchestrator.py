"""Signal orchestrator consistency logic for Prompt 1 Step 2."""

from __future__ import annotations

from hermes.signals.normalization import normalize_signals


def _derive_label(sequence_value: float, amd_value: float, combined_value: float) -> str:
    """Derive a deterministic label from normalized values only."""
    agreement = 1.0 - abs(sequence_value - amd_value)

    if combined_value >= 0.67 and agreement >= 0.50:
        return "bullish"
    if combined_value <= 0.33 and agreement >= 0.50:
        return "bearish"
    return "neutral"


def orchestrate_signals(input_signals: dict) -> dict:
    """Return consistent orchestrated outputs based on normalized signals.

    Output keys:
    - sequence_value
    - amd_value
    - combined_value
    - agreement
    - label
    """
    normalized = normalize_signals(input_signals)

    label = _derive_label(
        normalized["sequence_value"],
        normalized["amd_value"],
        normalized["combined_value"],
    )

    return {
        "sequence_value": normalized["sequence_value"],
        "amd_value": normalized["amd_value"],
        "combined_value": normalized["combined_value"],
        "agreement": normalized["agreement"],
        "label": label,
    }
