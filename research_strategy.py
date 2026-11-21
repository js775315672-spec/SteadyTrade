"""Research-only indicator-to-backtest adapter. No orders or network."""
from offline_backtest import backtest
from research_indicators import ema, rsi, macd


def strategy_signals(candles, strategy="ema", **parameters):
    """Signals calculated using completed bar i; engine fills at open i+1.

    Warm-up bars and missing indicators never open a position.
    """
    candles = list(candles)
    if not candles:
        raise ValueError("candles must be nonempty")
    prices = [c.close for c in candles]
    if strategy == "ema":
        fast = parameters.pop("fast", 12)
        slow = parameters.pop("slow", 26)
        if parameters or type(fast) is not int or type(slow) is not int or fast < 1 or fast >= slow:
            raise ValueError("EMA requires 1 <= fast < slow")
        a, b = ema(prices, fast), ema(prices, slow)
        return [x is not None and y is not None and x > y for x,y in zip(a,b)]
    if strategy == "rsi":
        period = parameters.pop("period", 14)
        threshold = parameters.pop("threshold", 50)
        if parameters or type(threshold) not in (float,int) or not 0 < threshold < 100:
            raise ValueError("invalid RSI parameters")
        values = rsi(prices, period)
        return [x is not None and x > threshold for x in values]
    if strategy == "macd":
        values = macd(prices, **parameters)
        return [x is not None and x > 0 for x in values["histogram"]]
    raise ValueError("unknown strategy")


def evaluate(candles, strategy="ema", initial_cash=10000., fee_rate=.001,
             slippage_rate=.0005, **parameters):
    candles = list(candles)
    signals = strategy_signals(candles, strategy=strategy, **parameters)
    result = backtest(candles, signals, initial_cash=initial_cash,
                      fee_rate=fee_rate, slippage_rate=slippage_rate)
    result["strategy"] = strategy
    result["warmup_bars"] = next((i for i, signal in enumerate(signals) if signal), len(signals))
    return result
