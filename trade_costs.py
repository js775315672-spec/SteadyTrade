"""Spot trade cost accounting. Research only; no exchange connectivity."""
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class TradeCost:
    entry_fee_rate: float
    exit_fee_rate: float
    entry_slippage_rate: float
    exit_slippage_rate: float

    def __post_init__(self):
        values = (self.entry_fee_rate, self.exit_fee_rate,
                  self.entry_slippage_rate, self.exit_slippage_rate)
        if any(not math.isfinite(value) or not 0 <= value < 1 for value in values):
            raise ValueError("Cost rates must be in [0, 1)")

def net_return(entry_price: float, exit_price: float, costs: TradeCost) -> float:
    """Round-trip return on entry cash, accounting for fees and slippage."""
    if (not math.isfinite(entry_price) or not math.isfinite(exit_price)
            or entry_price <= 0 or exit_price <= 0):
        raise ValueError("Prices must be positive")
    entry_cost = entry_price * (1 + costs.entry_slippage_rate) * (1 + costs.entry_fee_rate)
    exit_proceeds = exit_price * (1 - costs.exit_slippage_rate) * (1 - costs.exit_fee_rate)
    return exit_proceeds / entry_cost - 1

def target_exit_price(entry_price: float, target_net_return: float, costs: TradeCost) -> float:
    """Minimum quoted exit price for a specified net round-trip return.

    Returns a theoretical threshold, not a fill guarantee or trading signal.
    """
    if not math.isfinite(entry_price) or entry_price <= 0:
        raise ValueError("Entry price must be finite and positive")
    if not math.isfinite(target_net_return) or target_net_return < -1:
        raise ValueError("Target return must be finite and at least -100%")
    entry_cost = entry_price * (1 + costs.entry_slippage_rate) * (1 + costs.entry_fee_rate)
    exit_factor = (1 - costs.exit_slippage_rate) * (1 - costs.exit_fee_rate)
    return (1 + target_net_return) * entry_cost / exit_factor
