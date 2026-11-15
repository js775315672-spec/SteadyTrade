#!/usr/bin/env python3
"""Dependency-free, read-only repository policy checks."""
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
patterns = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    "github token": re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    "aws access key": re.compile(r"AKIA[0-9A-Z]{16}"),
}
skip = {".git", ".venv", "venv", "node_modules", "__pycache__"}
errors = []
for path in root.rglob("*"):
    if not path.is_file() or any(part in skip for part in path.relative_to(root).parts):
        continue
    if path.stat().st_size > 1024 * 1024:
        continue
    try:
        data = path.read_text(encoding="utf-8")
    except (UnicodeError, OSError):
        continue
    if path.name == "harness_check.py":
        continue  # avoid matching signatures in the scanner itself
    for label, regex in patterns.items():
        if regex.search(data):
            errors.append(f"{path.relative_to(root)}: possible {label}")
for error in errors:
    print("ERROR:", error)
print(f"Harness policy scan: {len(errors)} finding(s)")
sys.exit(bool(errors))
