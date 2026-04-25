"""Threshold adaptation and walk-forward validation for Prompt 1 Step 6."""

from __future__ import annotations


def _compute_trade_stats(trades: list[dict]) -> dict:
    count = len(trades)
    wins = [t for t in trades if t.get("outcome") == "win"]
    losses = [t for t in trades if t.get("outcome") == "loss"]
    net_pnl = sum(float(t.get("net_pnl", 0.0)) for t in trades)

    win_rate = (len(wins) / count) if count > 0 else 0.0
    gross_profit = sum(float(t.get("net_pnl", 0.0)) for t in wins)
    gross_loss = abs(sum(float(t.get("net_pnl", 0.0)) for t in losses))
    profit_factor = None if gross_loss == 0.0 else gross_profit / gross_loss

    equity = 0.0
    peak = 0.0
    max_drawdown = 0.0
    for trade in trades:
        equity += float(trade.get("net_pnl", 0.0))
        if equity > peak:
            peak = equity
        drawdown = peak - equity
        if drawdown > max_drawdown:
            max_drawdown = drawdown

    stability_score = 1.0 if peak <= 0.0 else max(0.0, min(1.0, 1.0 - (max_drawdown / peak)))

    return {
        "trade_count": count,
        "win_rate": win_rate,
        "net_pnl": net_pnl,
        "profit_factor": profit_factor,
        "max_drawdown": max_drawdown,
        "stability_score": stability_score,
    }


def propose_threshold_adaptation(
    trades: list[dict],
    current_thresholds: dict,
    min_trades_per_combination: int = 50,
    isolated_test_mode: bool = False,
    safety_hardening_active: bool = False,
) -> dict:
    """Propose bounded threshold adaptation from completed trades."""
    if not isinstance(trades, list) or not isinstance(current_thresholds, dict):
        raise ValueError("trades must be a list and current_thresholds must be a dict.")

    current_min_confidence = float(current_thresholds.get("min_confidence", 0.6))
    logs: list[dict] = []

    if len(trades) < 100:
        return {
            "proposed_thresholds": {"min_confidence": current_min_confidence},
            "applied": False,
            "risk_guardrails_unchanged": True,
            "reason": "Not enough completed trades (need at least 100).",
            "logs": logs,
        }

    combo_counts: dict[str, int] = {}
    for trade in trades:
        combo = f"{trade.get('regime', 'unknown')}|{trade.get('outcome', 'unknown')}"
        combo_counts[combo] = combo_counts.get(combo, 0) + 1

    max_combo_count = max((combo_counts[key] for key in combo_counts), default=0)
    if max_combo_count < min_trades_per_combination:
        return {
            "proposed_thresholds": {"min_confidence": current_min_confidence},
            "applied": False,
            "risk_guardrails_unchanged": True,
            "reason": "Not enough trades in any regime/outcome combination.",
            "logs": logs,
        }

    stats = _compute_trade_stats(trades)
    proposed = current_min_confidence
    reason = "No threshold change required."

    if stats["win_rate"] < 0.45:
        proposed = current_min_confidence + 0.05
        reason = "Win rate below 0.45; increasing min_confidence by 0.05."
    elif stats["win_rate"] > 0.60:
        proposed = current_min_confidence - 0.05
        reason = "Win rate above 0.60; decreasing min_confidence by 0.05."

    if proposed < 0.40:
        proposed = 0.40
    if proposed > 0.90:
        proposed = 0.90

    applied = isolated_test_mode and not safety_hardening_active and proposed != current_min_confidence
    logs.append(
        {
            "before": current_min_confidence,
            "after": proposed,
            "reason": reason,
            "applied": applied,
        }
    )

    return {
        "proposed_thresholds": {"min_confidence": proposed},
        "applied": applied,
        "risk_guardrails_unchanged": True,
        "reason": reason,
        "logs": logs,
    }


def run_walk_forward_validation(
    trades: list[dict],
    train_size: int,
    test_size: int,
    min_test_trades: int = 5,
) -> dict:
    """Run rolling train/test walk-forward validation with non-overlapping windows."""
    if not isinstance(trades, list):
        raise ValueError("trades must be a list.")
    if train_size <= 0 or test_size <= 0:
        raise ValueError("train_size and test_size must be positive.")

    ordered = sorted(trades, key=lambda t: float(t.get("timestamp", 0.0)))
    total_needed = train_size + test_size
    if len(ordered) < total_needed:
        return {"windows": [], "insufficient_data": True, "reason": "Insufficient data for one walk-forward window."}

    windows: list[dict] = []
    start = 0
    window_index = 0
    while start + total_needed <= len(ordered):
        train = ordered[start : start + train_size]
        test = ordered[start + train_size : start + total_needed]

        stats = _compute_trade_stats(test)
        accepted = stats["trade_count"] >= min_test_trades and stats["win_rate"] >= 0.5 and stats["net_pnl"] > 0

        windows.append(
            {
                "window_index": window_index,
                "train_start": float(train[0].get("timestamp", 0.0)),
                "train_end": float(train[-1].get("timestamp", 0.0)),
                "test_start": float(test[0].get("timestamp", 0.0)),
                "test_end": float(test[-1].get("timestamp", 0.0)),
                "trade_count": stats["trade_count"],
                "win_rate": stats["win_rate"],
                "net_pnl": stats["net_pnl"],
                "profit_factor": stats["profit_factor"],
                "max_drawdown": stats["max_drawdown"],
                "stability_score": stats["stability_score"],
                "accepted": accepted,
                "rejection_reason": "" if accepted else "Window did not meet acceptance criteria.",
            }
        )

        start += test_size
        window_index += 1

    return {"windows": windows, "insufficient_data": False, "reason": ""}
