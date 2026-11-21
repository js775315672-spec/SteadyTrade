import unittest
from offline_backtest import Candle, backtest, ema_signals

class OfflineBacktestTests(unittest.TestCase):
    def setUp(self):
        self.c = [Candle(100,110,90,100), Candle(110,120,100,115), Candle(120,130,110,125)]

    def test_next_bar_execution(self):
        r = backtest(self.c,[True,False,False],fee_rate=0,slippage_rate=0)
        self.assertAlmostEqual(r["final_equity"],10000*120/110)
        self.assertEqual(r["trade_count"],1)

    def test_costs_reduce_equity(self):
        a = backtest(self.c,[True,False,False],fee_rate=0,slippage_rate=0)
        b = backtest(self.c,[True,False,False],fee_rate=.001,slippage_rate=.002)
        self.assertLess(b["final_equity"],a["final_equity"])

    def test_last_signal_never_fills(self):
        r = backtest(self.c,[False,False,True])
        self.assertEqual(r["trade_count"],0)
        self.assertEqual(r["final_equity"],10000)

    def test_invalid_candle(self):
        with self.assertRaises(ValueError):
            backtest([Candle(100,90,110,100)],[False])

    def test_boolean_signals_only(self):
        with self.assertRaises(ValueError):
            backtest(self.c,[1,0,1])

    def test_ema_warmup(self):
        self.assertEqual(ema_signals(self.c,1,3)[:2],[False,False])

    def test_ema_invalid_parameters(self):
        with self.assertRaises(ValueError):
            ema_signals(self.c,5,3)

    def test_final_liquidation(self):
        r = backtest(self.c,[True,True,True],fee_rate=0,slippage_rate=0)
        self.assertAlmostEqual(r["final_equity"],10000*125/110)

    def test_no_trades(self):
        self.assertEqual(backtest(self.c,[False]*3)["max_drawdown"],0)

if __name__ == "__main__":
    unittest.main()
