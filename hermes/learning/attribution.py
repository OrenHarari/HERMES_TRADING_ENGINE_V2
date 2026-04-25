"""Signal attribution analysis for Prompt 1 Step 6."""

from __future__ import annotations


def _confidence_bucket(confidence: float) -> str:
    if confidence < 0.20:
        return "0.00-0.19"
    if confidence < 0.40:
        return "0.20-0.39"
    if confidence < 0.60:
        return "0.40-0.59"
    if confidence < 0.80:
        return "0.60-0.79"
    return "0.80-1.00"


def _metric_summary(condition: str, trades: list[dict]) -> dict:
    trade_count = len(trades)
    wins = [t for t in trades if t["outcome"] == "win"]
    losses = [t for t in trades if t["outcome"] == "loss"]

    win_rate = len(wins) / trade_count if trade_count > 0 else 0.0

    net_pnls = [t.get("net_pnl") for t in trades if isinstance(t.get("net_pnl"), (int, float))]
    avg_net_pnl = sum(net_pnls) / len(net_pnls) if net_pnls else None

    gross_profit = sum(float(t.get("net_pnl", 0.0)) for t in wins)
    gross_loss = abs(sum(float(t.get("net_pnl", 0.0)) for t in losses))
    profit_factor = None if gross_loss == 0.0 else gross_profit / gross_loss

    return {
        "condition": condition,
        "win_rate": win_rate,
        "trade_count": trade_count,
        "avg_net_pnl": avg_net_pnl,
        "profit_factor": profit_factor,
    }


def analyze_signal_attribution(
    trades: list[dict],
    min_trades_per_bucket: int = 20,
    min_trades_per_regime: int = 30,
    min_trades_per_combination: int = 50,
) -> dict:
    """Analyze win-rate attribution across confidence, regime, and combination."""
    if not isinstance(trades, list):
        raise ValueError("trades must be a list.")

    required = ("confidence", "regime", "outcome")
    valid_trades: list[dict] = []
    for trade in trades:
        if not isinstance(trade, dict):
            continue
        if not all(key in trade for key in required):
            continue
        if trade["outcome"] not in {"win", "loss", "breakeven"}:
            continue
        confidence = trade["confidence"]
        if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
            continue

        valid_trades.append({**trade, "confidence": float(confidence)})

    if len(valid_trades) < min(min_trades_per_bucket, min_trades_per_regime, min_trades_per_combination):
        return {"best_conditions": [], "worst_conditions": [], "insufficient_data": True}

    buckets: dict[str, list[dict]] = {}
    regimes: dict[str, list[dict]] = {}
    combos: dict[str, list[dict]] = {}

    for trade in valid_trades:
        bucket = _confidence_bucket(trade["confidence"])
        regime = str(trade["regime"])
        combo = f"{bucket}|{regime}"

        buckets.setdefault(bucket, []).append(trade)
        regimes.setdefault(regime, []).append(trade)
        combos.setdefault(combo, []).append(trade)

    summaries: list[dict] = []
    for key, bucket_trades in buckets.items():
        if len(bucket_trades) >= min_trades_per_bucket:
            summaries.append(_metric_summary(f"confidence_bucket:{key}", bucket_trades))

    for key, regime_trades in regimes.items():
        if len(regime_trades) >= min_trades_per_regime:
            summaries.append(_metric_summary(f"regime:{key}", regime_trades))

    for key, combo_trades in combos.items():
        if len(combo_trades) >= min_trades_per_combination:
            summaries.append(_metric_summary(f"combo:{key}", combo_trades))

    ordered = sorted(summaries, key=lambda item: (item["win_rate"], item["trade_count"]), reverse=True)

    return {
        "best_conditions": ordered[:3],
        "worst_conditions": list(reversed(ordered[-3:])),
        "insufficient_data": len(ordered) == 0,
    }
