# Binance archive CSV adapter (research only)

- **Source data format:** Binance public historical archive, https://data.binance.vision/ (no source code copied).
- **External open-source dependency:** None. Python standard library only; no third-party license/NOTICE obligation introduced.
- **Version pin:** Not applicable to this locally authored adapter; external data format is not version-pinned. Archive timestamps may use milliseconds or microseconds: specify `timestamp_unit` explicitly.
- **Changes:** Offline 12-column kline CSV reader for a single-member ZIP; UTC timestamps, OHLCV and chronological validation, uncompressed-size guard.
- **Security:** No network, API keys, exchange orders, or arbitrary ZIP extraction. A size cap does not eliminate all decompression/memory denial-of-service risks.
- **Verification:** Local Python unittest: 6/6 passed before PR; CI must be checked separately. No five-year real-market dataset has been tested.
- **Data quality:** Archive completeness, duplicates across ZIP files, continuity and timezone alignment must be validated before backtesting. A candle's close price is not available at its open timestamp; strategies must use next-bar execution.
- **Rollback:** Revert this PR; no migration or external state changes.
- **Integration:** Standalone adapter only. The existing backtest engine remains on another unmerged draft PR, so no integrated backtest is claimed.
