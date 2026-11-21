import unittest
from offline_backtest import Candle
from research_strategy import strategy_signals, evaluate


def candles(values):
    return [Candle(v, v, v, v) for v in values]


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.bars = candles([100+i*0.5+(i%5) for i in range(100)])

    def test_all_strategies_offline(self):
        for strategy in ("ema", "rsi", "macd"):
            with self.subTest(strategy=strategy):
                r = evaluate(self.bars, strategy=strategy)
                self.assertGreater(r["final_equity"], 0)
                self.assertEqual(len(r["equity_curve"]),len(self.bars))

    def test_prefix_causality(self):
        for strategy in ("ema", "rsi", "macd"):
            with self.subTest(strategy=strategy):
                self.assertEqual(strategy_signals(self.bars,strategy)[:70],
                                 strategy_signals(self.bars[:70],strategy))

    def test_last_bar_signal_does_not_fill(self):
        bars = candles([100,100,100,200])
        self.assertEqual(evaluate(bars, strategy="ema", fast=1, slow=3,
                                  fee_rate=0, slippage_rate=0)["trade_count"], 0)

    def test_fee_slippage_non_improving(self):
        bars = candles([100+i for i in range(50)])
        a = evaluate(bars, "ema", fast=2, slow=5, fee_rate=0, slippage_rate=0)
        b = evaluate(bars, "ema", fast=2, slow=5, fee_rate=.001, slippage_rate=.001)
        self.assertLessEqual(b["final_equity"], a["final_equity"])

    def test_invalid_strategy(self):
        with self.assertRaises(ValueError):
            evaluate(self.bars, "unsupported")

    def test_unknown_parameters_rejected(self):
        with self.assertRaises(ValueError):
            evaluate(self.bars, "ema", fast=2, slow=5, future=10)

    def test_rsi_warmup(self):
        self.assertFalse(any(strategy_signals(self.bars, "rsi")[:14]))


if __name__ == "__main__":
    unittest.main()
