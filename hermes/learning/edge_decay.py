"""Edge decay detection for Prompt 1 Step 6."""

from __future__ import annotations


def monitor_edge_decay(
    trades: list[dict],
    current_min_confidence: float,
    existing_alert: bool,
) -> dict:
    """Monitor rolling win rates and detect edge decay / recovery."""
    if not isinstance(trades, list):
        raise ValueError("trades must be a list.")

    ordered = sorted(trades, key=lambda t: float(t.get("timestamp", 0.0)))
    rolling_win_rates: list[float] = []

    for end in range(20, len(ordered) + 1, 20):
        window = ordered[end - 20 : end]
        wins = sum(1 for trade in window if trade.get("outcome") == "win")
        rolling_win_rates.append(wins / 20.0)

    logs: list[str] = []
    alert = existing_alert
    proposed_min_confidence = current_min_confidence

    if len(rolling_win_rates) >= 2:
        if rolling_win_rates[-1] < 0.45 and rolling_win_rates[-2] < 0.45:
            alert = True
            proposed_min_confidence = min(0.90, current_min_confidence + 0.05)
            logs.append("Edge decay detected: rolling win_rate below 0.45 for two consecutive windows.")

    if existing_alert and len(ordered) >= 10:
        recent = ordered[-10:]
        recent_wins = sum(1 for trade in recent if trade.get("outcome") == "win")
        recent_win_rate = recent_wins / 10.0
        if recent_win_rate > 0.50:
            alert = False
            logs.append("Edge decay recovery detected: win_rate above 0.50 for last 10 completed trades.")

    return {
        "rolling_win_rates": rolling_win_rates,
        "edge_decay_alert": alert,
        "proposed_min_confidence": proposed_min_confidence,
        "logs": logs,
    }
