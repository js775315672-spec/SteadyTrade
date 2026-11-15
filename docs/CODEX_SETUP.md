# Local Codex runner (manual approval required)

This is a **safe, interactive bootstrap**, not an unattended agent.

## Windows prerequisites
- Git, GitHub CLI (`gh`), and OpenAI Codex CLI (`codex`) installed separately
- Authenticate Codex and GitHub yourself; never commit tokens
- Clone the repository, and use PowerShell in its root

## Preview (no changes)
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-codex.ps1
```

## Interactive execution (creates a new isolated branch)
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-codex.ps1 -Execute -Branch autopilot/first-task
```

The script checks the clean working tree, fetches main, creates an isolated branch, and starts Codex interactively. It does not automatically commit, push, create PRs, deploy, merge, or trade. Inspect and approve changes before publishing.

**Status:** Not yet tested on your Windows computer. Hourly ChatGPT automation does not automatically execute this local script. A separate approved runner and credentials are required for unattended operation.
