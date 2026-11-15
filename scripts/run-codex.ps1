param(
  [switch]$Execute,
  [string]$Task = "Inspect this repository, propose one small tested improvement, and stop before merge.",
  [string]$Branch = "autopilot/local-codex"
)
$ErrorActionPreference = "Stop"
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw "Git is required." }
if (-not (Get-Command codex -ErrorAction SilentlyContinue)) { throw "Codex CLI is required; install and authenticate it separately." }
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { throw "GitHub CLI (gh) is required." }
if ((git status --porcelain)) { throw "Working tree must be clean." }
$default = (git branch --show-current).Trim()
if (-not $default) { throw "Checkout a branch first." }
git fetch origin main
if ($LASTEXITCODE -ne 0) { throw "Fetch failed." }
if (-not $Execute) {
  Write-Host "DRY RUN: would create a feature branch from origin/main and run Codex interactively."
  Write-Host "No changes made. To continue, pass -Execute."
  exit 0
}
if ($Branch -eq "main" -or $Branch -eq "master") { throw "Protected branch name." }
git switch -c $Branch origin/main
if ($LASTEXITCODE -ne 0) { throw "Cannot create branch; choose a fresh branch name." }
Write-Host "Running Codex in interactive mode. Review all tool permissions and changes."
codex "$Task Read AGENTS.md first. Never access secrets, enable live trades, deploy, merge, or push without approval. Run available tests and summarize results."
if ($LASTEXITCODE -ne 0) { throw "Codex returned an error." }
Write-Host "Review diff and tests. No automatic commit, push, PR or merge is performed."
git status --short
