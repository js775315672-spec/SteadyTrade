"""Independent structural audit for chronological walk-forward folds.

Does not claim train fitting, statistical significance or model improvement.
"""
from math import isfinite


def audit_folds(folds, n_rows, *, require_nonoverlapping_tests=True):
    if type(n_rows) is not int or n_rows < 1:
        raise ValueError("n_rows must be positive integer")
    folds = list(folds)
    if not folds:
        raise ValueError("at least one fold required")
    previous_test_end = None
    audited = []
    for i, fold in enumerate(folds):
        bounds = (fold.train_start, fold.train_end, fold.test_start, fold.test_end)
        if any(type(x) is not int for x in bounds):
            raise ValueError(f"fold {i}: noninteger boundary")
        a, b, c, d = bounds
        if not (0 <= a < b <= c < d <= n_rows):
            raise ValueError(f"fold {i}: invalid train/test ordering")
        if require_nonoverlapping_tests and previous_test_end is not None and c < previous_test_end:
            raise ValueError(f"fold {i}: overlapping OOS test windows")
        if previous_test_end is not None and d <= previous_test_end:
            raise ValueError(f"fold {i}: non-progressing test end")
        audited.append({"fold":i,"train":[a,b],"embargo":[b,c],
                        "test":[c,d],"train_rows":b-a,"test_rows":d-c})
        previous_test_end = d
    return {"fold_count":len(audited), "folds":audited,
            "nonoverlapping_tests":require_nonoverlapping_tests}


def audit_oos_reports(reports, *, n_rows):
    """Check report shape and finite results; never compound fold returns."""
    reports = list(reports)
    if not reports:
        raise ValueError("missing OOS reports")
    previous_end = -1
    checked = []
    for i, report in enumerate(reports):
        train, test = report["train"], report["test"]
        if len(train) != 2 or len(test) != 2:
            raise ValueError("invalid report bounds")
        a,b = train
        c,d = test
        if not all(type(x) is int for x in (a,b,c,d)) or not (0 <= a < b <= c < d <= n_rows):
            raise ValueError("train/test leakage or out-of-range bounds")
        if c < previous_end:
            raise ValueError("overlapping test reports")
        for key in ("net_return","max_drawdown"):
            val = report[key]
            if type(val) not in (float,int) or not isfinite(val):
                raise ValueError("nonfinite OOS metric")
        trades = report["trade_count"]
        if type(trades) is not int or trades < 0:
            raise ValueError("invalid trade count")
        checked.append({"fold":i,"test_rows":d-c})
        previous_end = d
    return {"fold_count":len(checked),"audited":checked,
            "compounded_return":None,
            "warning":"Fold-level returns are not a continuous investable equity curve"}
