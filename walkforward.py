"""Deterministic, leakage-resistant chronological walk-forward index splits.

Standard library only. Train and test indices are half-open. Purge/gap bars
between train and test are excluded. No strategy fitting or trading is performed.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Window:
    train_start: int
    train_end: int
    test_start: int
    test_end: int

def walk_forward_windows(length: int, train_size: int, test_size: int,
                         gap: int = 0, step: int | None = None):
    values = (length, train_size, test_size, gap)
    if any(type(v) is not int for v in values):
        raise TypeError("Window parameters must be integers")
    if length < 0 or train_size <= 0 or test_size <= 0 or gap < 0:
        raise ValueError("Invalid window sizes")
    if step is None:
        step = test_size
    if type(step) is not int or step <= 0:
        raise ValueError("step must be a positive integer")
    windows = []
    train_start = 0
    while train_start + train_size + gap + test_size <= length:
        train_end = train_start + train_size
        test_start = train_end + gap
        windows.append(Window(train_start, train_end, test_start,
                              test_start + test_size))
        train_start += step
    return windows
