"""Unit tests for Stage 6A trade memory."""

import json
import os
import tempfile
import unittest

from hermes.learning.trade_memory import (
    append_completed_trade,
    load_trade_memory,
    validate_completed_trade,
)


class TradeMemoryTests(unittest.TestCase):
    def _valid_trade(self) -> dict:
        return {
            "timestamp": "2026-04-25T12:00:00Z",
            "date": "2026-04-25",
            "hour": 12,
            "sequence_value": 0.8,
            "amd_value": 0.75,
            "combined_value": 0.78,
            "agreement": 0.9,
            "confidence": 0.85,
            "regime": "trend",
            "momentum_score": 0.7,
            "volatility_score": 0.3,
            "outcome": "win",
            "pnl": 120.5,
            "entry_price": 430.25,
            "exit_price": 433.75,
        }

    def test_valid_completed_trade_passes_validation(self) -> None:
        validate_completed_trade(self._valid_trade())

    def test_missing_required_field_rejected(self) -> None:
        trade = self._valid_trade()
        del trade["timestamp"]

        with self.assertRaises(ValueError):
            validate_completed_trade(trade)

    def test_invalid_outcome_rejected(self) -> None:
        trade = self._valid_trade()
        trade["outcome"] = "partial"

        with self.assertRaises(ValueError):
            validate_completed_trade(trade)

    def test_non_numeric_numeric_field_rejected(self) -> None:
        trade = self._valid_trade()
        trade["confidence"] = "high"

        with self.assertRaises(ValueError):
            validate_completed_trade(trade)

    def test_bool_numeric_field_rejected(self) -> None:
        trade = self._valid_trade()
        trade["pnl"] = True

        with self.assertRaises(ValueError):
            validate_completed_trade(trade)

    def test_append_creates_json_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, "trade_memory.json")
            trade = self._valid_trade()

            append_completed_trade(path, trade)

            self.assertTrue(os.path.exists(path))
            with open(path, "r", encoding="utf-8") as file_obj:
                stored = json.load(file_obj)
            self.assertEqual(stored, [trade])

    def test_append_preserves_existing_trades(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, "trade_memory.json")
            first_trade = self._valid_trade()
            second_trade = self._valid_trade()
            second_trade["timestamp"] = "2026-04-25T13:00:00Z"

            append_completed_trade(path, first_trade)
            append_completed_trade(path, second_trade)

            with open(path, "r", encoding="utf-8") as file_obj:
                stored = json.load(file_obj)
            self.assertEqual(stored, [first_trade, second_trade])

    def test_load_missing_file_returns_empty_list(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, "missing.json")

            self.assertEqual(load_trade_memory(path), [])

    def test_invalid_json_raises_value_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, "trade_memory.json")
            with open(path, "w", encoding="utf-8") as file_obj:
                file_obj.write("{invalid json")

            with self.assertRaises(ValueError):
                load_trade_memory(path)

    def test_non_list_json_raises_value_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, "trade_memory.json")
            with open(path, "w", encoding="utf-8") as file_obj:
                json.dump({"not": "a list"}, file_obj)

            with self.assertRaises(ValueError):
                load_trade_memory(path)

    def test_deterministic_load_after_append(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, "trade_memory.json")
            trade = self._valid_trade()

            append_completed_trade(path, trade)

            first = load_trade_memory(path)
            second = load_trade_memory(path)

            self.assertEqual(first, second)
            self.assertEqual(first, [trade])


if __name__ == "__main__":
    unittest.main()
