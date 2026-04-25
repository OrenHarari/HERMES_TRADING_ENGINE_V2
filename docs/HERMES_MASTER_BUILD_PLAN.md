# HERMES Master Build Plan

## Execution Structure

- Prompt 1 builds the core deterministic learning trading engine.
- Prompt 2 hardens the engine without breaking existing behavior.
- Do not implement the whole project in one task.
- Implement one requested step at a time.
- Add tests before implementation.
- Run all tests after every change.
- Preserve backward compatibility.
- Do not add live execution.

## Delivery Rules

- Keep each change set minimal and scoped to the requested step.
- Prioritize pure, explainable, deterministic logic.
- Do not introduce external dependencies unless explicitly approved.
