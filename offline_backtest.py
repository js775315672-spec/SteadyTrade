"""Offline long-only next-bar backtest. No network, API keys or order execution."""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class Candle:
    open: float
    high: float
    low: float
    close: float

def ema_signals(candles, fast=3, slow=8):
    if not (type(fast) is int and type(slow) is int and 1 <= fast < slow):
        raise ValueError("require integer 1 <= fast < slow")
    a = b = None
    result = []
    for i, c in enumerate(candles):
        a = c.close if a is None else a + 2/(fast+1)*(c.close-a)
        b = c.close if b is None else b + 2/(slow+1)*(c.close-b)
        result.append(i >= slow-1 and a > b)
    return result

def backtest(candles, signals, initial_cash=10000., fee_rate=.001, slippage_rate=.0005):
    """Signal at close i executes at open i+1; final liquidation at last close.

    Equity values include estimated liquidation costs. No intrabar stop fills.
    """
    candles, signals = list(candles), list(signals)
    if not candles or len(candles) != len(signals) or any(type(s) is not bool for s in signals):
        raise ValueError("nonempty candles and equally sized boolean signals required")
    if not all(isfinite(x) for x in (initial_cash, fee_rate, slippage_rate)) or initial_cash <= 0 or not 0 <= fee_rate < 1 or not 0 <= slippage_rate < 1:
        raise ValueError("invalid cash or costs")
    for c in candles:
        values = (c.open, c.high, c.low, c.close)
        if not all(isfinite(x) and x > 0 for x in values) or c.low > min(c.open, c.close) or c.high < max(c.open, c.close):
            raise ValueError("invalid candle")
    cash, units, entry_total, trades, equity = float(initial_cash), 0., None, [], []
    for i, c in enumerate(candles):
        if i:
            desired = signals[i-1]
            if desired and units == 0:
                entry_total = cash
                units = cash / (c.open*(1+slippage_rate)*(1+fee_rate))
                cash = 0.
            elif not desired and units > 0:
                cash = units*c.open*(1-slippage_rate)*(1-fee_rate)
                trades.append({"exit_index":i, "net_pnl":cash-entry_total})
                units, entry_total = 0., None
        if i == len(candles)-1 and units > 0:
            cash = units*c.close*(1-slippage_rate)*(1-fee_rate)
            trades.append({"exit_index":i, "net_pnl":cash-entry_total})
            units, entry_total = 0., None
        equity.append(cash if units == 0 else units*c.close*(1-slippage_rate)*(1-fee_rate))
    peak, mdd = initial_cash, 0.
    for value in equity:
        peak = max(peak, value)
        mdd = min(mdd, value/peak-1)
    return {"final_equity":cash, "net_return":cash/initial_cash-1,
            "max_drawdown":mdd, "trade_count":len(trades),
            "trades":trades, "equity_curve":equity}
