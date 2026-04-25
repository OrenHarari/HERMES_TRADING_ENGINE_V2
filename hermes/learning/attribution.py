"""Signal attribution helpers for Stage 6B."""

from typing import Dict, List, Tuple

DEFAULT_MIN_TRADES_PER_BUCKET = 20
DEFAULT_MIN_TRADES_PER_REGIME = 30
DEFAULT_MIN_TRADES_PER_COMBINATION = 50
VALID_OUTCOMES = {"win", "loss", "breakeven"}


def _is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_completed_trade(trade: dict) -> bool:
    if not isinstance(trade, dict):
        return False
    if (
        "confidence" not in trade
        or "regime" not in trade
        or "outcome" not in trade
        or "pnl" not in trade
    ):
        return False
    if not _is_number(trade["confidence"]):
        return False
    if not isinstance(trade["regime"], str) or trade["regime"] == "":
        return False
    if trade["outcome"] not in VALID_OUTCOMES:
        return False
    if not _is_number(trade["pnl"]):
        return False
    confidence = float(trade["confidence"])
    return 0.0 <= confidence <= 1.0


def _bucket_label(confidence: float) -> str:
    if confidence >= 1.0:
        lower = 0.9
        upper = 1.0
    else:
        lower = int(confidence * 10) / 10.0
        upper = lower + 0.1
    return "{0:.1f}-{1:.1f}".format(lower, upper)


def _safe_round(value: float) -> float:
    return round(value, 6)


def _build_condition_result(condition: str, group: List[dict]) -> dict:
    trade_count = len(group)
    wins = sum(1 for trade in group if trade["outcome"] == "win")
    losses = sum(1 for trade in group if trade["outcome"] == "loss")
    win_rate = wins / trade_count if trade_count > 0 else 0.0

    result = {
        "condition": condition,
        "win_rate": _safe_round(win_rate),
        "trade_count": trade_count,
    }

    pnl_values = [float(trade["pnl"]) for trade in group if _is_number(trade.get("pnl"))]
    if pnl_values:
        result["avg_net_pnl"] = _safe_round(sum(pnl_values) / len(pnl_values))

    if wins > 0 and losses > 0:
        gross_profit = sum(
            float(trade["pnl"])
            for trade in group
            if trade["outcome"] == "win" and _is_number(trade.get("pnl"))
        )
        gross_loss = sum(
            abs(float(trade["pnl"]))
            for trade in group
            if trade["outcome"] == "loss" and _is_number(trade.get("pnl"))
        )
        if gross_loss > 0.0:
            result["profit_factor"] = _safe_round(gross_profit / gross_loss)

    return result


def _sorted_results(results: List[dict], reverse: bool) -> List[dict]:
    return sorted(
        results,
        key=lambda item: (item["win_rate"], item["trade_count"], item["condition"]),
        reverse=reverse,
    )


def _group_by_bucket(trades: List[dict]) -> Dict[str, List[dict]]:
    grouped = {}
    for trade in trades:
        label = _bucket_label(float(trade["confidence"]))
        grouped.setdefault(label, []).append(trade)
    return grouped


def _group_by_regime(trades: List[dict]) -> Dict[str, List[dict]]:
    grouped = {}
    for trade in trades:
        regime = trade["regime"]
        grouped.setdefault(regime, []).append(trade)
    return grouped


def _group_by_bucket_and_regime(trades: List[dict]) -> Dict[Tuple[str, str], List[dict]]:
    grouped = {}
    for trade in trades:
        bucket = _bucket_label(float(trade["confidence"]))
        regime = trade["regime"]
        grouped.setdefault((bucket, regime), []).append(trade)
    return grouped


def build_signal_attribution(
    trades: List[dict],
    min_trades_per_bucket: int = DEFAULT_MIN_TRADES_PER_BUCKET,
    min_trades_per_regime: int = DEFAULT_MIN_TRADES_PER_REGIME,
    min_trades_per_combination: int = DEFAULT_MIN_TRADES_PER_COMBINATION,
) -> dict:
    """Build deterministic attribution from completed Stage 6A trades."""
    completed = [trade for trade in trades if _is_completed_trade(trade)]

    total_trades = len(completed)
    wins = sum(1 for trade in completed if trade["outcome"] == "win")
    overall_win_rate = wins / total_trades if total_trades > 0 else 0.0

    bucket_groups = _group_by_bucket(completed)
    regime_groups = _group_by_regime(completed)
    combination_groups = _group_by_bucket_and_regime(completed)

    condition_results: List[dict] = []

    for bucket in sorted(bucket_groups):
        group = bucket_groups[bucket]
        if len(group) >= min_trades_per_bucket:
            condition_results.append(
                _build_condition_result("confidence:{0}".format(bucket), group)
            )

    for regime in sorted(regime_groups):
        group = regime_groups[regime]
        if len(group) >= min_trades_per_regime:
            condition_results.append(
                _build_condition_result("regime:{0}".format(regime), group)
            )

    for bucket, regime in sorted(combination_groups):
        group = combination_groups[(bucket, regime)]
        if len(group) >= min_trades_per_combination:
            condition_results.append(
                _build_condition_result(
                    "confidence:{0}|regime:{1}".format(bucket, regime), group
                )
            )

    if not condition_results:
        return {
            "total_trades": total_trades,
            "overall_win_rate": _safe_round(overall_win_rate),
            "best_conditions": [],
            "worst_conditions": [],
            "thresholds_adapted": False,
            "reason": "insufficient_sample_size",
        }

    return {
        "total_trades": total_trades,
        "overall_win_rate": _safe_round(overall_win_rate),
        "best_conditions": _sorted_results(condition_results, reverse=True),
        "worst_conditions": _sorted_results(condition_results, reverse=False),
        "thresholds_adapted": False,
    }
