"""Unit tests for Stage 5A trade eligibility gating."""

import unittest

from hermes.trading.eligibility import check_trade_allowed


class EligibilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = {
            "min_confidence": 0.6,
            "min_agreement": 0.5,
            "allow_chop": False,
            "max_volatility": 0.8,
        }
        self.base_signal = {
            "sequence_value": 0.55,
            "amd_value": 0.60,
            "combined_value": 0.75,
            "agreement": 0.70,
            "label": "strong",
            "momentum_score": 0.80,
            "volatility_score": 0.30,
            "regime": "trend_up",
        }

    def test_allows_trade_when_all_rules_pass(self) -> None:
        result = check_trade_allowed(self.base_signal, self.config)

        self.assertEqual(result, {"trade_allowed": True, "reason": "allowed"})

    def test_blocks_trade_for_low_confidence(self) -> None:
        signal = dict(self.base_signal)
        signal["combined_value"] = 0.0
        signal["agreement"] = 0.0
        signal["momentum_score"] = 0.0
        signal["volatility_score"] = 1.0
        signal["regime"] = "chop"

        result = check_trade_allowed(signal, self.config)

        self.assertEqual(result, {"trade_allowed": False, "reason": "low_confidence"})

    def test_blocks_trade_for_low_agreement(self) -> None:
        signal = dict(self.base_signal)
        signal["agreement"] = 0.1

        result = check_trade_allowed(signal, self.config)

        self.assertEqual(result, {"trade_allowed": False, "reason": "low_agreement"})

    def test_blocks_trade_for_chop_when_disabled(self) -> None:
        signal = dict(self.base_signal)
        signal["regime"] = "chop"

        result = check_trade_allowed(signal, self.config)

        self.assertEqual(result, {"trade_allowed": False, "reason": "chop_blocked"})

    def test_blocks_trade_for_high_volatility(self) -> None:
        signal = dict(self.base_signal)
        signal["volatility_score"] = 0.95

        result = check_trade_allowed(signal, self.config)

        self.assertEqual(result, {"trade_allowed": False, "reason": "volatility_too_high"})

    def test_output_is_deterministic(self) -> None:
        first = check_trade_allowed(self.base_signal, self.config)
        second = check_trade_allowed(self.base_signal, self.config)

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
