"""Static guardrail checks for the bootstrap PowerShell runner."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run-codex.ps1"
POLICY = ROOT / "AGENTS.md"

class RunnerPolicyTests(unittest.TestCase):
    def test_runner_exists(self):
        self.assertTrue(SCRIPT.is_file())

    def test_explicit_execute_flag(self):
        s = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("[switch]$Execute", s)
        self.assertIn("if (-not $Execute)", s)

    def test_no_automatic_push_or_merge(self):
        s = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("git push ", s)
        self.assertNotIn("gh pr merge", s)
        self.assertNotIn("gh pr create", s)

    def test_isolated_branch_and_clean_tree(self):
        s = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("git status --porcelain", s)
        self.assertIn("git switch -c $Branch origin/main", s)

    def test_approval_policy(self):
        p = POLICY.read_text(encoding="utf-8").lower()
        self.assertIn("explicit user approval", p)
        self.assertIn("live trading", p)

if __name__ == "__main__":
    unittest.main()
