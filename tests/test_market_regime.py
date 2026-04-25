"""Tests for Stage 4 market regime classification and scoring."""

import unittest

from hermes.market.regime import (
    classify_regime,
    compute_momentum_score,
    compute_volatility_score,
)


def make_candle(timestamp: int, open_: float, high: float, low: float, close: float) -> dict:
    return {
        "timestamp": timestamp,
        "open": open_,
        "high": high,
        "low": low,
        "close": close,
    }


class MarketRegimeTests(unittest.TestCase):
    def test_classify_regime_trend_up(self) -> None:
        candles = [
            make_candle(1, 100.0, 103.0, 99.0, 102.0),
            make_candle(2, 102.0, 106.0, 101.0, 105.0),
            make_candle(3, 105.0, 109.0, 104.0, 108.0),
            make_candle(4, 108.0, 113.0, 107.0, 112.0),
            make_candle(5, 112.0, 118.0, 111.0, 117.0),
        ]
        self.assertEqual(classify_regime(candles), "trend_up")

    def test_classify_regime_trend_down(self) -> None:
        candles = [
            make_candle(1, 120.0, 121.0, 116.0, 117.0),
            make_candle(2, 117.0, 118.0, 112.0, 113.0),
            make_candle(3, 113.0, 114.0, 107.0, 108.0),
            make_candle(4, 108.0, 109.0, 102.0, 103.0),
            make_candle(5, 103.0, 104.0, 96.0, 97.0),
        ]
        self.assertEqual(classify_regime(candles), "trend_down")

    def test_classify_regime_chop(self) -> None:
        candles = [
            make_candle(1, 100.0, 111.0, 89.0, 101.0),
            make_candle(2, 101.0, 113.0, 90.0, 100.0),
            make_candle(3, 100.0, 112.0, 88.0, 99.0),
            make_candle(4, 99.0, 114.0, 87.0, 100.0),
            make_candle(5, 100.0, 110.0, 89.0, 100.2),
        ]
        self.assertEqual(classify_regime(candles), "chop")

    def test_classify_regime_high_volatility(self) -> None:
        candles = [
            make_candle(1, 100.0, 120.0, 80.0, 101.0),
            make_candle(2, 101.0, 125.0, 75.0, 102.0),
            make_candle(3, 102.0, 130.0, 70.0, 103.0),
            make_candle(4, 103.0, 135.0, 65.0, 104.0),
            make_candle(5, 104.0, 140.0, 60.0, 105.0),
        ]
        self.assertEqual(classify_regime(candles), "high_volatility")

    def test_classify_regime_low_volatility(self) -> None:
        candles = [
            make_candle(1, 100.0, 101.0, 99.0, 100.2),
            make_candle(2, 100.2, 101.1, 99.6, 100.1),
            make_candle(3, 100.1, 100.8, 99.7, 100.0),
            make_candle(4, 100.0, 100.7, 99.5, 100.1),
            make_candle(5, 100.1, 100.9, 99.8, 100.0),
        ]
        self.assertEqual(classify_regime(candles), "low_volatility")

    def test_volatility_score_in_range(self) -> None:
        candles = [
            make_candle(1, 100.0, 102.0, 99.0, 101.0),
            make_candle(2, 101.0, 104.0, 100.0, 102.0),
            make_candle(3, 102.0, 106.0, 101.0, 105.0),
        ]
        score = compute_volatility_score(candles)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_momentum_score_in_range(self) -> None:
        candles = [
            make_candle(1, 100.0, 101.0, 99.0, 100.5),
            make_candle(2, 100.5, 102.0, 100.0, 101.5),
            make_candle(3, 101.5, 104.0, 101.0, 103.0),
        ]
        score = compute_momentum_score(candles)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_deterministic_output(self) -> None:
        candles = [
            make_candle(1, 100.0, 104.0, 98.0, 101.0),
            make_candle(2, 101.0, 105.0, 99.0, 103.0),
            make_candle(3, 103.0, 106.0, 100.0, 102.0),
            make_candle(4, 102.0, 107.0, 101.0, 106.0),
            make_candle(5, 106.0, 110.0, 104.0, 109.0),
        ]

        regime_a = classify_regime(candles)
        regime_b = classify_regime(candles)
        vol_a = compute_volatility_score(candles)
        vol_b = compute_volatility_score(candles)
        mom_a = compute_momentum_score(candles)
        mom_b = compute_momentum_score(candles)

        self.assertEqual(regime_a, regime_b)
        self.assertEqual(vol_a, vol_b)
        self.assertEqual(mom_a, mom_b)


if __name__ == "__main__":
    unittest.main()
