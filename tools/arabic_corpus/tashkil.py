#!/usr/bin/env python3
"""Signed vocalization deposit for a sealed Arabic corpus (slice S3 of docs/COMPETITIVE_REMEDIATION_PLAN_AR.md).

NABT never guesses a diacritic, and neither does this tool. A human vocalizer fills `vocalized` for each
segment of a sealed source text; the filled table is signed in the Alghanem `owner-*.json` manner
(signed_by, signed_on, file, sha256, scope, owner_words), and `check` refuses anything that breaks the
chain from the sealed reality to the vocalized row:

  TASHKIL_SIGNATURE_MISSING          no signature file for the table
  TASHKIL_SIGNATURE_DRIFTED          signature sha256 != sha256 of the table bytes
  TASHKIL_SIGNATURE_INCOMPLETE       signature lacks a required field, or a signed scope lacks owner words
  TASHKIL_SCOPE_UNKNOWN              scope is not TASHKIL_SIGNED / TASHKIL_AGENT_SAMPLE_UNSIGNED
  TASHKIL_SEGMENT_NOT_IN_SEALED_SOURCE  segment id / sha256 / text do not match the sealed text
  TASHKIL_CHANGES_LETTERS            vocalized row differs from the source in anything but marks and ٱ
  TASHKIL_DROPS_SOURCE_MARKS         a mark the sealed source already carried was removed
  TASHKIL_SEGMENT_HAS_TAB            a sealed line contains a tab and cannot be carried by the table
  SOURCE_SEAL_DRIFTED                the extracted text no longer hashes to the manifest
  TASHKIL_VOCALIZER_UNKNOWN          vocalizer is not in the registry
  TASHKIL_AGENT_ROW_IN_SIGNED_SCOPE  an agent-kind vocalizer inside a TASHKIL_SIGNED table
  TASHKIL_ROW_MALFORMED              wrong column count

Vocalization convention expected downstream (the Alghanem bridge, protocol A116-CANONICAL-TXT-1.1, reads
it losslessly): every consonant carries one of fatha/damma/kasra/sukun; long و/ي carry sukun; the long alif
after fatha carries nothing; the article at a word start is written ٱَ (wasla with its start vowel) and its
lam always carries sukun, also before a solar letter; shadda, tanwin, hamza seats and final ة are allowed.
A row that does not follow the convention is not an error here: the reader (qiraa.py) reports it by name.

Commands:
  tashkil.py new   CORPUS_DIR SOURCE --out TABLE.tsv        skeleton: one row per non-empty line
  tashkil.py check CORPUS_DIR TABLE.tsv --signature S.json [--vocalizers V.json] [--report R.json]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import unicodedata
from pathlib import Path

COLUMNS = ("segment_id", "segment_sha256", "unvocalized", "vocalized", "vocalizer")
SCOPES = ("TASHKIL_SIGNED", "TASHKIL_AGENT_SAMPLE_UNSIGNED")
SIGNATURE_FIELDS = ("signed_by", "signed_on", "file", "sha256", "scope")
DEFAULT_VOCALIZERS = Path(__file__).with_name("vocalizers.json")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def letters_only(text: str) -> str:
    """The row with every combining mark removed and ٱ folded to ا: what the vocalizer may not change."""
    out = []
    for ch in text:
        if unicodedata.category(ch).startswith("M"):
            continue
        out.append("ا" if ch == "ٱ" else ch)
    return "".join(out)


def marks_per_letter(text: str) -> list[frozenset[str]]:
    """The set of combining marks carried by each base character, in order (parallel to letters_only)."""
    out: list[set[str]] = []
    for ch in text:
        if unicodedata.category(ch).startswith("M"):
            if out:
                out[-1].add(ch)
            continue
        out.append(set())
    return [frozenset(m) for m in out]


def vocalization_problem(unvocalized: str, vocalized: str) -> str:
    """'' if the vocalizer only added marks (and ٱ) to the sealed segment; otherwise the error code.
    Both sides are projected to letters, so an officially part-vocalized source compares letter by
    letter, and a mark the source already carried may not be removed (TASHKIL_DROPS_SOURCE_MARKS)."""
    if letters_only(vocalized) != letters_only(unvocalized):
        return "TASHKIL_CHANGES_LETTERS"
    if any(
        not src <= new
        for src, new in zip(marks_per_letter(unvocalized), marks_per_letter(vocalized))
    ):
        return "TASHKIL_DROPS_SOURCE_MARKS"
    return ""


def load_source_text(corpus_dir: Path, source: str) -> str:
    """The sealed text, only if its bytes still hash to the manifest's text_sha256 (SOURCE_SEAL_DRIFTED)."""
    manifest = json.loads((corpus_dir / "manifest.json").read_text(encoding="utf-8"))
    for entry in manifest["sources"]:
        if entry["source"] == source:
            raw = (corpus_dir / entry["text_file"]).read_bytes()
            if sha256_bytes(raw) != entry.get("text_sha256"):
                raise SystemExit(f"SOURCE_SEAL_DRIFTED: {entry['text_file']}")
            return raw.decode("utf-8")
    raise SystemExit(f"SOURCE_NOT_IN_MANIFEST: {source}")


