import math
import unittest
from trade_costs import TradeCost, net_return, target_exit_price

class TargetExitTests(unittest.TestCase):
    def test_one_percent_net_target(self):
        costs = TradeCost(.001, .001, .0005, .0005)
        exit_price = target_exit_price(100, .01, costs)
        self.assertGreater(exit_price, 101)
        self.assertAlmostEqual(net_return(100, exit_price, costs), .01, places=12)

    def test_zero_cost_target(self):
        costs = TradeCost(0, 0, 0, 0)
        self.assertAlmostEqual(target_exit_price(100, .01, costs), 101)

    def test_invalid_target_rejected(self):
        costs = TradeCost(0, 0, 0, 0)
        for target in (math.nan, math.inf, -1.01):
            with self.subTest(target=target):
                with self.assertRaises(ValueError):
                    target_exit_price(100, target, costs)

    def test_invalid_entry_rejected(self):
        with self.assertRaises(ValueError):
            target_exit_price(0, .01, TradeCost(0,0,0,0))
