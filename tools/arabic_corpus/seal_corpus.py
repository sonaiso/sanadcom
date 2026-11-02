#!/usr/bin/env python3
"""Seal the official Arabic regulatory texts (slice S1 of docs/COMPETITIVE_REMEDIATION_PLAN_AR.md).

Input:  a directory of source documents as published by the authority (PDF or UTF-8 text), one per
        framework edition, e.g. corpora/nca/ecc-2-2024-ar.pdf.
Output: corpora/nca/manifest.json — for every source: its sha256, size, the sha256 of the extracted
        text, word count and Arabic-character count; plus one .txt per source with the extracted text.

Rules (constitutional: reality → trace):
- No normalization, no diacritic insertion, no spelling repair. The text is extracted and sealed as is.
- Extraction is deterministic (`pdftotext -layout`); the manifest records the tool and its version so
  the seal can be reproduced.
- `--check` recomputes everything and fails on any drift (DEPOSIT_DRIFTED_FROM_SOURCE), so CI can
  prove the corpus in the tree is the sealed one.
- The texts are © their authority; keep the corpus directory private until written permission to
  redistribute exists. Only the manifest (hashes) is safe to publish.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ARABIC = re.compile(r"[؀-ۿ]")
TOKEN = re.compile(r"\S+")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_text(source: Path) -> tuple[str, str]:
    """Return (text, extractor_id). PDF via pdftotext -layout; .txt read verbatim."""
    if source.suffix.lower() == ".pdf":
        tool = shutil.which("pdftotext")
        if tool is None:
            raise RuntimeError("pdftotext is required to seal PDF sources (poppler-utils)")
        version = subprocess.run([tool, "-v"], capture_output=True, text=True).stderr.strip().splitlines()[0]
        out = subprocess.run([tool, "-layout", "-enc", "UTF-8", str(source), "-"], capture_output=True, check=True)
        return out.stdout.decode("utf-8"), version
    return source.read_text(encoding="utf-8"), "utf-8-text"


def seal(corpus_dir: Path) -> dict:
    entries = []
    for source in sorted(p for p in corpus_dir.iterdir() if p.suffix.lower() in {".pdf", ".txt"} and not p.name.endswith(".extracted.txt")):
        raw = source.read_bytes()
        text, extractor = extract_text(source)
        entries.append({
            "source": source.name,
            "source_sha256": sha256_bytes(raw),
            "source_bytes": len(raw),
            "extractor": extractor,
            "text_file": source.stem + ".extracted.txt",
            "text_sha256": sha256_bytes(text.encode("utf-8")),
            "words": len(TOKEN.findall(text)),
            "arabic_chars": len(ARABIC.findall(text)),
        })
        (corpus_dir / (source.stem + ".extracted.txt")).write_text(text, encoding="utf-8")
    return {"schema": "sanadcom.arabic-corpus-manifest.v1", "sources": entries,
            "rights": "Texts are the property of the issuing authority; hashes only may be published."}


def check(corpus_dir: Path, manifest_path: Path) -> list[str]:
    stored = json.loads(manifest_path.read_text(encoding="utf-8"))
    fresh = seal(corpus_dir)
    problems = []
    by_name = {e["source"]: e for e in fresh["sources"]}
    for e in stored["sources"]:
        f = by_name.get(e["source"])
        if f is None:
            problems.append(f"{e['source']}: missing from corpus directory")
            continue
        for key in ("source_sha256", "text_sha256", "words", "arabic_chars"):
            if e[key] != f[key]:
                problems.append(f"{e['source']}: {key} drifted ({e[key]} -> {f[key]})  [DEPOSIT_DRIFTED_FROM_SOURCE]")
    for name in by_name:
        if name not in {e["source"] for e in stored["sources"]}:
            problems.append(f"{name}: present in corpus directory but not in manifest")
    return problems


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("corpus_dir", type=Path)
    ap.add_argument("--manifest", type=Path, default=None, help="default: <corpus_dir>/manifest.json")
    ap.add_argument("--check", action="store_true", help="verify the stored manifest instead of writing it")
    args = ap.parse_args(argv[1:])
    manifest = args.manifest or (args.corpus_dir / "manifest.json")
    if args.check:
        problems = check(args.corpus_dir, manifest)
        for p in problems:
            print("  -", p)
        print("corpus check:", "FAILED" if problems else "passed")
        return 1 if problems else 0
    data = seal(args.corpus_dir)
    manifest.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for e in data["sources"]:
        print(f"{e['source']}: {e['words']} words, {e['arabic_chars']} Arabic chars, text sha256 {e['text_sha256'][:12]}…")
    print(f"manifest written: {manifest}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
