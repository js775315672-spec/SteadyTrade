"""Local, checksum-gated single-month research; no downloads or orders."""
from pathlib import Path
from archive_provenance import monthly_spot_manifest, verify_checksum
from validated_research import validated_research


def evaluate_verified_month(zip_path, checksum_text, *, symbol, interval,
                            year, month, **research_kwargs):
    manifest=monthly_spot_manifest(symbol,interval,year,month)
    path=Path(zip_path)
    if path.name!=manifest["filename"]:
        raise ValueError("archive filename does not match manifest")
    proof=verify_checksum(path,checksum_text)
    # Only fixed-duration intervals are supported by quality validation.
    result=validated_research(path,interval=interval,
                              timestamp_unit=manifest["timestamp_unit"],
                              **research_kwargs)
    result["provenance"]={"source":manifest["source"],
                          "url":manifest["url"],"sha256":proof["sha256"],
                          "checksum_verified":True}
    return result
