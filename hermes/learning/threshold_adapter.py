"""Stage 6C baseline threshold adaptation for Prompt 1 learning loop."""

from typing import Dict, List, Tuple

DEFAULT_MIN_TOTAL_TRADES = 100
DEFAULT_MIN_TRADES_PER_BUCKET = 20
DEFAULT_MIN_TRADES_PER_REGIME = 30
DEFAULT_TARGET_WIN_RATE = 0.55
MIN_CONFIDENCE_FLOOR = 0.40
MIN_CONFIDENCE_CEILING = 0.90
VALID_OUTCOMES = {"win", "loss", "breakeven"}


def _is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_completed_trade(trade: dict) -> bool:
    if not isinstance(trade, dict):
        return False
    if "confidence" not in trade or "regime" not in trade or "outcome" not in trade:
        return False
    if not _is_number(trade["confidence"]):
        return False
    if not isinstance(trade["regime"], str) or trade["regime"] == "":
        return False
    if trade["outcome"] not in VALID_OUTCOMES:
        return False
    confidence = float(trade["confidence"])
    return 0.0 <= confidence <= 1.0


def _bucket_lower_bound(confidence: float) -> float:
    if confidence >= 1.0:
        return 0.9
    return int(confidence * 10) / 10.0


def _bounded_min_confidence(value: float) -> float:
    bounded = max(MIN_CONFIDENCE_FLOOR, min(MIN_CONFIDENCE_CEILING, value))
    return round(bounded, 6)


def _bucket_stats(trades: List[dict]) -> Dict[float, Tuple[int, float]]:
    grouped: Dict[float, List[dict]] = {}
    for trade in trades:
        lower_bound = _bucket_lower_bound(float(trade["confidence"]))
        grouped.setdefault(lower_bound, []).append(trade)

    stats: Dict[float, Tuple[int, float]] = {}
    for bucket in sorted(grouped):
        group = grouped[bucket]
        trade_count = len(group)
        wins = sum(1 for trade in group if trade["outcome"] == "win")
        win_rate = wins / trade_count if trade_count > 0 else 0.0
        stats[bucket] = (trade_count, round(win_rate, 6))
    return stats


def _regime_stats(trades: List[dict], regime_name: str) -> Tuple[int, float]:
    group = [trade for trade in trades if trade["regime"] == regime_name]
    trade_count = len(group)
    if trade_count == 0:
        return (0, 0.0)
    wins = sum(1 for trade in group if trade["outcome"] == "win")
    return (trade_count, round(wins / trade_count, 6))


def adapt_thresholds(
    trades: List[dict],
    current_thresholds: dict,
    *,
    min_total_trades: int = DEFAULT_MIN_TOTAL_TRADES,
    min_trades_per_bucket: int = DEFAULT_MIN_TRADES_PER_BUCKET,
    min_trades_per_regime: int = DEFAULT_MIN_TRADES_PER_REGIME,
    target_win_rate: float = DEFAULT_TARGET_WIN_RATE,
) -> dict:
    """Adapt Prompt 1 baseline thresholds from completed trades."""
    completed = [trade for trade in trades if _is_completed_trade(trade)]

    if len(completed) < min_total_trades:
        return {
            "thresholds_adapted": False,
            "reason": "insufficient_sample_size",
        }

    old_thresholds = dict(current_thresholds)
    new_thresholds = dict(current_thresholds)
    adaptation_log = []

    bucket_statistics = _bucket_stats(completed)
    chosen_bucket = None
    for bucket_lower in sorted(bucket_statistics):
        trade_count, win_rate = bucket_statistics[bucket_lower]
        if trade_count >= min_trades_per_bucket and win_rate >= target_win_rate:
            chosen_bucket = bucket_lower
            break

    if chosen_bucket is not None:
        bounded = _bounded_min_confidence(chosen_bucket)
        new_thresholds["min_confidence"] = bounded
        adaptation_log.append(
            "min_confidence set from bucket {0:.1f} (bounded to {1:.2f})".format(
                chosen_bucket,
                bounded,
            )
        )

    chop_count, chop_win_rate = _regime_stats(completed, "chop")
    if chop_count >= min_trades_per_regime:
        if chop_win_rate < 0.45:
            new_thresholds["allow_chop"] = False
            adaptation_log.append("allow_chop set to false from chop win_rate")
        elif chop_win_rate >= 0.55:
            new_thresholds["allow_chop"] = True
            adaptation_log.append("allow_chop set to true from chop win_rate")

    if new_thresholds == old_thresholds:
        reason = "no_qualifying_bucket"
        if chosen_bucket is None and chop_count < min_trades_per_regime:
            reason = "no_qualifying_bucket"
        return {
            "thresholds_adapted": False,
            "reason": reason,
        }

    return {
        "thresholds_adapted": True,
        "old_thresholds": old_thresholds,
        "new_thresholds": new_thresholds,
        "adaptation_reason": "prompt1_baseline_threshold_adaptation",
        "adaptation_log": adaptation_log,
    }
