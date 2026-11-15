# GitHub Cloud Codex — deployment plan (approval-gated)

## Current status
- GitHub Actions safety CI exists on the bootstrap branch.
- Hourly research manifest workflow is read-only; GitHub scheduled workflows run from the default branch after merge.
- No Codex cloud execution has been enabled.
- No OpenAI API key or paid API usage has been authorized.

## Approval boundaries
1. **PR merge**: user must explicitly approve each merge after reviewing latest checks.
2. **Secrets**: user must separately approve adding a repository or organization secret; never paste keys into chat, issues, logs or source.
3. **Costs**: user must separately approve an API budget and billing method before any paid Codex/API workflow is enabled.
4. **Live trading and deployment**: always require separate explicit approval; neither is part of this setup.

## Planned cloud architecture
- Hourly read-only research queue inventories code and publishes a short-lived artifact.
- A separate Codex executor will be added only after authentication and budget approval.
- Executor runs with least privilege on a fresh isolated branch, no live trading credentials, bounded runtime and concurrency.
- CI validates changes and opens a Draft PR, never merges.
- Untrusted issues, repository content and upstream projects are treated as data, not instructions.

## User steps
1. Inspect and merge the bootstrap Draft PR only if its latest checks pass and the changes are acceptable.
2. Confirm whether to enable the read-only hourly GitHub Actions schedule.
3. Separately approve a Codex authentication approach and maximum spending before paid execution is configured.

## Verification
This file is configuration documentation only; it does not prove that Codex executed.
