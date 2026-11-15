"""Research-only realized equity curve from closed trades.

Each trade return is net of fees and slippage and represents the return on
allocated notional. No orders are placed and no mark-to-market PnL is inferred.
"""
from dataclasses import dataclass
from datetime import date
import math

@dataclass(frozen=True)
class ClosedTrade:
    closed_on: date
    net_return: float
    allocation_fraction: float = 1.0

def daily_realized_equity(trades, initial_equity: float):
    """Return sorted (day, equity, daily_return) snapshots.

    Trade order within a day is preserved as provided. Compounding assumes
    each closed trade's allocated fraction is drawn from current equity.
    """
    if not math.isfinite(initial_equity) or initial_equity <= 0:
        raise ValueError("Initial equity must be finite and positive")
    indexed = list(enumerate(trades))
    for _, trade in indexed:
        if not isinstance(trade.closed_on, date):
            raise ValueError("closed_on must be a date")
        if not math.isfinite(trade.net_return) or trade.net_return < -1:
            raise ValueError("net_return must be finite and >= -1")
        if not math.isfinite(trade.allocation_fraction) or not 0 <= trade.allocation_fraction <= 1:
            raise ValueError("allocation_fraction must be in [0, 1]")
    indexed.sort(key=lambda pair: (pair[1].closed_on, pair[0]))
    equity = initial_equity
    results = []
    day = None
    day_start = initial_equity
    for _, trade in indexed:
        if day is not None and trade.closed_on != day:
            results.append((day, equity, equity / day_start - 1))
            day_start = equity
        day = trade.closed_on
        equity *= 1 + trade.allocation_fraction * trade.net_return
    if day is not None:
        results.append((day, equity, equity / day_start - 1))
    return results
