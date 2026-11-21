"""Offline Binance archive -> deterministic chronological out-of-sample research.

No API calls, live orders, tuning, or model fitting. This evaluates fixed
parameters separately on each OOS test window with a fresh cash balance.
Fold returns must NOT be interpreted as a continuous compounded equity curve.
"""
from binance_klines import read_zip_csv
from walk_forward import expanding_folds
from research_strategy import evaluate


def evaluate_archive(path, *, strategy="ema", timestamp_unit="ms",
                     train_size=100, test_size=30, gap=0,
                     fee_rate=.001, slippage_rate=.0005,
                     initial_cash=10000., **strategy_parameters):
    candles = read_zip_csv(path, timestamp_unit=timestamp_unit)
    if len(candles) < train_size + gap + test_size:
        raise ValueError("insufficient candles for one complete fold")
    folds = expanding_folds(len(candles), train_size, test_size,
                            step=test_size, gap=gap)
    reports = []
    for fold in folds:
        # Precompute on historical prefix to preserve indicator warm-up.
        # Test-only equity is simulated from test_start; the first test open
        # may use the signal at test_start-1, which is historical.
        from research_strategy import strategy_signals
        from offline_backtest import backtest
        history = candles[:fold.test_end]
        signals = strategy_signals(history, strategy, **strategy_parameters)
        test_candles = history[fold.test_start:fold.test_end]
        # Start test flat: no inherited position. Signal from the previous
        # closed bar is permitted only at the first test open.
        test_signals = signals[fold.test_start:fold.test_end]
        # The base backtester fills signal[i-1] at bar i; first test bar
        # cannot fill, making the boundary conservative and unambiguous.
        result = backtest(test_candles, test_signals, initial_cash=initial_cash,
                          fee_rate=fee_rate, slippage_rate=slippage_rate)
        reports.append({"train": [fold.train_start, fold.train_end],
                        "test": [fold.test_start, fold.test_end],
                        "net_return": result["net_return"],
                        "max_drawdown": result["max_drawdown"],
                        "trade_count": result["trade_count"]})
    return {"mode":"offline_fixed_parameters_oos",
            "fold_count":len(reports), "folds":reports,
            "data_rows":len(candles),
            "aggregate_equity":None,
            "note":"Per-fold reset; do not compound fold results or tune on test."}
