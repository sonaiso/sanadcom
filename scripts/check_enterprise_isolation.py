#!/usr/bin/env python3
"""Licence boundary gate: community (AGPLv3) code must not import the intuitem-licensed enterprise code.

Everything under enterprise/ is under the intuitem Commercial Software License (LICENSE.md). If community
modules import it, the shipped product silently depends on code that needs a contract. This gate fails CI
on any `import enterprise...` / `from enterprise... import` outside enterprise/, except the registered
exceptions below, each with a reason and a removal condition.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

PATTERN = re.compile(r"^\s*(?:from\s+(enterprise\w*)[\s.]|import\s+(enterprise\w*)\b)", re.MULTILINE)
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", "dist", "build"}
# path -> reason; remove the entry when the import is gone
REGISTERED_EXCEPTIONS: dict[str, str] = {
    "backend/core/management/commands/dump_permissions.py":
        "guarded try/except import of enterprise_core.models.ClientSettings; to be replaced by a plugin hook",
}


def scan(root: Path) -> list[str]:
    hits: list[str] = []
    for path in root.rglob("*.py"):
        rel = path.relative_to(root).as_posix()
        if any(part in SKIP_DIRS for part in path.parts) or rel.startswith("enterprise/") or rel == "scripts/check_enterprise_isolation.py":
            continue
        if rel in REGISTERED_EXCEPTIONS:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for m in PATTERN.finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            hits.append(f"{rel}:{line}: imports {m.group(1) or m.group(2)} (intuitem-licensed) from community code")
    return hits


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path(__file__).resolve().parent.parent
    hits = scan(root)
    if hits:
        print("Licence boundary violations:")
        for h in hits:
            print("  -", h)
        return 1
    print(f"Licence boundary checks passed ({len(REGISTERED_EXCEPTIONS)} registered exception(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
