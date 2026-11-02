#!/usr/bin/env python3
"""Repository hygiene gate: no database dumps, backups, session stores or oversized binaries may be committed.

Rationale (2026-11-02 review): three PostgreSQL dumps and an SQLite WAL backup were tracked in the public
repository; they contained user accounts, argon2 password hashes, auth tokens, live session keys and audit
logs. This gate fails CI if such files reappear. It inspects tracked files only (``git ls-files``).
"""
from __future__ import annotations

import fnmatch
import subprocess
import sys
from pathlib import Path

FORBIDDEN_PATTERNS: tuple[str, ...] = (
    "*.dump",
    "*.sql",
    "*.sqlite3",
    "*.sqlite3-wal",
    "*.sqlite3-shm",
    "*.db",
    "*.db-wal",
    "*.db-shm",
    "backup-*.json",
    "db-backup-*/*",
    "*.pem",
    "*.key",
    ".env",
    "*/.env",
)
# Explicitly reviewed exceptions: path -> reason. Keep this list short and justified.
ALLOWED_EXCEPTIONS: dict[str, str] = {}
MAX_FILE_BYTES = 15 * 1024 * 1024
# Oversized files that pre-date this gate; each entry is a debt to resolve, not a permanent allowance.
LEGACY_OVERSIZED: dict[str, str] = {
    "all_frameworks_export.csv": "22 MB generated export; move to a release asset or regenerate on demand",
}


def tracked_files(root: Path) -> list[str]:
    out = subprocess.run(["git", "-C", str(root), "ls-files", "-z"], check=True, capture_output=True).stdout
    return [p for p in out.decode("utf-8", errors="surrogateescape").split("\0") if p]


def violations(root: Path, files: list[str]) -> list[str]:
    found: list[str] = []
    for rel in files:
        if rel in ALLOWED_EXCEPTIONS:
            continue
        if any(fnmatch.fnmatch(rel, pat) for pat in FORBIDDEN_PATTERNS):
            found.append(f"{rel}: forbidden file type (database dump, backup, key or environment file)")
            continue
        path = root / rel
        if path.is_file() and rel not in LEGACY_OVERSIZED and path.stat().st_size > MAX_FILE_BYTES:
            found.append(f"{rel}: {path.stat().st_size} bytes exceeds {MAX_FILE_BYTES} byte limit")
    return found


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path(__file__).resolve().parent.parent
    found = violations(root, tracked_files(root))
    if found:
        print("Repository hygiene violations:")
        for item in found:
            print(f"  - {item}")
        return 1
    print("Repository hygiene checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
