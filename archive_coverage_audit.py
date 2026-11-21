"""Offline multi-month coverage and continuity audit; no trading."""
from datetime import timedelta
from pathlib import Path

from archive_provenance import monthly_spot_manifest, verify_checksum
from archive_quality import validate_klines
from binance_klines import read_zip_csv


def audit_months(folder, symbol, interval, year_months, checksum_by_month):
    """Verify each local ZIP against supplied official CHECKSUM text.

    Each month must contain data; all adjacent candle timestamps must be
    continuous. Coverage bounds are reported, not guessed as complete.
    """
    root = Path(folder)
    months = list(year_months)
    if not months:
        raise ValueError("no months")
    if months != sorted(set(months)):
        raise ValueError("months must be sorted and unique")
    reports = []
    previous_last = None
    for year, month in months:
        m = monthly_spot_manifest(symbol, interval, year, month)
        path = root / m["filename"]
        proof = verify_checksum(path, checksum_by_month[(year,month)])
        rows = read_zip_csv(path, timestamp_unit=m["timestamp_unit"])
        quality = validate_klines(rows, interval=interval)
        if previous_last is not None:
            seconds = {"1s":1,"1m":60,"3m":180,"5m":300,"15m":900,
                       "30m":1800,"1h":3600,"2h":7200,"4h":14400,
                       "6h":21600,"8h":28800,"12h":43200,"1d":86400}
            if interval not in seconds:
                raise ValueError("unsupported fixed-duration interval")
            if rows[0].open_time - previous_last != timedelta(seconds=seconds[interval]):
                raise ValueError("cross-month missing, duplicated or unordered candle")
        previous_last = rows[-1].open_time
        reports.append({"year":year,"month":month,"rows":len(rows),
                        "sha256":proof["sha256"],"quality":quality})
    return {"verified_months":len(reports),"months":reports,
            "first_open_utc":reports[0]["quality"]["start_utc"],
            "last_open_utc":reports[-1]["quality"]["end_utc"],
            "strategy_evaluation":None}
