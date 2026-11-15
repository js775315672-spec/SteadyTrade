# Harness / Ouroboros governance v1

- No secrets, private keys, paid API calls, or live trading.
- GitHub Actions jobs are read-only and use `contents: read`.
- No automated merge, push, deployment, or PR approval.
- Changes enter via Draft PR; explicit user approval is required **for each merge**.
- Workflow: interview -> seed -> TRD -> decompose -> run -> evaluate -> evolve.
- Blocking checks: boundaries, layers, secrets, security, structure, specification, dependencies, mutation.
- Advisory checks: complexity, performance, AI anti-patterns.
- Checkpoint every iteration; retain reproducible test evidence.
- This initial scanner is a minimal baseline, not a full 35-pattern implementation.
- Never interpret a green CI check as proof of strategy profitability or trading safety.

## Shared policy source
https://github.com/js775315672-spec/Harness-Ouroboros-MCP
