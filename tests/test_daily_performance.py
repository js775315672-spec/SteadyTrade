import math
import unittest
from datetime import datetime
from daily_performance import daily_equity_report

class DailyPerformanceTests(unittest.TestCase):
    def test_last_observation_per_day(self):
        curve = [(datetime(2026,1,1,10), 101),
                 (datetime(2026,1,1,23), 102),
                 (datetime(2026,1,2,23), 99)]
        report = daily_equity_report(curve, 100)
        self.assertEqual(len(report["days"]), 2)
        self.assertAlmostEqual(report["days"][0]["daily_return"], .02)
        self.assertAlmostEqual(report["days"][1]["daily_return"], 99 / 102 - 1)
        self.assertAlmostEqual(report["total_return"], -.01)
        self.assertAlmostEqual(report["max_daily_drawdown"], 99 / 102 - 1)

    def test_empty_curve(self):
        report = daily_equity_report([], 100)
        self.assertEqual(report["days"], [])
        self.assertEqual(report["total_return"], 0)

    def test_invalid_equity(self):
        for value in (math.nan, math.inf, -1):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    daily_equity_report([(datetime(2026,1,1), value)], 100)

    def test_unsorted_timestamps(self):
        curve = [(datetime(2026,1,2), 100), (datetime(2026,1,1), 100)]
        with self.assertRaises(ValueError):
            daily_equity_report(curve, 100)
