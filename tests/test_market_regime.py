import unittest

from hermes.market.regime import classify_market_regime


VALID_REGIMES = {
    "trend_up",
    "trend_down",
    "chop",
    "high_volatility",
    "low_volatility",
}


class TestMarketRegime(unittest.TestCase):
    def test_regime_is_always_valid_enum(self) -> None:
        windows = [
            [
                {"close": 100.0},
                {"close": 102.0},
                {"close": 104.0},
                {"close": 106.0},
            ],
            [
                {"close": 100.0},
                {"close": 98.0},
                {"close": 96.0},
                {"close": 94.0},
            ],
            [
                {"close": 100.0},
                {"close": 100.2},
                {"close": 99.9},
                {"close": 100.1},
            ],
            [
                {"close": 100.0},
                {"close": 110.0},
                {"close": 95.0},
                {"close": 120.0},
            ],
        ]

        for candles in windows:
            result = classify_market_regime(candles)
            self.assertIn(result["regime"], VALID_REGIMES)

    def test_volatility_score_in_unit_interval(self) -> None:
        result = classify_market_regime(
            [{"close": 100.0}, {"close": 101.0}, {"close": 100.5}, {"close": 102.0}]
        )
        self.assertGreaterEqual(result["volatility_score"], 0.0)
        self.assertLessEqual(result["volatility_score"], 1.0)

    def test_momentum_score_in_unit_interval(self) -> None:
        result = classify_market_regime(
            [{"close": 100.0}, {"close": 101.0}, {"close": 102.0}, {"close": 103.0}]
        )
        self.assertGreaterEqual(result["momentum_score"], 0.0)
        self.assertLessEqual(result["momentum_score"], 1.0)

    def test_no_future_data_used(self) -> None:
        prefix = [
            {"close": 100.0},
            {"close": 101.0},
            {"close": 102.0},
            {"close": 103.0},
        ]
        with_future = prefix + [{"close": 50.0}, {"close": 200.0}]

        prefix_result = classify_market_regime(prefix)
        truncated_result = classify_market_regime(with_future[: len(prefix)])

        self.assertEqual(prefix_result, truncated_result)

    def test_same_input_is_deterministic(self) -> None:
        candles = [
            {"close": 100.0},
            {"close": 101.5},
            {"close": 99.0},
            {"close": 100.5},
        ]

        first = classify_market_regime(candles)
        second = classify_market_regime(candles)

        self.assertEqual(first, second)

    def test_missing_volume_does_not_fail(self) -> None:
        candles = [
            {"close": 100.0},
            {"close": 101.0},
            {"close": 102.0},
            {"close": 101.5},
        ]

        result = classify_market_regime(candles)
        self.assertIn(result["regime"], VALID_REGIMES)

    def test_invalid_or_insufficient_windows_are_handled_safely(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least 2 candles"):
            classify_market_regime([{"close": 100.0}])

        with self.assertRaisesRegex(ValueError, "missing required 'close'"):
            classify_market_regime([{"close": 100.0}, {"open": 101.0}])

        with self.assertRaisesRegex(ValueError, "must be numeric"):
            classify_market_regime([{"close": 100.0}, {"close": "101.0"}])
