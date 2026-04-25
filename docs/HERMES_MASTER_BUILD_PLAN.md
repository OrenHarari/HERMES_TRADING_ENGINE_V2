# HERMES Master Build Plan

- This project is implemented in locked stages.
- Do not implement the whole project in one task.
- Prompt 1 builds the core deterministic learning trading engine.
- Prompt 2 hardens the engine without breaking existing behavior.
- Each stage must be requested explicitly.
- Stage 0 is scaffold only.
- Stage 1 is Signal Normalization.
- Stage 2 is Orchestrator.
- Stage 3 is Quality Gate.
- Stage 4 is Market Intelligence.
- Stage 5 is Trading Edge Validation.
- Stage 6 is Learning Loop.
- Prompt 2 starts only after explicit instruction.
