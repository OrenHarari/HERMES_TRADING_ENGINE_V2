"""Unit tests for Stage 5A trade eligibility gating."""

import unittest

from hermes.decision.eligibility import check_trade_allowed


class TestCheckTradeAllowed(unittest.TestCase):
    def setUp(self) -> None:
        self.default_config = {
            "min_confidence": 0.6,
            "min_agreement": 0.5,
            "allow_chop": False,
            "max_volatility": 0.8,
        }

    def test_allowed_trade(self) -> None:
        signal = {
            "confidence": 0.75,
            "agreement": 0.65,
            "regime": "trend_up",
            "volatility_score": 0.40,
        }

        result = check_trade_allowed(signal, self.default_config)

        self.assertEqual(result, {"trade_allowed": True, "reason": "allowed"})

    def test_blocked_by_confidence(self) -> None:
        signal = {
            "confidence": 0.59,
            "agreement": 0.65,
            "regime": "trend_up",
            "volatility_score": 0.40,
        }

        result = check_trade_allowed(signal, self.default_config)

        self.assertEqual(result, {"trade_allowed": False, "reason": "low_confidence"})

    def test_blocked_by_agreement(self) -> None:
        signal = {
            "confidence": 0.75,
            "agreement": 0.49,
            "regime": "trend_up",
            "volatility_score": 0.40,
        }

        result = check_trade_allowed(signal, self.default_config)

        self.assertEqual(result, {"trade_allowed": False, "reason": "low_agreement"})

    def test_blocked_by_chop(self) -> None:
        signal = {
            "confidence": 0.75,
            "agreement": 0.65,
            "regime": "chop",
            "volatility_score": 0.40,
        }

        result = check_trade_allowed(signal, self.default_config)

        self.assertEqual(result, {"trade_allowed": False, "reason": "chop_blocked"})

    def test_blocked_by_volatility(self) -> None:
        signal = {
            "confidence": 0.75,
            "agreement": 0.65,
            "regime": "trend_up",
            "volatility_score": 0.81,
        }

        result = check_trade_allowed(signal, self.default_config)

        self.assertEqual(result, {"trade_allowed": False, "reason": "volatility_too_high"})

    def test_deterministic_eligibility(self) -> None:
        signal = {
            "confidence": 0.75,
            "agreement": 0.65,
            "regime": "trend_up",
            "volatility_score": 0.40,
        }

        first = check_trade_allowed(signal, self.default_config)
        second = check_trade_allowed(signal, self.default_config)

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
