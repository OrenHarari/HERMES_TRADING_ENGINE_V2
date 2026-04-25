# Changelog

## 0.1.6 - 2026-04-25
- Implemented Stage 5B risk guardrails in `hermes.risk.guardrails.check_risk_limits` with deterministic max-trades, daily-loss, loss-streak, and cooldown blocking reasons.
- Replaced placeholder risk test module with Stage 5B unit coverage for allowed/blocked paths and deterministic output.

## 0.1.5 - 2026-04-25
- Implemented Stage 5A decision confidence scoring in `hermes.decision.confidence.compute_confidence` with weighted regime-aware formula and [0,1] clamping.
- Implemented Stage 5A trade eligibility gating in `hermes.decision.eligibility.check_trade_allowed` with explicit deterministic block reasons.
- Replaced Stage 0 placeholder tests with Stage 5A coverage for confidence behavior and trade-eligibility pass/fail conditions.
- Resolved Stage 5A merge conflicts in changelog and test files while preserving real Stage 5A test coverage.

## 0.1.4 - 2026-04-25
- Implemented Stage 4 market intelligence functions in `hermes.market.regime` for deterministic regime classification plus normalized volatility and momentum scoring.
- Added Stage 4 unit tests for trend/chop/volatility regimes, score bounds, and deterministic output.

## 0.1.3 - 2026-04-25
- Implemented Stage 3 quality gate tests using AST-only scanning for banned `pandas`/`numpy` imports and `.values` usage.
- Added tests for repository pass state, each banned pattern, and excluded-directory behavior.

## 0.1.2 - 2026-04-25
- Implemented Stage 2 signal orchestrator in `orchestrate_signals`, using Stage 1 normalization output and strict strong/medium/weak labeling thresholds.
- Added Stage 2 unit tests for strong/medium/weak outcomes, deterministic behavior, value-driven labels, and normalization error propagation.

## 0.1.1 - 2026-04-25
- Implemented Stage 1 signal normalization in `normalize_signals` with strict type/range validation and agreement computation.
- Added Stage 1 unit tests for valid paths, error paths, agreement formula correctness, and deterministic behavior.

## 0.1.0 - 2026-04-25
- Initial Stage 0 repository scaffold created.