def segments(source: str, text: str) -> list[tuple[str, str, str]]:
    """(segment_id, sha256, line) for every non-empty line, ids by 1-based line number of the sealed text."""
    out = []
    for number, line in enumerate(text.split("\n"), start=1):
        if "\t" in line:
            raise SystemExit(f"TASHKIL_SEGMENT_HAS_TAB: {source}:L{number}")
        if line.strip():
            out.append(
                (f"{source}:L{number}", sha256_bytes(line.encode("utf-8")), line)
            )
    return out


def write_skeleton(corpus_dir: Path, source: str, out: Path) -> int:
    rows = segments(source, load_source_text(corpus_dir, source))
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("\t".join(COLUMNS) + "\n")
        for seg_id, digest, line in rows:
            fh.write(f"{seg_id}\t{digest}\t{line}\t\t\n")
    return len(rows)


def read_table(path: Path) -> tuple[bytes, list[dict[str, str]], list[dict]]:
    raw = path.read_bytes()
    lines = raw.decode("utf-8").split("\n")
    errors: list[dict] = []
    if not lines or lines[0].split("\t") != list(COLUMNS):
        errors.append({"code": "TASHKIL_ROW_MALFORMED", "row": 0, "detail": "header"})
        return raw, [], errors
    rows = []
    for number, line in enumerate(lines[1:], start=2):
        if line == "":
            continue
        parts = line.split("\t")
        if len(parts) != len(COLUMNS):
            errors.append(
                {
                    "code": "TASHKIL_ROW_MALFORMED",
                    "row": number,
                    "detail": f"{len(parts)} columns",
                }
            )
            continue
        rows.append(dict(zip(COLUMNS, parts)))
    return raw, rows, errors


def check_signature(
    signature: Path | None, table_bytes: bytes, table_name: str
) -> tuple[dict, list[dict]]:
    errors: list[dict] = []
    if signature is None or not signature.exists():
        errors.append({"code": "TASHKIL_SIGNATURE_MISSING", "detail": str(signature)})
        return {}, errors
    sig = json.loads(signature.read_text(encoding="utf-8"))
    if not isinstance(sig, dict):
        errors.append(
            {"code": "TASHKIL_SIGNATURE_INCOMPLETE", "detail": "not an object"}
        )
        return {}, errors

    def filled(
        key: str,
    ) -> bool:  # a null, a number or a blank string is not a field value
        value = sig.get(key)
        return isinstance(value, str) and bool(value.strip())

    missing = [f for f in SIGNATURE_FIELDS if not filled(f)]
    if missing:
        errors.append(
            {"code": "TASHKIL_SIGNATURE_INCOMPLETE", "detail": ",".join(missing)}
        )
    if sig.get("scope") not in SCOPES:
        errors.append(
            {"code": "TASHKIL_SCOPE_UNKNOWN", "detail": str(sig.get("scope"))}
        )
    elif sig["scope"] == "TASHKIL_SIGNED" and not filled("owner_words"):
        errors.append({"code": "TASHKIL_SIGNATURE_INCOMPLETE", "detail": "owner_words"})
    if filled("file") and Path(sig["file"]).name != table_name:
        errors.append(
            {
                "code": "TASHKIL_SIGNATURE_INCOMPLETE",
                "detail": f"file={sig['file']} != {table_name}",
            }
        )
    if sig.get("sha256") != sha256_bytes(table_bytes):
        errors.append(
            {"code": "TASHKIL_SIGNATURE_DRIFTED", "detail": sha256_bytes(table_bytes)}
        )
    return sig, errors


