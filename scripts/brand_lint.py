#!/usr/bin/env python3
"""Fail if forbidden brand strings appear in the athru_service tree."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = re.compile(r"sanrad|infion|hitachi|megachip|scintcare", re.I)
SKIP_DIRS = {".git", "__pycache__", ".ruff_cache", "node_modules", ".venv"}
# Allow this script to mention forbidden terms in the pattern itself
ALLOW_FILES = {"brand_lint.py"}


def main() -> int:
	hits: list[str] = []
	for path in ROOT.rglob("*"):
		if not path.is_file():
			continue
		if any(part in SKIP_DIRS for part in path.parts):
			continue
		if path.name in ALLOW_FILES:
			continue
		if path.suffix.lower() not in {".py", ".js", ".json", ".md", ".txt", ".css", ".html", ".xml", ".csv"}:
			continue
		try:
			text = path.read_text(encoding="utf-8")
		except Exception:
			continue
		for i, line in enumerate(text.splitlines(), 1):
			if FORBIDDEN.search(line):
				hits.append(f"{path.relative_to(ROOT)}:{i}: {line.strip()[:120]}")
	if hits:
		print("Brand lint FAILED — forbidden strings found:")
		for h in hits:
			print(" ", h)
		return 1
	print("Brand lint OK — no forbidden OEM/customer brand strings.")
	return 0


if __name__ == "__main__":
	sys.exit(main())
