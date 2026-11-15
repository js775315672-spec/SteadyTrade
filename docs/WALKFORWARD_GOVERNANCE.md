# Walk-forward split governance

This PR adds a dependency-free chronological split utility only. It does not
implement strategy fitting, backtesting, live execution, or performance claims.

## Provenance and license
- External code incorporated: none.
- Third-party runtime dependencies: none (Python standard library).
- Third-party NOTICE / attribution obligations introduced: none.
- No external source URL or pinned commit is applicable because no external
  package or code was integrated.
- Existing repository license and dependencies remain unchanged.

## Leakage and validation boundaries
- Each train window ends before its test window begins.
- Optional gap purges observations between train and test.
- The caller MUST fit indicators/models only on training data, and must not
  use test results to choose the winning strategy or tune parameters.
- Overlapping test windows are possible with step < test_size and must not
  be treated as independent out-of-sample observations.
- Backtest execution must separately account for fees, slippage, and fill
  assumptions. These are NOT evaluated by this split-only module.

## Test and risk notes
- Unit/regression tests: tests/test_walkforward.py.
- Integration with historical Binance datasets: NOT RUN.
- License/dependency check: no added dependencies or copied third-party code;
  this is a manifest-level review, not an automated license scanner.
- Secret scan: repository safety workflow's basic private-key scan only;
  it is not comprehensive.
- Rollback: revert the PR commit(s); module is isolated and unused by runtime.
- No API credentials, paid services, trading, or deployment.
