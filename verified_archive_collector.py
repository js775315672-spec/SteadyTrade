"""Opt-in public Binance archive collector. No credentials, orders or background jobs.

Network access occurs ONLY when download_verified_month is explicitly called.
Every file must match its official checksum before becoming usable.
"""
from pathlib import Path
from urllib.request import urlopen
import os
import tempfile

from archive_provenance import monthly_spot_manifest, verify_checksum


def _fetch_limited(url, destination, max_bytes, opener):
    received = 0
    with opener(url, timeout=30) as response, open(destination, "wb") as output:
        while True:
            chunk = response.read(min(1024 * 1024, max_bytes + 1 - received))
            if not chunk:
                break
            received += len(chunk)
            if received > max_bytes:
                raise ValueError("download exceeds byte limit")
            output.write(chunk)
    return received


def download_verified_month(symbol, interval, year, month, output_dir, *,
                            max_zip_bytes=250_000_000, opener=urlopen):
    """Download a single monthly Spot ZIP and CHECKSUM into a local directory.

    Existing destination is never overwritten. Temp files are removed on failure.
    Caller must supply an explicit output directory. Returns SHA256 receipt.
    """
    if type(max_zip_bytes) is not int or max_zip_bytes < 1:
        raise ValueError("invalid max_zip_bytes")
    manifest = monthly_spot_manifest(symbol, interval, year, month)
    folder = Path(output_dir)
    if not folder.is_dir():
        raise ValueError("output_dir must already exist")
    target = folder / manifest["filename"]
    if target.exists():
        raise FileExistsError(target)
    with tempfile.TemporaryDirectory(dir=folder, prefix=".archive-staging-") as tmp:
        tmp_zip = Path(tmp) / manifest["filename"]
        tmp_checksum = Path(tmp) / (manifest["filename"] + ".CHECKSUM")
        _fetch_limited(manifest["url"], tmp_zip, max_zip_bytes, opener)
        _fetch_limited(manifest["checksum_url"], tmp_checksum, 4096, opener)
        checksum = tmp_checksum.read_text(encoding="utf-8")
        receipt = verify_checksum(tmp_zip, checksum)
        # Atomic hard link within the same directory filesystem. No overwrite.
        os.link(tmp_zip, target)
        return {"path":str(target), "sha256":receipt["sha256"],
                "bytes":target.stat().st_size, "source_url":manifest["url"],
                "timestamp_unit":manifest["timestamp_unit"],
                "verified":True}
