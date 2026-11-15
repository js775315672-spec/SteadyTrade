import math
import unittest
from trade_costs import TradeCost, net_return

class CostEdgeCases(unittest.TestCase):
    def test_flat_price_with_costs_is_negative(self):
        costs = TradeCost(.001, .001, .001, .001)
        self.assertLess(net_return(100, 100, costs), 0)

    def test_break_even_price_accounts_for_costs(self):
        costs = TradeCost(.001, .001, .001, .001)
        entry = 100
        exit_price = entry * (1 + costs.entry_slippage_rate) * (1 + costs.entry_fee_rate) / ((1 - costs.exit_slippage_rate) * (1 - costs.exit_fee_rate))
        self.assertAlmostEqual(net_return(entry, exit_price, costs), 0, places=12)

    def test_negative_and_zero_exit_rejected(self):
        with self.assertRaises(ValueError):
            net_return(100, -1, TradeCost(0,0,0,0))
        with self.assertRaises(ValueError):
            net_return(100, 0, TradeCost(0,0,0,0))

    def test_invalid_cost_rate_rejected(self):
        with self.assertRaises(ValueError):
            TradeCost(1,0,0,0)
        with self.assertRaises(ValueError):
            TradeCost(math.nan,0,0,0)
