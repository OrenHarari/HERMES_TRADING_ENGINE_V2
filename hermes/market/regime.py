"""Market regime classification and scoring for Stage 4."""


def _clamp_01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


def compute_volatility_score(candles: list[dict]) -> float:
    """Compute normalized volatility score from average candle range."""
    if len(candles) < 1:
        return 0.0

    total_range_ratio = 0.0
    count = 0

    for candle in candles:
        close = float(candle["close"])
        high = float(candle["high"])
        low = float(candle["low"])
        base = abs(close)
        if base <= 1e-9:
            continue
        total_range_ratio += max(0.0, high - low) / base
        count += 1

    if count == 0:
        return 0.0

    avg_range_ratio = total_range_ratio / float(count)
    return _clamp_01(avg_range_ratio / 0.30)


def compute_momentum_score(candles: list[dict]) -> float:
    """Compute normalized absolute momentum from net close-to-close change."""
    if len(candles) < 2:
        return 0.0

    first_close = float(candles[0]["close"])
    last_close = float(candles[-1]["close"])
    base = abs(first_close)
    if base <= 1e-9:
        return 0.0

    change_ratio = abs(last_close - first_close) / base
    return _clamp_01(change_ratio / 0.10)


def classify_regime(candles: list[dict]) -> str:
    """Classify market regime using deterministic change and volatility thresholds."""
    if len(candles) < 2:
        return "low_volatility"

    first_close = float(candles[0]["close"])
    last_close = float(candles[-1]["close"])
    base = abs(first_close)
    if base <= 1e-9:
        return "low_volatility"

    net_change_ratio = (last_close - first_close) / base
    volatility_score = compute_volatility_score(candles)

    if volatility_score >= 0.90:
        return "high_volatility"

    if net_change_ratio >= 0.08:
        return "trend_up"

    if net_change_ratio <= -0.08:
        return "trend_down"

    if abs(net_change_ratio) <= 0.02:
        if volatility_score <= 0.12:
            return "low_volatility"
        if volatility_score >= 0.25:
            return "chop"

    if volatility_score <= 0.12:
        return "low_volatility"

    return "chop"
