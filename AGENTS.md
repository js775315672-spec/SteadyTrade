# Codex agent instructions

## Scope
Work only on an isolated feature branch. Do not modify main directly. Prefer small, reviewable changes with tests and a Draft Pull Request.

## Autonomous loop
1. Inspect repository and open issues; propose a scoped change.
2. Research upstream projects, verify licenses and provenance. Never copy incompatible code.
3. Implement one bounded improvement.
4. Run tests, lint, security checks, and record commands and outputs.
5. Open a Draft PR with evidence, limitations, and next steps. Never merge automatically.

## Hard approval gates
Never execute live trading orders, enable live trading, access or expose secrets, deploy, merge PRs, or change branch protection without explicit user approval. Never place credentials, private datasets, or account data in this public repository.
Do not claim tests or backtests passed unless actually executed. On missing runtime/data, report BLOCKED.

## SteadyTrade
Paper trading only by default. Require Backtest -> Paper -> Risk verification -> User approval before any live capability.
For backtests use chronological in/out-of-sample splits, walk-forward checks, fees, slippage, lookahead checks, and report drawdown, daily returns, and compounded equity. Never optimize on the final holdout or promise a 1% daily return.
