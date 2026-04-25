# Changelog

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
