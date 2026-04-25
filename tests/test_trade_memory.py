import json
import tempfile
import unittest
from pathlib import Path

from hermes.learning.trade_memory import load_trade_memory, log_completed_trade


class TestTradeMemory(unittest.TestCase):
    def _trade(self, timestamp: int, outcome: str = "win") -> dict:
        return {
            "status": "completed",
            "timestamp": timestamp,
            "sequence_value": 0.6,
            "amd_value": 0.7,
            "combined_value": 0.65,
            "agreement": 0.9,
            "confidence": 0.8,
            "regime": "trend_up",
            "momentum_score": 0.55,
            "volatility_score": 0.4,
            "outcome": outcome,
            "pnl": 12.0,
            "net_pnl": 10.5,
            "entry_price": 100.0,
            "exit_price": 102.0,
            "notes": "sample",
        }

    def test_logged_completed_trade_has_required_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "trades.json"
            log_completed_trade(path, self._trade(1700000000))
            data = load_trade_memory(path)

            self.assertEqual(len(data), 1)
            record = data[0]
            expected_keys = {
                "timestamp",
                "date",
                "hour",
                "sequence_value",
                "amd_value",
                "combined_value",
                "agreement",
                "confidence",
                "regime",
                "momentum_score",
                "volatility_score",
                "outcome",
                "pnl",
                "net_pnl",
                "entry_price",
                "exit_price",
                "notes",
            }
            self.assertEqual(set(record.keys()), expected_keys)

    def test_incomplete_trades_are_not_counted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "trades.json"
            incomplete = self._trade(1700000100)
            incomplete["status"] = "open"

            with self.assertRaisesRegex(ValueError, "incomplete"):
                log_completed_trade(path, incomplete)

            self.assertEqual(load_trade_memory(path), [])

    def test_completed_records_are_immutable_and_appended(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "trades.json"
            first = log_completed_trade(path, self._trade(1700000000, outcome="win"))
            second = log_completed_trade(path, self._trade(1700003600, outcome="loss"))

            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(len(data), 2)
            self.assertEqual(data[0], first)
            self.assertEqual(data[1], second)
