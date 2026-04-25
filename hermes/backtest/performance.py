"""Performance report generation for Prompt 1 Step 5."""

from __future__ import annotations


def _safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0.0:
        return 0.0
    return numerator / denominator


def generate_performance_report(trades: list[dict], fees_available: bool) -> dict:
    """Generate deterministic backtest performance metrics."""
    if not isinstance(trades, list):
        raise ValueError("trades must be a list of dictionaries.")

    adjusted_pnls: list[float] = []
    trades_per_regime: dict[str, int] = {}

    for trade in trades:
        if not isinstance(trade, dict):
            raise ValueError("Each trade must be a dictionary.")
        if "pnl" not in trade:
            raise ValueError("Each trade requires a pnl field.")

        pnl = trade["pnl"]
        if isinstance(pnl, bool) or not isinstance(pnl, (int, float)):
            raise ValueError("trade pnl must be numeric.")

        adjusted_pnl = float(pnl)
        if fees_available:
            fee = trade.get("fee", 0.0)
            if isinstance(fee, bool) or not isinstance(fee, (int, float)):
                raise ValueError("trade fee must be numeric when provided.")
            adjusted_pnl -= float(fee)

        adjusted_pnls.append(adjusted_pnl)

        regime = trade.get("regime", "unknown")
        if not isinstance(regime, str):
            regime = "unknown"
        trades_per_regime[regime] = trades_per_regime.get(regime, 0) + 1

    trade_count = len(adjusted_pnls)
    net_pnl = sum(adjusted_pnls)

    wins = [p for p in adjusted_pnls if p > 0.0]
    losses = [p for p in adjusted_pnls if p < 0.0]

    win_rate = _safe_divide(float(len(wins)), float(trade_count))
    avg_win = _safe_divide(sum(wins), float(len(wins))) if wins else 0.0
    avg_loss = _safe_divide(sum(losses), float(len(losses))) if losses else 0.0

    gross_profit = sum(wins)
    gross_loss_abs = abs(sum(losses))
    if gross_loss_abs == 0.0:
        profit_factor = float("inf") if gross_profit > 0.0 else 0.0
    else:
        profit_factor = gross_profit / gross_loss_abs

    equity = 0.0
    peak = 0.0
    max_drawdown = 0.0
    for pnl in adjusted_pnls:
        equity += pnl
        if equity > peak:
            peak = equity
        drawdown = peak - equity
        if drawdown > max_drawdown:
            max_drawdown = drawdown

    if peak <= 0.0:
        stability_score = 1.0 if max_drawdown == 0.0 else 0.0
    else:
        stability_score = 1.0 - _safe_divide(max_drawdown, peak)
        if stability_score < 0.0:
            stability_score = 0.0
        if stability_score > 1.0:
            stability_score = 1.0

    return {
        "net_pnl": net_pnl,
        "win_rate": win_rate,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "profit_factor": profit_factor,
        "max_drawdown": max_drawdown,
        "trade_count": trade_count,
        "trades_per_regime": trades_per_regime,
        "stability_score": stability_score,
        "cost_model_applied": bool(fees_available),
        "notes": "Win rate alone is not enough; evaluate multiple metrics together.",
    }
