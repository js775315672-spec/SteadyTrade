# SteadyTrade five-year offline research gate (draft)

This is an **execution plan**, not evidence of collected data or profitability.

1. Use only Binance official Spot monthly kline ZIPs and sibling .CHECKSUM files.
   First pilot: BTCUSDT and ETHUSDT, 1h interval, a small approved batch.
   Never commit raw archives, exchange credentials, or private data.
2. Run opt-in collection via archive_batch.collect_months in a network-enabled,
   user-authorized research environment. It has a maximum 12-month batch
   limit and defaults to three months per invocation. Retain local SHA256
   receipts; collection does not execute automatically.
3. Independently validate every archive checksum, UTC candle continuity,
   timestamp unit (2025+ Spot microseconds), gaps and month boundaries.
   Investigate missing months or listing changes before backtesting.
4. Establish a frozen dataset covering a stated start and end, excluding
   incomplete recent months and symbols without full listing histories.
5. Compare buy-and-hold, EMA, RSI, MACD and cost-aware variants with fixed
   fee/slippage assumptions; separately report gross and net returns,
   max drawdown, trades, exposure, and calendar coverage.
6. Run chronological train/validation/OOS partitions with embargo, no
   parameter tuning on test folds, no overlap or future data, and
   an independent holdout. Report uncertainty and regime sensitivity.
7. Avoid compounding returns from independently reset folds. A realistic
   continuous-equity simulation is required for a compounding claim.
8. Gate progression to paper trading on independent CI, verified dataset,
   realistic fill and fee simulation, risk controls and explicit approval.

**Known limitations:** Real archive retrieval, coverage, strategy evaluation,
independent out-of-sample verification and a final CI gate are still pending.
This draft does not enable real orders.
