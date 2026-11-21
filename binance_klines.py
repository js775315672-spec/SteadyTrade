"""Offline Binance public kline ZIP/CSV adapter. No API, credentials or orders."""
import csv
import io
import math
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True)
class Kline:
    open_time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

def parse_klines(rows, timestamp_unit="ms"):
    """Read 12-column Binance archive rows. Time is UTC candle OPEN time."""
    if timestamp_unit not in ("ms", "us"):
        raise ValueError("timestamp_unit must be ms or us")
    scale = 1000 if timestamp_unit == "ms" else 1000000
    result, previous = [], None
    for row in rows:
        if not row:
            continue
        if len(row) != 12:
            raise ValueError("Expected 12 Binance kline fields")
        try:
            start, end = int(row[0]), int(row[6])
            op, hi, lo, cl, vol = (float(row[i]) for i in (1, 2, 3, 4, 5))
            if any(not math.isfinite(v) for v in (op, hi, lo, cl, vol)):
                raise ValueError("Nonfinite OHLCV")
            if min(op, hi, lo, cl) <= 0 or vol < 0 or lo > min(op, cl) or hi < max(op, cl):
                raise ValueError("Invalid OHLCV")
            if end <= start or (previous is not None and start <= previous):
                raise ValueError("Invalid timestamp order")
            timestamp = datetime.fromtimestamp(start / scale, tz=timezone.utc)
        except (TypeError, OverflowError, OSError) as exc:
            raise ValueError("Invalid Binance kline record") from exc
        result.append(Kline(timestamp, op, hi, lo, cl, vol))
        previous = start
    return result

def read_zip_csv(path, timestamp_unit="ms", max_uncompressed_bytes=250000000):
    """Read a local ZIP with exactly one CSV member, with size limit."""
    with zipfile.ZipFile(path) as archive:
        members = [m for m in archive.infolist() if not m.is_dir()]
        if len(members) != 1 or not members[0].filename.lower().endswith(".csv"):
            raise ValueError("ZIP must contain exactly one CSV")
        if members[0].file_size > max_uncompressed_bytes:
            raise ValueError("Uncompressed CSV exceeds size limit")
        with archive.open(members[0]) as raw:
            return parse_klines(csv.reader(io.TextIOWrapper(raw, encoding="utf-8-sig", newline="")),
                                timestamp_unit=timestamp_unit)
