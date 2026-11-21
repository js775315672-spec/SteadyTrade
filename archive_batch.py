"""Opt-in bounded monthly archive acquisition with auditable receipts.

No scheduled jobs, credentials, exchange orders or automatic research execution.
"""
from datetime import date
from pathlib import Path
import json

from archive_provenance import manifests
from verified_archive_collector import download_verified_month


def collect_months(symbol, interval, start_year, start_month, end_year, end_month,
                   output_dir, *, max_months=3, opener=None):
    plan = manifests(symbol, interval, start_year, start_month, end_year, end_month)
    if type(max_months) is not int or not 1 <= max_months <= 12:
        raise ValueError("max_months must be 1..12")
    if len(plan) > max_months:
        raise ValueError("requested months exceed explicit batch limit")
    folder = Path(output_dir)
    if not folder.is_dir():
        raise ValueError("output_dir must already exist")
    receipts = []
    for item in plan:
        kwargs = {"opener":opener} if opener is not None else {}
        receipt = download_verified_month(symbol, interval, item["year"],
                    item["month"], folder, **kwargs)
        receipts.append({"year":item["year"],"month":item["month"],
                         "sha256":receipt["sha256"],"bytes":receipt["bytes"],
                         "source_url":receipt["source_url"],
                         "timestamp_unit":receipt["timestamp_unit"],
                         "verified":receipt["verified"]})
    return {"symbol":symbol,"interval":interval,
            "requested_months":len(plan),"verified_months":len(receipts),
            "receipts":receipts,"data_committed_to_git":False}


def write_receipt(report, path):
    """Save a local JSON receipt, never overwrite an existing receipt."""
    target = Path(path)
    with target.open("x", encoding="utf-8") as output:
        json.dump(report, output, indent=2, sort_keys=True)
        output.write("\n")
    return str(target)
