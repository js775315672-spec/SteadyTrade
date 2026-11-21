"""Research-only validated walk-forward entry point; no orders."""
from quality_gated_research import evaluate_quality_gated_archive
from walkforward_audit import audit_oos_reports


def validated_research(path, *, interval="1m", **kwargs):
    result = evaluate_quality_gated_archive(path, interval=interval, **kwargs)
    result["independent_oos_audit"] = audit_oos_reports(
        result["folds"], n_rows=result["data_rows"])
    return result
