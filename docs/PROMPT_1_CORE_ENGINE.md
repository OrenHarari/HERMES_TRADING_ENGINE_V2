# Prompt 1: Core Deterministic Learning Engine

This document defines the implementation contract for Prompt 1.

## Objective

Build the core deterministic learning trading engine in incremental, test-first steps.

## Process Requirements

- Implement only the explicitly requested step.
- Do not implement future steps early.
- Add or update tests before implementation.
- Run the full test suite after every change.
- Preserve existing behavior unless a step explicitly requires behavior changes.
- Keep modules pure and deterministic where possible.

## Global Constraints

- No pandas.
- No numpy.
- No `.values` usage.
- No external dependencies unless explicitly approved.
- No randomness for core decision logic.
- No hidden mutable state.
- No live broker/exchange/wallet execution.
- No profitability claims.

## Step 1 — Signal Normalization

### Scope

- Implement `hermes/signals/normalization.py`.
- Add real unit tests in `tests/test_signal_normalization.py`.
- Keep behavior deterministic and explainable.

### Required Inputs

`normalize_signals(input_signals: dict) -> dict` must require:

- `sequence_value`
- `amd_value`
- `combined_value`

Each value must be numeric and in the inclusive range `[0, 1]`.

### Validation Rules

- Reject missing required keys with a clear exception.
- Reject values below `0`.
- Reject values above `1`.
- Reject non-numeric values (including strings).
- Do not silently clamp.
- Do not silently cast.

### Agreement Formula

Compute:

`agreement = 1 - abs(sequence_value - amd_value)`

### Output Contract

Return a dict with exactly:

- `sequence_value`
- `amd_value`
- `combined_value`
- `agreement`

All outputs must be deterministic and side-effect free.

### Test Coverage for Step 1

Tests must verify:

- valid normalized values
- invalid values below 0
- invalid values above 1
- missing required keys
- agreement formula correctness
- deterministic outputs
- no implicit casting from strings

## Explicitly Out of Scope for Prompt 1 Step 1

- Step 2 and beyond
- Prompt 2 safety hardening
- unrelated module refactors
