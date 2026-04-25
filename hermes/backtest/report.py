"""Stage 5D performance report metrics."""


def generate_performance_report(trades: list) -> dict:
    """Generate deterministic aggregate metrics for completed trades."""
    if not trades:
        return {
            "net_pnl": 0.0,
            "win_rate": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "profit_factor": 0.0,
            "max_drawdown": 0.0,
            "trade_count": 0,
            "trades_per_regime": {},
            "stability_score": 0.0,
        }

    trade_count = len(trades)
    net_pnl = 0.0
    win_total = 0.0
    loss_total = 0.0
    win_count = 0
    loss_count = 0
    trades_per_regime = {}

    cumulative_pnl = 0.0
    peak_pnl = 0.0
    max_drawdown = 0.0

    for trade in trades:
        pnl = float(trade.get("net_pnl", 0.0))
        outcome = trade.get("outcome")
        regime = trade.get("regime")

        net_pnl += pnl

        if outcome == "win":
            win_total += pnl
            win_count += 1
        elif outcome == "loss":
            loss_total += pnl
            loss_count += 1

        trades_per_regime[regime] = trades_per_regime.get(regime, 0) + 1

        cumulative_pnl += pnl
        if cumulative_pnl > peak_pnl:
            peak_pnl = cumulative_pnl

        drawdown = peak_pnl - cumulative_pnl
        if drawdown > max_drawdown:
            max_drawdown = drawdown

    win_rate = win_count / trade_count if trade_count > 0 else 0.0
    avg_win = win_total / win_count if win_count > 0 else 0.0
    avg_loss = abs(loss_total / loss_count) if loss_count > 0 else 0.0

    if loss_total == 0.0:
        profit_factor = 999.0
    else:
        profit_factor = win_total / abs(loss_total)

    stability_score = win_rate * profit_factor

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
    }
