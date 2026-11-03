#!/usr/bin/env python3
"""Governed reading of a checked vocalization table (slice S4, first step): word certificates and governors.

For every filled row of a vocalization table (tashkil.py, slice S3), every whitespace token is sent through:

  1. the orthographic bridge  (Alghanem gate/bridge.py, protocol A116-CANONICAL-TXT-1.1): ordinary vocalized
     spelling -> canonical A116 text, or DEFER/REJECT by name (HARAKA_IS_ABSENT_AND_IS_NEVER_GUESSED, ...);
  2. NABT's strict word reader and shape law (nabt.alphabet.parse_word, nabt.certificates.issue_certificate):
     canonical text -> cells -> WORD_SHAPE certificate (GENERATED_BY_LAW) or UNLICENSED_SHAPE by name;
  3. a lookup in Mashru's sealed table of the hundred governors (SLGE/AwamilTable.lean, generated from the
     owner's xlsx): a token, or a token pair, whose letters equal a governor's letters is reported with the
     governor's class (1..13) and the class name. This is a LOOKUP, not a parse: no operand is identified,
     no sentence structure is claimed, and a clitic prefix (وَ، فَ، بِ...) hides a governor (named residual
     CLITIC_PREFIX_NOT_SPLIT is not detectable here and is listed as a known gap).
  4. optionally NABT's document reader (nabt.arabic_reader.read_arabic) on the whole row; its status and
     residual codes are reported as they come (the installed fragment does not cover regulatory prose yet).

Each word is read in isolation (entry start, exit continue): the bridge's boundary interface between words
(wasl of the article's alif after a previous word, pause at the end) is not modelled yet; residual
BOUNDARY_INTERFACE_NOT_MODELLED is recorded once per row.

The three sources are pluggable so the aggregation is testable without them:
  --alghanem-src DIR   directory containing gate/bridge.py
  --nabt-src DIR       NABT's src/ directory
  --mashru-src DIR     Mashru checkout containing SLGE/AwamilTable.lean (its sha256 is recorded)
The table is accepted by tashkil.check_table first (signature, seal, source binding) and the report
carries that table's sha256 and scope. Output (JSON): per row the words with their stage results, governors found, document-reader status; totals by
status and by reason name. `--check REPORT` recomputes and fails on any difference (QIRAA_DRIFTED).
No percentage is computed; the S4 acceptance threshold is measured later on the signed ECC table.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter
from collections.abc import Callable
from pathlib import Path

# Mashru Jisr/Awamil.lean, `sinfIsm` (owner's assignment); checked against the file by the tests when present.
GOVERNOR_CLASSES = {
    1: "كان وأخواتها",
    2: "إنّ وأخواتها",
    3: "ظنّ وأخواتها",
    4: "نواصب المضارع",
    5: "جوازم المضارع",
    6: "كاد وأخواتها",
    7: "حروف الجرّ",
    8: "حروف العطف",
    9: "لام التعليل",
    10: "أدوات الشرط الجازمة",
    11: "أدوات الشرط غير الجازمة",
    12: "أدوات الاستفهام",
    13: "أدوات النداء",
}
PUNCTUATION = ".،؛:؟!()«»\"'"
TABLE_ROW = re.compile(r'^\s*\("([^"]+)",\s*(\d+),\s*(true|false)\),?\s*$')

BridgeFn = Callable[
    [str], tuple[str, str, str]
]  # word -> (status, reason, canonical_text)
CertFn = Callable[
    [str], tuple[str, str, str]
]  # canonical -> (status, reason, numeric_code)
DocFn = Callable[[str], tuple[str, list[str]]]  # row -> (status, residual codes)


def letters_only(text: str) -> str:
    return "".join(
        "ا" if ch == "ٱ" else ch
        for ch in text
        if not unicodedata.category(ch).startswith("M")
    )


def alghanem_bridge(src: Path) -> BridgeFn:
    sys.path.insert(0, str(src))
    try:
        from gate.bridge import bridge  # type: ignore
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise SystemExit(f"ALGHANEM_NOT_AVAILABLE: {exc}") from exc

    def read(word: str) -> tuple[str, str, str]:
        record = bridge(word)
        status = str(record["status"])
        if status == "READY":
            return ("READY", "", record["canonical_text"])
        items = record.get("deferrals") or record.get("rejections") or []
        reason = (
            items[0]["reason"]
            if items
            else (record.get("error") or {}).get("reason", status)
        )
        return (status, str(reason), "")

    return read


def nabt_certifier(src: Path) -> CertFn:
    sys.path.insert(0, str(src))
    try:
        from nabt.alphabet import parse_word  # type: ignore
        from nabt.certificates import issue_certificate  # type: ignore
        from nabt.errors import NabtError  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise SystemExit(f"NABT_NOT_AVAILABLE: {exc}") from exc

    def certify(canonical: str) -> tuple[str, str, str]:
        try:
            cert = issue_certificate(parse_word(canonical), mode="wasl")
            return (str(cert["status"]), "", str(cert["numeric_code"]))
        except NabtError as err:
            return (
                str(getattr(err, "status", "REJECT")),
                str(getattr(err, "code", "?")),
                "",
            )

    return certify


def nabt_document_reader(src: Path) -> DocFn:
    sys.path.insert(0, str(src))
    try:
        from nabt.arabic_reader import read_arabic  # type: ignore
        from nabt.errors import NabtError  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise SystemExit(f"NABT_NOT_AVAILABLE: {exc}") from exc

    def read(row: str) -> tuple[str, list[str]]:
        try:
            d = read_arabic(row, source_id="tashkil").as_dict()
            return (
                str(d["status"]),
                sorted({r["code"] for r in d["document"].get("residuals", [])}),
            )
        except NabtError as err:
            return (
                str(getattr(err, "status", "REJECT")),
                [str(getattr(err, "code", "?"))],
            )

    return read


def mashru_table(src: Path) -> tuple[list[tuple[str, int, bool]], str]:
    path = src / "SLGE" / "AwamilTable.lean"
    raw = path.read_bytes()
    rows = []
    for line in raw.decode("utf-8").split("\n"):
        m = TABLE_ROW.match(line)
        if m:
            rows.append((m.group(1), int(m.group(2)), m.group(3) == "true"))
    if not rows:
        raise SystemExit(f"MASHRU_TABLE_EMPTY: {path}")
    return rows, hashlib.sha256(raw).hexdigest()


def clusters(text: str) -> list[tuple[str, frozenset[str]]]:
    """(base letter, its combining marks) per letter; ٱ folded to ا, spaces kept as bases."""
    out: list[tuple[str, set[str]]] = []
    for ch in text:
        if unicodedata.category(ch).startswith("M"):
            if out:
                out[-1][1].add(ch)
            continue
        out.append(("ا" if ch == "\u0671" else ch, set()))
    return [(b, frozenset(m)) for b, m in out]


def marks_compatible(entry: str, token: str) -> bool:
    """A table entry written with marks (إنّ vs إنْ, ظنَّ) matches only a token carrying those marks on
    the same letters; an entry without marks (ما) matches any vocalization: that ambiguity is kept."""
    e, t = clusters(entry), clusters(token)
    if len(e) != len(t):
        return False
    return all(eb == tb and em <= tm for (eb, em), (tb, tm) in zip(e, t))


def governor_index(
    table: list[tuple[str, int, bool]],
) -> dict[str, list[tuple[str, int, bool]]]:
    index: dict[str, list[tuple[str, int, bool]]] = {}
    for name, cls, implied in table:
        index.setdefault(letters_only(name), []).append((name, cls, implied))
    return index


SOLAR = set("تثدذرزسشصضطظلن")


def tokens_of(row: str) -> tuple[list[str], int, set[int]]:
    """Tokens without edge punctuation, how many had some, and the indices after which punctuation stood
    (a governor pair never crosses such a boundary)."""
    out, stripped, closed = [], 0, set()
    for tok in row.split():
        t = tok.strip(PUNCTUATION)
        if t != tok:
            stripped += 1
        if t:
            out.append(t)
            if tok.rstrip(PUNCTUATION) != tok:
                closed.add(len(out) - 1)
        elif out:
            closed.add(
                len(out) - 1
            )  # a free-standing punctuation token closes the previous word
    return out, stripped, closed


def article_before_solar_with_shadda(token: str) -> bool:
    """ٱَلْ + a solar letter carrying shadda: the case the bridge keeps unassimilated."""
    cl = clusters(token)
    if len(cl) < 3 or cl[0][0] != "ا" or cl[1][0] != "ل":
        return False
    base, marks = cl[2]
    return base in SOLAR and "\u0651" in marks


def read_row(
    row: str, bridge: BridgeFn, certify: CertFn, index: dict, doc: DocFn | None
) -> dict:
    tokens, stripped, closed = tokens_of(row)
    words = []
    for tok in tokens:
        status, reason, canonical = bridge(tok)
        entry = {
            "token": tok,
            "bridge": status,
            "bridge_reason": reason,
            "canonical": canonical,
            "certificate": "",
            "certificate_reason": "",
            "numeric_code": "",
        }
        if status == "READY":
            c_status, c_reason, code = certify(canonical)
            entry.update(
                certificate=c_status, certificate_reason=c_reason, numeric_code=code
            )
            if c_reason == "UNLICENSED_SHAPE" and article_before_solar_with_shadda(tok):
                # the bridge keeps the article's lam with its sukun before a solar letter (lossless, no
                # assimilation); NABT's shape law refuses the two sukuns in a row. Named, not guessed away.
                entry["residual"] = "ARTICLE_LAM_BEFORE_SOLAR_NOT_ASSIMILATED"
        words.append(entry)
    governors = []
    plain = [letters_only(t) for t in tokens]
    for i, p in enumerate(plain):
        for name, cls, implied in index.get(p, []):
            if marks_compatible(name, tokens[i]):
                governors.append(
                    {
                        "span": [i],
                        "token": tokens[i],
                        "governor": name,
                        "class": cls,
                        "class_name": GOVERNOR_CLASSES.get(cls, "?"),
                        "implied": implied,
                    }
                )
        if i + 1 < len(plain) and i not in closed:
            pair = tokens[i] + " " + tokens[i + 1]
            for name, cls, implied in index.get(p + " " + plain[i + 1], []):
                if marks_compatible(name, pair):
                    governors.append(
                        {
                            "span": [i, i + 1],
                            "token": pair,
                            "governor": name,
                            "class": cls,
                            "class_name": GOVERNOR_CLASSES.get(cls, "?"),
                            "implied": implied,
                        }
                    )
    result = {
        "words": words,
        "governors": governors,
        "punctuation_stripped": stripped,
        "residuals": ["BOUNDARY_INTERFACE_NOT_MODELLED"],
        "authority": "LOOKUP_NOT_PARSE",
    }
    if doc is not None:
        status, codes = doc(row)
        result["document_reading"] = {"status": status, "residual_codes": codes}
    return result


def read_table(
    rows: list[dict[str, str]],
    bridge: BridgeFn,
    certify: CertFn,
    table: list,
    table_sha256: str,
    doc: DocFn | None = None,
    tashkil_seal: dict | None = None,
) -> dict:
    index = governor_index(table)
    out_rows = []
    totals = Counter()
    bridge_reasons: Counter = Counter()
    cert_statuses: Counter = Counter()
    governor_classes: Counter = Counter()
    for r in rows:
        if not r.get("vocalized"):
            continue
        res = read_row(r["vocalized"], bridge, certify, index, doc)
        res["segment_id"] = r["segment_id"]
        out_rows.append(res)
        for w in res["words"]:
            totals["words"] += 1
            totals[w["bridge"]] += 1
            if w["bridge_reason"]:
                bridge_reasons[w["bridge_reason"]] += 1
            if w["certificate"]:
                cert_statuses[
                    w["certificate"]
                    if not w["certificate_reason"]
                    else w["certificate_reason"]
                ] += 1
        for g in res["governors"]:
            totals["governors"] += 1
            governor_classes[f"{g['class']} {g['class_name']}"] += 1
    return {
        "schema": "sanadcom.qiraa.v1",
        "tashkil": tashkil_seal or {},
        "governor_table_sha256": table_sha256,
        "governor_table_rows": len(table),
        "rows": out_rows,
        "totals": dict(totals),
        "bridge_reasons": dict(sorted(bridge_reasons.items(), key=lambda kv: -kv[1])),
        "certificates": dict(sorted(cert_statuses.items(), key=lambda kv: -kv[1])),
        "governor_classes": dict(sorted(governor_classes.items())),
        "known_gaps": [
            "BOUNDARY_INTERFACE_NOT_MODELLED",
            "CLITIC_PREFIX_NOT_SPLIT",
            "GOVERNOR_OPERANDS_NOT_IDENTIFIED",
            "GOVERNOR_HOMOGRAPHS_KEPT_AS_CANDIDATES",
            "ARTICLE_LAM_BEFORE_SOLAR_NOT_ASSIMILATED",
        ],
    }


def load_accepted_rows(
    corpus_dir: Path, table: Path, signature: Path, vocalizers: Path | None
) -> tuple[list[dict[str, str]], dict]:
    """Rows of a table only after tashkil.check_table accepted it now (TASHKIL_NOT_ACCEPTED otherwise)."""
    here = str(Path(__file__).resolve().parent)
    if here not in sys.path:
        sys.path.insert(0, here)
    import tashkil  # same directory

    report = tashkil.check_table(
        corpus_dir, table, signature, vocalizers or tashkil.DEFAULT_VOCALIZERS
    )
    if not report["accepted"]:
        raise SystemExit(f"TASHKIL_NOT_ACCEPTED: {report['errors_by_code']}")
    _, rows, _ = tashkil.read_table(table)
    return rows, {
        "table": report["table"],
        "table_sha256": report["table_sha256"],
        "scope": report["scope"],
    }


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument(
        "table",
        type=Path,
        help="a vocalization table; tashkil.py check is run on it first",
    )
    ap.add_argument("--corpus-dir", type=Path, required=True)
    ap.add_argument("--signature", type=Path, required=True)
    ap.add_argument("--vocalizers", type=Path, default=None)
    ap.add_argument("--alghanem-src", type=Path, required=True)
    ap.add_argument("--nabt-src", type=Path, required=True)
    ap.add_argument("--mashru-src", type=Path, required=True)
    ap.add_argument(
        "--document-reader",
        action="store_true",
        help="also run NABT's document reader per row",
    )
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--check", type=Path, default=None)
    args = ap.parse_args(argv[1:])
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    rows, seal = load_accepted_rows(
        args.corpus_dir, args.table, args.signature, args.vocalizers
    )
    table, digest = mashru_table(args.mashru_src)
    report = read_table(
        rows,
        alghanem_bridge(args.alghanem_src),
        nabt_certifier(args.nabt_src),
        table,
        digest,
        nabt_document_reader(args.nabt_src) if args.document_reader else None,
        seal,
    )
    if args.check:
        stored = json.loads(args.check.read_text(encoding="utf-8"))
        if stored != report:
            print("QIRAA_DRIFTED: stored report differs from a fresh run")
            return 1
        print("qiraa check: passed")
        return 0
    text = json.dumps(report, ensure_ascii=False, indent=1)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")
    t = report["totals"]
    print(
        f"words {t.get('words', 0)}  READY {t.get('READY', 0)}  DEFER {t.get('DEFER', 0)}  REJECT {t.get('REJECT', 0)}  governors {t.get('governors', 0)}"
    )
    for k, v in report["bridge_reasons"].items():
        print(f"  bridge {k}: {v}")
    for k, v in report["certificates"].items():
        print(f"  certificate {k}: {v}")
    for k, v in report["governor_classes"].items():
        print(f"  governor class {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
