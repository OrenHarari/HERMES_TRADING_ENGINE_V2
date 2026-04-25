import unittest

from hermes.decision.eligibility import evaluate_trade_eligibility


class TestEligibility(unittest.TestCase):
    def test_trade_allowed_when_all_conditions_pass(self) -> None:
        result = evaluate_trade_eligibility(
            signal_data={"agreement": 0.9, "volatility_score": 0.4, "regime": "trend_up"},
            confidence_score=0.8,
            min_confidence=0.6,
            min_agreement=0.6,
            allow_chop=False,
            volatility_bounds=(0.1, 0.8),
            risk_result={"allowed": True, "reason": "", "position_size": 0.4},
            active_block_condition=False,
        )
        self.assertTrue(result["trade_allowed"])
        self.assertEqual(result["reason_if_blocked"], "")

    def test_blocks_on_low_confidence(self) -> None:
        result = evaluate_trade_eligibility(
            signal_data={"agreement": 0.9, "volatility_score": 0.4, "regime": "trend_up"},
            confidence_score=0.2,
            min_confidence=0.6,
            min_agreement=0.6,
            allow_chop=False,
            volatility_bounds=(0.1, 0.8),
            risk_result={"allowed": True, "reason": "", "position_size": 0.4},
            active_block_condition=False,
        )
        self.assertFalse(result["trade_allowed"])
        self.assertIn("confidence_score", result["reason_if_blocked"])

    def test_blocks_chop_unless_allowed(self) -> None:
        blocked = evaluate_trade_eligibility(
            signal_data={"agreement": 0.9, "volatility_score": 0.4, "regime": "chop"},
            confidence_score=0.8,
            min_confidence=0.6,
            min_agreement=0.6,
            allow_chop=False,
            volatility_bounds=(0.1, 0.8),
            risk_result={"allowed": True, "reason": "", "position_size": 0.4},
            active_block_condition=False,
        )
        allowed = evaluate_trade_eligibility(
            signal_data={"agreement": 0.9, "volatility_score": 0.4, "regime": "chop"},
            confidence_score=0.8,
            min_confidence=0.6,
            min_agreement=0.6,
            allow_chop=True,
            volatility_bounds=(0.1, 0.8),
            risk_result={"allowed": True, "reason": "", "position_size": 0.4},
            active_block_condition=False,
        )
        self.assertFalse(blocked["trade_allowed"])
        self.assertTrue(allowed["trade_allowed"])

    def test_high_confidence_does_not_override_risk(self) -> None:
        result = evaluate_trade_eligibility(
            signal_data={"agreement": 0.95, "volatility_score": 0.4, "regime": "trend_up"},
            confidence_score=0.99,
            min_confidence=0.6,
            min_agreement=0.6,
            allow_chop=True,
            volatility_bounds=(0.1, 0.8),
            risk_result={"allowed": False, "reason": "max_daily_loss reached", "position_size": 0.0},
            active_block_condition=False,
        )

        self.assertFalse(result["trade_allowed"])
        self.assertIn("risk guardrail", result["reason_if_blocked"])

    def test_missing_required_signal_data_blocks_safely(self) -> None:
        result = evaluate_trade_eligibility(
            signal_data={"regime": "trend_up"},
            confidence_score=0.8,
            min_confidence=0.6,
            min_agreement=0.6,
            allow_chop=True,
            volatility_bounds=(0.1, 0.8),
            risk_result={"allowed": True, "reason": "", "position_size": 0.4},
            active_block_condition=False,
        )

        self.assertFalse(result["trade_allowed"])
        self.assertIn("missing required signal data", result["reason_if_blocked"])

    def test_active_block_condition_blocks_trade(self) -> None:
        result = evaluate_trade_eligibility(
            signal_data={"agreement": 0.9, "volatility_score": 0.4, "regime": "trend_up"},
            confidence_score=0.8,
            min_confidence=0.6,
            min_agreement=0.6,
            allow_chop=True,
            volatility_bounds=(0.1, 0.8),
            risk_result={"allowed": True, "reason": "", "position_size": 0.4},
            active_block_condition=True,
        )

        self.assertFalse(result["trade_allowed"])
        self.assertIn("active block", result["reason_if_blocked"])
