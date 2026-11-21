import unittest
from research_indicators import ema, rsi, macd

class IndicatorTests(unittest.TestCase):
    def test_ema_warmup(self):
        self.assertEqual(ema([1,2,3,4], 3)[:2], [None,None])
    def test_ema_constant(self):
        self.assertEqual(ema([5]*12, 4)[-1], 5)
    def test_rsi_constant(self):
        self.assertEqual(rsi([10]*20)[-1], 50)
    def test_rsi_rising(self):
        self.assertEqual(rsi(list(range(1,30)))[-1], 100)
    def test_rsi_falling(self):
        self.assertEqual(rsi(list(range(30,0,-1)))[-1], 0)
    def test_macd_constant(self):
        self.assertAlmostEqual(macd([10]*40)['histogram'][-1], 0)
    def test_macd_warmup(self):
        x=macd([10]*40)
        self.assertIsNone(x['macd'][24])
        self.assertIsNone(x['signal'][32])
        self.assertIsNotNone(x['signal'][33])
    def test_causal_prefix(self):
        x=[100+i%7 for i in range(80)]
        for fn in (lambda a: ema(a,8), rsi, lambda a: macd(a)['histogram']):
            self.assertEqual(fn(x)[:50],fn(x[:50]))
    def test_bad_prices(self):
        for p in ([], [1,0], [1,float('nan')], [1,float('inf')]):
            with self.assertRaises(ValueError): rsi(p)
    def test_bad_periods(self):
        with self.assertRaises(ValueError): ema([1,2],True)
        with self.assertRaises(ValueError): macd([1,2],fast=20,slow=10)
if __name__ == '__main__': unittest.main()