def check_table(
    corpus_dir: Path, table: Path, signature: Path | None, vocalizers: Path
) -> dict:
    registry = json.loads(vocalizers.read_text(encoding="utf-8"))["vocalizers"]
    kinds = {v["id"]: v["kind"] for v in registry}
    table_bytes, rows, errors = read_table(table)
    sig, sig_errors = check_signature(signature, table_bytes, table.name)
    errors.extend(sig_errors)
    scope = sig.get("scope")
    sealed_by_source: dict[str, dict[str, tuple[str, str]]] = {}
    filled = 0
    for number, row in enumerate(rows, start=2):
        source = row["segment_id"].split(":L")[0]
        if source not in sealed_by_source:
            try:
                sealed_by_source[source] = {
                    s: (d, line)
                    for s, d, line in segments(
                        source, load_source_text(corpus_dir, source)
                    )
                }
            except (SystemExit, OSError, KeyError) as exc:
                sealed_by_source[source] = {}
                errors.append(
                    {
                        "code": "TASHKIL_SEGMENT_NOT_IN_SEALED_SOURCE",
                        "row": number,
                        "detail": f"source {source}: {exc}",
                    }
                )
        sealed = sealed_by_source[source].get(row["segment_id"])
        if (
            sealed is None
            or sealed[0] != row["segment_sha256"]
            or sealed[1] != row["unvocalized"]
        ):
            errors.append(
                {
                    "code": "TASHKIL_SEGMENT_NOT_IN_SEALED_SOURCE",
                    "row": number,
                    "detail": row["segment_id"],
                }
            )
            continue
        if not row["vocalized"]:
            continue
        filled += 1
        problem = vocalization_problem(row["unvocalized"], row["vocalized"])
        if problem:
            errors.append({"code": problem, "row": number, "detail": row["segment_id"]})
        kind = kinds.get(row["vocalizer"])
        if kind is None:
            errors.append(
                {
                    "code": "TASHKIL_VOCALIZER_UNKNOWN",
                    "row": number,
                    "detail": row["vocalizer"],
                }
            )
        elif kind == "agent" and scope == "TASHKIL_SIGNED":
            errors.append(
                {
                    "code": "TASHKIL_AGENT_ROW_IN_SIGNED_SCOPE",
                    "row": number,
                    "detail": row["vocalizer"],
                }
            )
    by_code: dict[str, int] = {}
    for e in errors:
        by_code[e["code"]] = by_code.get(e["code"], 0) + 1
    return {
        "schema": "sanadcom.tashkil-check.v1",
        "table": table.name,
        "table_sha256": sha256_bytes(table_bytes),
        "scope": scope,
        "counts": {
            "segments": len(rows),
            "filled": filled,
            "unfilled": len(rows) - filled,
            "errors": len(errors),
        },
        "errors_by_code": dict(sorted(by_code.items())),
        "errors": errors,
        "accepted": not errors,
    }


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="command", required=True)
    new = sub.add_parser("new", help="write a skeleton table from a sealed source")
    new.add_argument("corpus_dir", type=Path)
    new.add_argument("source")
    new.add_argument("--out", type=Path, required=True)
    chk = sub.add_parser(
        "check",
        help="verify a filled table against the sealed source and its signature",
    )
    chk.add_argument("corpus_dir", type=Path)
    chk.add_argument("table", type=Path)
    chk.add_argument("--signature", type=Path, default=None)
    chk.add_argument("--vocalizers", type=Path, default=DEFAULT_VOCALIZERS)
    chk.add_argument("--report", type=Path, default=None)
    args = ap.parse_args(argv[1:])
    if args.command == "new":
        n = write_skeleton(args.corpus_dir, args.source, args.out)
        print(f"skeleton: {n} segments -> {args.out}")
        return 0
    report = check_table(args.corpus_dir, args.table, args.signature, args.vocalizers)
    if args.report:
        args.report.write_text(
            json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
    c = report["counts"]
    print(
        f"segments {c['segments']}  filled {c['filled']}  unfilled {c['unfilled']}  errors {c['errors']}  scope {report['scope']}"
    )
    for code, n in report["errors_by_code"].items():
        print(f"  {code}: {n}")
    return 0 if report["accepted"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
