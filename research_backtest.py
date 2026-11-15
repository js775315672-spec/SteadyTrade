"""Small, deterministic research backtester for timestamped OHLCV bars.

Signals are decided at a bar close, then executed at the *next* bar open.
Long-only, all-in/all-out, no leverage or exchange connectivity. This is
not an intrabar stop-loss simulator or an execution-quality model.
"""
import csv
import math
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from trade_costs import TradeCost

@dataclass(frozen=True)
class Bar:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

def load_csv(path):
    """Require timestamp,open,high,low,close,volume; timestamps ISO 8601."""
    bars = []
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            bar = Bar(datetime.fromisoformat(row["timestamp"]), *(
                float(row[field]) for field in ("open", "high", "low", "close", "volume")
            ))
            bars.append(bar)
    validate_bars(bars)
    return bars

def validate_bars(bars):
    previous = None
    for bar in bars:
        values = (bar.open, bar.high, bar.low, bar.close, bar.volume)
        if any(not math.isfinite(v) for v in values):
            raise ValueError("Bar fields must be finite")
        if min(bar.open, bar.high, bar.low, bar.close) <= 0 or bar.volume < 0:
            raise ValueError("Invalid price or volume")
        if bar.low > min(bar.open, bar.close) or bar.high < max(bar.open, bar.close):
            raise ValueError("Inconsistent OHLC")
        if previous is not None and bar.timestamp <= previous:
            raise ValueError("Timestamps must be strictly increasing")
        previous = bar.timestamp

def sma_crossover(bars, fast_window, slow_window, costs, initial_cash=1000.0):
    """SMA crossover with next-open fills and end-of-series marked equity.

    Equity curve is recorded at each close; terminal holdings are valued at
    close with hypothetical liquidation costs but NOT force-sold.
    """
    validate_bars(bars)
    if not isinstance(fast_window, int) or not isinstance(slow_window, int) or not 1 <= fast_window < slow_window:
        raise ValueError("Require integer 1 <= fast_window < slow_window")
    if not isinstance(costs, TradeCost):
        raise TypeError("costs must be TradeCost")
    if not math.isfinite(initial_cash) or initial_cash <= 0:
        raise ValueError("Initial cash must be positive and finite")
    cash, units, pending = initial_cash, 0.0, None
    curve, trades = [], []
    closes = []
    entry_total = None
    for bar in bars:
        if pending == "buy" and cash > 0:
            price = bar.open * (1 + costs.entry_slippage_rate)
            entry_total = cash
            units = cash / (price * (1 + costs.entry_fee_rate))
            cash = 0.0
        elif pending == "sell" and units > 0:
            proceeds = units * bar.open * (1 - costs.exit_slippage_rate) * (1 - costs.exit_fee_rate)
            trades.append((bar.timestamp, proceeds / entry_total - 1))
            cash, units, entry_total = proceeds, 0.0, None
        pending = None
        closes.append(bar.close)
        if len(closes) >= slow_window + 1:
            prev_fast = sum(closes[-fast_window-1:-1]) / fast_window
            prev_slow = sum(closes[-slow_window-1:-1]) / slow_window
            now_fast = sum(closes[-fast_window:]) / fast_window
            now_slow = sum(closes[-slow_window:]) / slow_window
            if units == 0 and prev_fast <= prev_slow and now_fast > now_slow:
                pending = "buy"
            elif units > 0 and prev_fast >= prev_slow and now_fast < now_slow:
                pending = "sell"
        marked = cash + units * bar.close * (1 - costs.exit_slippage_rate) * (1 - costs.exit_fee_rate)
        curve.append((bar.timestamp, marked))
    peak, mdd = initial_cash, 0.0
    for _, equity in curve:
        peak = max(peak, equity)
        mdd = min(mdd, equity / peak - 1)
    return {"equity_curve": curve, "closed_trades": trades,
            "terminal_marked_equity": curve[-1][1] if curve else initial_cash,
            "max_drawdown": mdd, "open_position": units > 0}
