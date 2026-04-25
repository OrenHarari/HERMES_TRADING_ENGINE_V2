"""Deterministic market intelligence layer for Prompt 1 Step 4."""

from __future__ import annotations


_VALID_REGIMES: tuple[str, str, str, str, str] = (
    "trend_up",
    "trend_down",
    "chop",
    "high_volatility",
    "low_volatility",
)


def _validate_close_price(value: object, index: int) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"candle[{index}] close must be numeric.")

    close_price = float(value)
    if close_price <= 0.0:
        raise ValueError(f"candle[{index}] close must be greater than 0.")

    return close_price


def _clamp_unit_interval(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


def classify_market_regime(candles: list[dict]) -> dict:
    """Classify market regime and compute normalized volatility/momentum scores.

    Uses only provided candles (no future data) and deterministic calculations.
    """
    if not isinstance(candles, list):
        raise ValueError("candles must be a list of candle dictionaries.")
    if len(candles) < 2:
        raise ValueError("candles must contain at least 2 candles.")

    close_prices: list[float] = []
    for index, candle in enumerate(candles):
        if not isinstance(candle, dict):
            raise ValueError(f"candle[{index}] must be a dictionary.")
        if "close" not in candle:
            raise ValueError(f"candle[{index}] is missing required 'close'.")

        close_prices.append(_validate_close_price(candle["close"], index))

    returns: list[float] = []
    for index in range(1, len(close_prices)):
        prev_close = close_prices[index - 1]
        curr_close = close_prices[index]
        abs_return = abs((curr_close - prev_close) / prev_close)
        returns.append(abs_return)

    avg_abs_return = sum(returns) / len(returns)
    volatility_score = _clamp_unit_interval(avg_abs_return / 0.05)

    momentum_raw = (close_prices[-1] - close_prices[0]) / close_prices[0]
    momentum_score = _clamp_unit_interval((momentum_raw + 1.0) / 2.0)

    if volatility_score >= 0.70:
        regime = "high_volatility"
    elif volatility_score <= 0.15:
        regime = "low_volatility"
    elif momentum_raw >= 0.02:
        regime = "trend_up"
    elif momentum_raw <= -0.02:
        regime = "trend_down"
    else:
        regime = "chop"

    if regime not in _VALID_REGIMES:
        raise ValueError("Internal error: invalid regime produced.")

    return {
        "regime": regime,
        "volatility_score": volatility_score,
        "momentum_score": momentum_score,
    }
