"""Fail-closed quality-gated archive evaluation. Research only."""
from binance_klines import read_zip_csv
from archive_quality import validate_klines
from offline_walkforward import evaluate_archive


def evaluate_quality_gated_archive(path, *, interval="1m",
                                   timestamp_unit="ms", **kwargs):
    rows = read_zip_csv(path, timestamp_unit=timestamp_unit)
    quality = validate_klines(rows, interval=interval)
    report = evaluate_archive(path, timestamp_unit=timestamp_unit, **kwargs)
    report["data_quality"] = quality
    return report
