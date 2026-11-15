import csv
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from research_backtest import Bar, load_csv, sma_crossover
from trade_costs import TradeCost

class BacktestTests(unittest.TestCase):
    def bars(self, prices):
        t = datetime(2026, 1, 1)
        return [Bar(t + timedelta(minutes=i), p, p, p, p, 100)
                for i, p in enumerate(prices)]

    def test_next_bar_fill_not_signal_bar(self):
        bars = self.bars([10, 9, 8, 10, 12, 14, 8, 6])
        result = sma_crossover(bars, 1, 2, TradeCost(0,0,0,0))
        self.assertEqual(len(result["closed_trades"]), 1)
        self.assertAlmostEqual(result["closed_trades"][0][1], 6 / 12 - 1)
        self.assertAlmostEqual(result["terminal_marked_equity"], 500)
        self.assertFalse(result["open_position"])

    def test_costs_reduce_marked_equity(self):
        bars = self.bars([10, 9, 8, 10, 12, 14, 8, 6])
        gross = sma_crossover(bars, 1, 2, TradeCost(0,0,0,0))
        net = sma_crossover(bars, 1, 2, TradeCost(.001,.001,.001,.001))
        self.assertLess(net["terminal_marked_equity"], gross["terminal_marked_equity"])

    def test_invalid_bar_rejected(self):
        bars = self.bars([10, 11])
        with self.assertRaises(ValueError):
            sma_crossover(bars[::-1], 1, 2, TradeCost(0,0,0,0))

    def test_csv_loader(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bars.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(["timestamp","open","high","low","close","volume"])
                writer.writerow(["2026-01-01T00:00:00",10,11,9,10,100])
            self.assertEqual(load_csv(path)[0].close, 10)

    def test_no_trade_and_empty_data(self):
        self.assertEqual(sma_crossover([], 1, 2, TradeCost(0,0,0,0))["terminal_marked_equity"], 1000)
        self.assertEqual(sma_crossover(self.bars([10,10,10]), 1, 2, TradeCost(0,0,0,0))["closed_trades"], [])
