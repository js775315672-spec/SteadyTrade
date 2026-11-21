"""Strict offline kline integrity checks for research, without network or orders."""
from datetime import timedelta
from math import isfinite

INTERVAL_SECONDS = {
    "1s": 1, "1m": 60, "3m": 180, "5m": 300, "15m": 900,
    "30m": 1800, "1h": 3600, "2h": 7200, "4h": 14400,
    "6h": 21600, "8h": 28800, "12h": 43200, "1d": 86400,
}


def validate_klines(klines, *, interval="1m", min_rows=2):
    """Reject duplicates, missing fixed-interval candles, bad prices and volume.

    Assumes UTC fixed-duration intervals. Calendar month/week bars are
    intentionally unsupported. Does not infer missing candles or fill gaps.
    """
    if interval not in INTERVAL_SECONDS:
        raise ValueError("unsupported fixed-duration interval")
    if type(min_rows) is not int or min_rows < 2:
        raise ValueError("min_rows must be integer >= 2")
    rows = list(klines)
    if len(rows) < min_rows:
        raise ValueError("insufficient rows")
    delta = timedelta(seconds=INTERVAL_SECONDS[interval])
    prev = None
    for i, row in enumerate(rows):
        timestamp = row.open_time
        if timestamp.tzinfo is None or timestamp.utcoffset() != timedelta(0):
            raise ValueError(f"row {i}: timestamp must be UTC aware")
        fields = (row.open, row.high, row.low, row.close, row.volume)
        if any(not isfinite(v) for v in fields):
            raise ValueError(f"row {i}: nonfinite OHLCV")
        if min(fields[:4]) <= 0 or row.volume < 0:
            raise ValueError(f"row {i}: invalid OHLCV")
        if row.low > min(row.open, row.close) or row.high < max(row.open, row.close) or row.low > row.high:
            raise ValueError(f"row {i}: inconsistent OHLC")
        if prev is not None and timestamp - prev != delta:
            raise ValueError(f"row {i}: duplicate, unordered or missing candle")
        prev = timestamp
    return {"rows":len(rows), "interval":interval,
            "start_utc":rows[0].open_time.isoformat(),
            "end_utc":rows[-1].open_time.isoformat(),
            "gaps":0, "duplicates":0}
