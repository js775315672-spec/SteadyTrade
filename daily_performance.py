"""Daily marked-to-market performance summary from a backtest equity curve.

Unlike realized-only accounting, open positions are included at estimated
liquidation value. Missing calendar dates are not forward-filled.
"""
from datetime import datetime
import math

def daily_equity_report(equity_curve, initial_equity):
    if not math.isfinite(initial_equity) or initial_equity <= 0:
        raise ValueError("initial_equity must be finite and positive")
    daily = {}
    previous_time = None
    for timestamp, equity in equity_curve:
        if not isinstance(timestamp, datetime):
            raise ValueError("timestamps must be datetime")
        if previous_time is not None and timestamp <= previous_time:
            raise ValueError("timestamps must increase")
        if not math.isfinite(equity) or equity < 0:
            raise ValueError("equity must be finite and nonnegative")
        daily[timestamp.date()] = equity
        previous_time = timestamp
    results = []
    prior = initial_equity
    peak = initial_equity
    max_drawdown = 0.0
    for day, equity in daily.items():
        daily_return = equity / prior - 1 if prior > 0 else (0.0 if equity == 0 else math.inf)
        peak = max(peak, equity)
        drawdown = equity / peak - 1
        max_drawdown = min(max_drawdown, drawdown)
        results.append({"date": day.isoformat(), "equity": equity,
                        "daily_return": daily_return, "drawdown": drawdown})
        prior = equity
    return {"days": results, "total_return": prior / initial_equity - 1,
            "max_daily_drawdown": max_drawdown}
