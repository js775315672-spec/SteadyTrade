import unittest
from trade_costs import TradeCost, net_return

class CostTests(unittest.TestCase):
    def test_zero_cost(self):
        self.assertAlmostEqual(net_return(100, 101, TradeCost(0,0,0,0)), .01)
    def test_costs_reduce_return(self):
        self.assertLess(net_return(100, 101, TradeCost(.001,.001,.001,.001)), .01)
    def test_bad_input(self):
        with self.assertRaises(ValueError):
            TradeCost(-.1,0,0,0)
        with self.assertRaises(ValueError):
            net_return(0,100,TradeCost(0,0,0,0))
if __name__ == "__main__":
    unittest.main()
