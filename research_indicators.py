"""Pure offline, causal, close-only research indicators; no exchange access."""
from math import isfinite


def _prices(values):
    prices = list(values)
    if not prices or any(not isinstance(x, (float, int)) or isinstance(x, bool) or not isfinite(x) or x <= 0 for x in prices):
        raise ValueError('prices must be nonempty positive finite numbers')
    return prices


def ema(values, period):
    prices = _prices(values)
    if type(period) is not int or period < 1:
        raise ValueError('period must be positive integer')
    alpha = 2 / (period + 1)
    current = None
    result = []
    for i, price in enumerate(prices):
        current = price if current is None else alpha * price + (1 - alpha) * current
        result.append(current if i >= period - 1 else None)
    return result


def rsi(values, period=14):
    prices = _prices(values)
    if type(period) is not int or period < 1:
        raise ValueError('period must be positive integer')
    result = [None] * len(prices)
    if len(prices) <= period:
        return result
    changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gain = sum(max(d, 0) for d in changes[:period]) / period
    loss = sum(max(-d, 0) for d in changes[:period]) / period
    def value(g, l):
        if l == 0:
            return 50.0 if g == 0 else 100.0
        return 100 - 100 / (1 + g/l)
    result[period] = value(gain, loss)
    for i in range(period+1, len(prices)):
        d = changes[i-1]
        gain = (gain * (period-1) + max(d, 0)) / period
        loss = (loss * (period-1) + max(-d, 0)) / period
        result[i] = value(gain, loss)
    return result


def macd(values, fast=12, slow=26, signal=9):
    prices = _prices(values)
    if not all(type(p) is int and p > 0 for p in (fast, slow, signal)) or fast >= slow:
        raise ValueError('require positive integer periods fast < slow')
    fast_line, slow_line = ema(prices, fast), ema(prices, slow)
    line = [None if a is None or b is None else a-b for a,b in zip(fast_line, slow_line)]
    valid = [x for x in line if x is not None]
    signal_values = []
    current = None
    alpha = 2 / (signal + 1)
    for i, value in enumerate(valid):
        current = value if current is None else alpha * value + (1 - alpha) * current
        signal_values.append(current if i >= signal - 1 else None)
    offset = len(line)-len(valid)
    signal_line = [None]*offset + signal_values
    histogram = [None if a is None or b is None else a-b for a,b in zip(line, signal_line)]
    return {'macd':line, 'signal':signal_line, 'histogram':histogram}
