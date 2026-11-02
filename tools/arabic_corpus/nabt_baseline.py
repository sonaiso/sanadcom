#!/usr/bin/env python3
"""Baseline of what NABT can read in a sealed Arabic corpus (slice S2 of the remediation plan).

For every sealed text, every whitespace token is sent to NABT's strict word reader. NABT never guesses
diacritics, so an unvocalized official text is expected to be mostly DEFER; this report is the work
queue for slice S3 (signed vocalization), not a score.

The reader is pluggable so the aggregation can be tested without NABT installed:
  --nabt-src PATH     use NABT's `src/` directory (nabt.alphabet.parse_word, the strict A116 reader)
  (default)           try `import nabt`; if unavailable, exit 2 with a named reason

Output (JSON): per source {tokens, unique, READY, DEFER, REJECT, by_reason{name: count}} and totals.
`--check REPORT` recomputes and fails if any number differs (BASELINE_DRIFTED).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Callable

TOKEN = re.compile(r"[؀-ۿ]+")  # Arabic runs only; digits, Latin and punctuation are not words for NABT

Verdict = tuple[str, str]  # (status, reason)


def nabt_reader(src: Path | None) -> Callable[[str], Verdict]:
    if src is not None:
        sys.path.insert(0, str(src))
    try:
        from nabt.alphabet import parse_word  # type: ignore
        from nabt.errors import NabtError  # type: ignore
    except Exception as exc:  # pragma: no cover - environment dependent
        raise SystemExit(f"NABT_NOT_AVAILABLE: {exc}")

    def read(word: str) -> Verdict:
        try:
            parse_word(word)
            return ("READY", "")
        except NabtError as err:
            status = getattr(err, "status", None) or "REJECT"
            code = getattr(err, "code", None) or getattr(err, "args", ["?"])[0]
            return (str(status), str(code))

    return read


def baseline(texts: dict[str, str], read: Callable[[str], Verdict]) -> dict:
    report = {"schema": "sanadcom.nabt-baseline.v1", "sources": {}, "totals": Counter()}
    cache: dict[str, Verdict] = {}
    for name, text in texts.items():
        tokens = TOKEN.findall(text)
        statuses = Counter()
        reasons = Counter()
        for tok in tokens:
            if tok not in cache:
                cache[tok] = read(tok)
            status, reason = cache[tok]
            statuses[status] += 1
            if status != "READY":
                reasons[reason] += 1
        entry = {"tokens": len(tokens), "unique": len(set(tokens)),
                 "READY": statuses.get("READY", 0), "DEFER": statuses.get("DEFER", 0),
                 "REJECT": sum(v for k, v in statuses.items() if k not in ("READY", "DEFER")),
                 "by_reason": dict(sorted(reasons.items(), key=lambda kv: -kv[1]))}
        report["sources"][name] = entry
        for k in ("tokens", "unique", "READY", "DEFER", "REJECT"):
            report["totals"][k] += entry[k]
    report["totals"] = dict(report["totals"])
    return report


def load_texts(corpus_dir: Path) -> dict[str, str]:
    manifest = json.loads((corpus_dir / "manifest.json").read_text(encoding="utf-8"))
    return {e["source"]: (corpus_dir / e["text_file"]).read_text(encoding="utf-8") for e in manifest["sources"]}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("corpus_dir", type=Path)
    ap.add_argument("--nabt-src", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=None, help="write the JSON report here")
    ap.add_argument("--check", type=Path, default=None, help="compare against a stored report and fail on drift")
    args = ap.parse_args(argv[1:])
    report = baseline(load_texts(args.corpus_dir), nabt_reader(args.nabt_src))
    if args.check:
        stored = json.loads(args.check.read_text(encoding="utf-8"))
        if stored != report:
            print("BASELINE_DRIFTED: stored report differs from a fresh run")
            return 1
        print("baseline check: passed")
        return 0
    text = json.dumps(report, ensure_ascii=False, indent=1)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")
    t = report["totals"]
    print(f"tokens {t['tokens']}  unique {t['unique']}  READY {t['READY']}  DEFER {t['DEFER']}  REJECT {t['REJECT']}")
    for name, e in report["sources"].items():
        top = ", ".join(f"{k}: {v}" for k, v in list(e["by_reason"].items())[:3])
        print(f"  {name}: READY {e['READY']}/{e['tokens']}  top refusals: {top}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
