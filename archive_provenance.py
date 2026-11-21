"""Offline Binance spot monthly archive provenance and checksum verification.

Does not download, call exchanges, place orders or commit market data.
"""
import hashlib
import re
from datetime import date
from pathlib import Path

SYMBOL_RE = re.compile(r"^[A-Z0-9]{3,20}$")
INTERVALS = frozenset(("1s","1m","3m","5m","15m","30m","1h","2h",
                       "4h","6h","8h","12h","1d","3d","1w","1mo"))


def monthly_spot_manifest(symbol, interval, year, month):
    if not isinstance(symbol,str) or not SYMBOL_RE.fullmatch(symbol):
        raise ValueError("invalid symbol")
    if interval not in INTERVALS:
        raise ValueError("invalid interval")
    if type(year) is not int or not 2017 <= year <= 2100:
        raise ValueError("invalid year")
    if type(month) is not int or not 1 <= month <= 12:
        raise ValueError("invalid month")
    name=f"{symbol}-{interval}-{year:04d}-{month:02d}.zip"
    base=f"https://data.binance.vision/data/spot/monthly/klines/{symbol}/{interval}/{name}"
    # Spot archives switched from milliseconds to microseconds on 2025-01-01.
    unit="us" if (year,month)>=(2025,1) else "ms"
    return {"symbol":symbol,"interval":interval,"year":year,"month":month,
            "filename":name,"url":base,"checksum_url":base+".CHECKSUM",
            "timestamp_unit":unit,"source":"Binance public Spot monthly klines"}


def manifests(symbol,interval,start_year,start_month,end_year,end_month):
    start=date(start_year,start_month,1)
    end=date(end_year,end_month,1)
    if end < start:
        raise ValueError("end before start")
    out=[]
    year,month=start.year,start.month
    while (year,month)<=(end.year,end.month):
        out.append(monthly_spot_manifest(symbol,interval,year,month))
        month+=1
        if month==13:
            year,month=year+1,1
    return out


def verify_checksum(zip_path, checksum_text):
    """Verify sha256sum-formatted Binance .CHECKSUM against local ZIP bytes."""
    path=Path(zip_path)
    match=re.fullmatch(r"([0-9a-fA-F]{64})\s+\*?([^\r\n/\\]+)\s*",checksum_text)
    if match is None or match.group(2)!=path.name:
        raise ValueError("invalid checksum record or filename")
    digest=hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b""):
            digest.update(chunk)
    if digest.hexdigest().lower()!=match.group(1).lower():
        raise ValueError("SHA256 mismatch")
    return {"filename":path.name,"sha256":digest.hexdigest(),"verified":True}
