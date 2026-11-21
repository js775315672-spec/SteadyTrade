"""Deterministic chronological walk-forward split boundaries (stdlib only).

Returns half-open index intervals; no strategy fitting or order execution.
The gap removes observations between train and test to support embargo.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Fold:
    train_start: int
    train_end: int
    test_start: int
    test_end: int


def expanding_folds(n_rows: int, train_size: int, test_size: int,
                    step: int | None = None, gap: int = 0):
    """Build chronological folds without overlapping train and test slices.

    All intervals are [start, end); partial final test folds are excluded.
    Test windows may overlap if step < test_size; callers must account for
    this when aggregating out-of-sample performance.
    """
    for name, value in (("n_rows", n_rows), ("train_size", train_size),
                        ("test_size", test_size), ("gap", gap)):
        if type(value) is not int or value < (0 if name in ("n_rows", "gap") else 1):
            raise ValueError(f"Invalid {name}")
    if step is None:
        step = test_size
    if type(step) is not int or step < 1:
        raise ValueError("step must be a positive integer")
    folds = []
    train_end = train_size
    while train_end + gap + test_size <= n_rows:
        fold = Fold(0, train_end, train_end + gap,
                    train_end + gap + test_size)
        folds.append(fold)
        train_end += step
    return folds
