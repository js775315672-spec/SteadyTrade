import math
import unittest
from datetime import date
from realized_equity import ClosedTrade, daily_realized_equity

class RealizedEquityTests(unittest.TestCase):
    def test_compounding_and_daily_returns(self):
        trades = [
            ClosedTrade(date(2026, 1, 1), .01),
            ClosedTrade(date(2026, 1, 1), .02),
            ClosedTrade(date(2026, 1, 2), -.01),
        ]
        result = daily_realized_equity(trades, 100)
        self.assertEqual(len(result), 2)
        self.assertAlmostEqual(result[0][1], 103.02)
        self.assertAlmostEqual(result[0][2], .0302)
        self.assertAlmostEqual(result[1][1], 101.9898)
        self.assertAlmostEqual(result[1][2], -.01)

    def test_partial_allocation(self):
        result = daily_realized_equity([ClosedTrade(date(2026,1,1), .10, .5)], 100)
        self.assertAlmostEqual(result[0][1], 105)

    def test_empty_trades(self):
        self.assertEqual(daily_realized_equity([], 100), [])

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            daily_realized_equity([], 0)
        for bad in (math.nan, math.inf, -1.01):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    daily_realized_equity([ClosedTrade(date(2026,1,1), bad)], 100)

    def test_sorted_days(self):
        result = daily_realized_equity([
            ClosedTrade(date(2026,1,2), .02),
            ClosedTrade(date(2026,1,1), .01),
        ], 100)
        self.assertEqual([r[0] for r in result], [date(2026,1,1), date(2026,1,2)])
