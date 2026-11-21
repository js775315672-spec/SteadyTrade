# SteadyTrade P0 baseline audit (2026-11-22)

Status: **BLOCKED for live trading**. This is a read-only design and provenance audit; no runtime test or backtest was executed for this document.

## Source inventory
- main: README.md contains only the project title. AGENTS.md requires feature branches, Draft PRs, and human approval before merge or live trading.
- PR #1: governance and CI scaffolding (not evidence of autonomous operation).
- PR #2: offline fee/slippage trade-return research and tests.
- PR #3: read-only Harness policy scanner.
- PR #4: walkforward.py and tests.
- PR #5: binance_klines.py offline archive loader and tests.
- PR #6: walk_forward.py and tests (overlaps PR #4).

**Important:** PR descriptions and local test claims are not independent verification. The six PRs are not a single integrated engine. Verify each head SHA, merge state, and CI logs before selecting code for integration.

## P0 gate A: reproducible inventory
1. Record main SHA, each PR head SHA, draft/merge state, changed files, dependency list and workflow checks.
2. Execute existing unit tests on each PR head in isolated environments; capture command, exit code, SHA, and timestamp. Mark unexecuted tests NOT RUN.
3. Compare PR #4 and #6 for fold semantics, embargo/purge, overlap, incomplete folds and parameter validation. Select one implementation based on tested behavior, not PR number.
4. Scan repository and Git history for credentials, unsafe workflow permissions, dependencies and licenses. Never print secrets into logs.

## P0 gate B: offline research pipeline
Input: Binance local archive with explicit UTC candle-open/close timestamps, interval, symbol, unique ordering and data-gap checks.
Pipeline: validated candles -> lagged indicator signals -> next-bar execution -> fees/slippage -> realized trade ledger -> equity curve -> chronological train/validation/untouched holdout.
Invariants:
- No signal may use the current unfinished candle or future observations.
- Explicit fill assumptions; no same-bar lookahead.
- Charge both entry and exit costs; account for minimum notional and precision.
- Reject duplicate, unordered, invalid, or missing candles unless a documented gap policy handles them.
- Walk-forward folds must not leak labels/features across boundaries; exclude overlapping test periods from aggregate metrics or deduplicate explicitly.
- Never tune on the final holdout.
Report: trade count, net realized PnL, compounded equity, drawdown, win rate, profit factor, daily returns, costs, sample period and data quality. Never claim a daily 1% return.

## P0 gate C: paper-only execution safety
Default LIVE_TRADING=false, with no credential or exchange-order capability in the research runner.
Required deterministic tests: duplicate client order IDs, unknown API response, partial fill, crash/restart replay, stop-loss submission failure, stale market data, daily loss limit, consecutive-loss halt, emergency lock, and idempotent recovery.
Unknown response or partial fill must block new orders until reconciliation.
Do not unlock live trading from CI, an automation, or a model-generated recommendation.

## Proposed PR sequence
A. Baseline evidence + CI audit (this Draft PR).
B. Single canonical walk-forward splitter and cost model, with integration tests.
C. Offline data adapter and strategy/backtest integration; out-of-sample report.
D. Isolated paper execution state machine and failure-injection tests.
E. Read-only README dashboard generated from verified artifacts.

## Acceptance checklist
- [ ] main and PR SHA inventory independently verified
- [ ] CI run URLs and test logs collected for each PR
- [ ] duplicate walk-forward implementations reconciled
- [ ] deterministic cost-aware offline backtest passed
- [ ] OOS and leakage tests passed
- [ ] paper-only fault-injection suite passed
- [ ] dependency/license and secret scans passed
- [ ] README reports evidence, not unsupported percentages
- [ ] explicit human approval before any merge

No main modifications, merges, secrets, deployment or live trading are authorized by this audit.
