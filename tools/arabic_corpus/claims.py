#!/usr/bin/env python3
"""S5, first step: from a governed reading to the knowledge kernel, one decision envelope per segment.

Chain (docs/00_KNOWLEDGE_CONSTITUTION.md, backend/knowledge_constitution):

  Reality   = the sealed segment of the authority's text (manifest text_sha256, segment sha256)
  Trace     = the certified reading of that segment (slice S4: every word READY in the bridge and
              GENERATED_BY_LAW in NABT's shape law); a segment that is not fully read HAS NO TRACE,
              so the kernel blocks it at TRACE_CANDIDATE: no claim is formed from an unread text
  Locus     = the source document
  Domain    = nca-text-v1: the only admissible relation is "states" (the source says this segment)
  Claim     = "the source states <segment>", predicate = the sealed text verbatim, never a paraphrase
  Relation  = locus states claim, citing the reading trace
  Binding   = provenance_ok iff the vocalization table is TASHKIL_SIGNED (an agent sample caps the
              rank at CANDIDATE), integrity_ok iff tashkil.check accepted the table now
  Rank, residuals, judgment, action licence "register_normative_statement" (threshold VERIFIED:
  never granted from this slice alone), handoff, feedback: all by the kernel, nothing here.

What this is not: no requirement is extracted, no obligation parsed, no applicability to any entity
(applicability_result = NOT_EVALUATED), no compliance judgment. The claim is a quotation claim.

Inputs: the sealed corpus, the vocalization table and its signature (re-checked now), and the S4 report
of exactly this table (its recorded table sha256 must match: CLAIMS_READING_NOT_FOR_THIS_TABLE).
Output (JSON): per segment the generated objects and the kernel's envelope (REQUIRED_ENVELOPE_KEYS);
totals by judgment status, failed stage and handoff route. `--check` fails on any difference.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
BACKEND = HERE.parent.parent / "backend"
for p in (str(HERE), str(BACKEND)):
    if p not in sys.path:
        sys.path.insert(0, p)

from knowledge_constitution import (
    ClaimCandidate,
    DefinedLocus,
    DomainContract,
    EvidenceBinding,
    KnowledgeRank,
    RealityCandidate,
    RelationCandidate,
    TraceCandidate,
    decision_envelope,
    evaluate_action_license,
    evaluate_knowledge_transition,
)
from knowledge_constitution.envelope import REQUIRED_ENVELOPE_KEYS

DOMAIN = DomainContract(
    domain_contract_id="nca-text-v1",
    governing_vocabulary="nca-ecc",
    admissible_relation_types=("states",),
    evidence_rules=(
        "sealed_source_required",
        "signed_vocalization_required",
        "all_words_certified_required",
    ),
    rank_policy="quotation_ceiling_supported",
)
ACTION_TYPE = "register_normative_statement"
ACTION_MIN_RANK = KnowledgeRank.VERIFIED


def fully_read(row: dict) -> bool:
    words = row.get("words", [])
    return bool(words) and all(
        w.get("bridge") == "READY" and w.get("certificate") == "GENERATED_BY_LAW"
        for w in words
    )


def segment_chain(
    source: str,
    seg: dict,
    reading: dict | None,
    signature: dict,
    table_sha256: str,
    text_sha256: str,
    governor_table_sha256: str,
) -> dict:
    segment_id, segment_sha = seg["segment_id"], seg["segment_sha256"]
    signed = signature.get("scope") == "TASHKIL_SIGNED"
    reality = RealityCandidate(
        reality_candidate_id=f"text:{source}",
        reality_type="NORMATIVE_TEXT",
        temporal_bounds=str(signature.get("signed_on", "")),
        observation_source=f"corpus:{text_sha256}",
        identity_conditions=("source_sha256", "text_sha256"),
    )
    read = reading is not None and fully_read(reading)
    traces: tuple[TraceCandidate, ...] = ()
    if read:
        traces = (
            TraceCandidate(
                trace_id=f"reading:{segment_id}",
                reality_candidate_id=reality.reality_candidate_id,
                source=f"sealed:{segment_sha}",
                scope=segment_id,
                owner=str(signature.get("signed_by", "")),
                freshness=str(signature.get("signed_on", "")),
                control_binding=segment_id,
                trace_type="certified_reading",
                provenance_ok=signed,
                integrity_ok=True,
                transformation_history=(
                    f"tashkil:{table_sha256}",
                    f"qiraa:governors:{governor_table_sha256}",
                ),
            ),
        )
    locus = DefinedLocus(
        defined_locus_id=f"locus:{source}",
        locus_type="DOCUMENT",
        reality_candidate_id=reality.reality_candidate_id,
        boundaries=source,
        applicable_time=reality.temporal_bounds,
    )
    claim = ClaimCandidate(
        claim_id=f"says:{segment_id}",
        defined_locus_id=locus.defined_locus_id,
        predicate=f"the source states: {seg['unvocalized']}",
        relation_type="states",
        temporal_scope=reality.temporal_bounds,
        domain_contract_id=DOMAIN.domain_contract_id,
        required_evidence_class="certified_reading",
    )
    relation = RelationCandidate(
        relation_id=f"rel:{segment_id}",
        source_object_id=locus.defined_locus_id,
        target_object_id=claim.claim_id,
        relation_type="states",
        domain_contract_id=DOMAIN.domain_contract_id,
        evidence_trace_ids=tuple(t.trace_id for t in traces),
    )
    bindings = tuple(
        EvidenceBinding(
            evidence_binding_id=f"binding:{t.trace_id}",
            claim_id=claim.claim_id,
            defined_locus_id=locus.defined_locus_id,
            domain_contract_id=DOMAIN.domain_contract_id,
            trace_ids=(t.trace_id,),
            provenance_ok=t.provenance_ok,
            integrity_ok=t.integrity_ok,
        )
        for t in traces
    )
    context = evaluate_knowledge_transition(
        knowledge_context_id=f"kc:{segment_id}",
        reality_candidate=reality,
        trace_candidates=traces,
        defined_locus=locus,
        domain_contract=DOMAIN,
        claim_candidate=claim,
        relation_candidates=(relation,),
        evidence_bindings=bindings,
        requested_rank=KnowledgeRank.SUPPORTED,
    )
    action = evaluate_action_license(
        context=context,
        action_license_id=f"al:{segment_id}",
        action_type=ACTION_TYPE,
        minimum_rank=ACTION_MIN_RANK,
    )
    envelope = decision_envelope(
        context,
        action,
        normative_source_ids=(f"nca:{source}",),
        applicability_result="NOT_EVALUATED",
    )
    assert all(k in envelope for k in REQUIRED_ENVELOPE_KEYS)
    reading_summary = None
    if reading is not None:
        words = reading.get("words", [])
        reading_summary = {
            "words": len(words),
            "certified": sum(
                1 for w in words if w.get("certificate") == "GENERATED_BY_LAW"
            ),
            "not_certified": [
                w["token"] for w in words if w.get("certificate") != "GENERATED_BY_LAW"
            ],
            "governors": [
                {"token": g["token"], "governor": g["governor"], "class": g["class"]}
                for g in reading.get("governors", [])
            ],
            "fully_read": read,
        }
    return {
        "segment_id": segment_id,
        "segment_sha256": segment_sha,
        "normative_source_id": f"nca:{source}",
        "reading": reading_summary,
        "objects": {
            "reality_candidate": reality.__dict__,
            "trace_candidates": [t.__dict__ for t in traces],
            "defined_locus": locus.__dict__,
            "domain_contract": DOMAIN.__dict__,
            "claim_candidate": claim.__dict__,
            "relation_candidate": relation.__dict__,
            "evidence_bindings": [b.__dict__ for b in bindings],
        },
        "envelope": envelope,
    }


def build(
    rows: list[dict],
    qiraa_report: dict,
    signature: dict,
    table_sha256: str,
    text_sha256_by_source: dict[str, str],
) -> dict:
    if qiraa_report.get("tashkil", {}).get("table_sha256") != table_sha256:
        raise SystemExit(
            "CLAIMS_READING_NOT_FOR_THIS_TABLE: the S4 report was made from another table"
        )
    readings = {r["segment_id"]: r for r in qiraa_report.get("rows", [])}
    segments = []
    by_status: Counter = Counter()
    by_stage: Counter = Counter()
    by_route: Counter = Counter()
    for row in rows:
        if not row.get("vocalized"):
            continue
        source = row["segment_id"].split(":L")[0]
        out = segment_chain(
            source,
            row,
            readings.get(row["segment_id"]),
            signature,
            table_sha256,
            text_sha256_by_source.get(source, ""),
            qiraa_report.get("governor_table_sha256", ""),
        )
        segments.append(out)
        env = out["envelope"]
        by_status[env["judgment_status"]] += 1
        by_stage[env["failed_stage"] or "NONE"] += 1
        by_route[(env["handoff"] or {}).get("route", "NONE")] += 1
    return {
        "schema": "sanadcom.claims.v1",
        "tashkil": {
            "table_sha256": table_sha256,
            "scope": signature.get("scope"),
            "signed_by": signature.get("signed_by"),
        },
        "domain_contract": DOMAIN.domain_contract_id,
        "action_type": ACTION_TYPE,
        "action_minimum_rank": ACTION_MIN_RANK.name,
        "applicability_result": "NOT_EVALUATED",
        "segments": segments,
        "counts": {
            "segments": len(segments),
            "by_judgment_status": dict(by_status),
            "by_failed_stage": dict(by_stage),
            "by_handoff_route": dict(by_route),
        },
        "what_this_is_not": [
            "no requirement extracted",
            "no obligation parsed",
            "no applicability evaluated",
            "no compliance judgment",
            "no training data",
        ],
    }


def main(argv: list[str]) -> int:
    import tashkil

    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("table", type=Path)
    ap.add_argument("--corpus-dir", type=Path, required=True)
    ap.add_argument("--signature", type=Path, required=True)
    ap.add_argument(
        "--reading",
        type=Path,
        required=True,
        help="the S4 report (qiraa.py --out) of this table",
    )
    ap.add_argument("--vocalizers", type=Path, default=tashkil.DEFAULT_VOCALIZERS)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--check", type=Path, default=None)
    args = ap.parse_args(argv[1:])
    check = tashkil.check_table(
        args.corpus_dir, args.table, args.signature, args.vocalizers
    )
    if not check["accepted"]:
        raise SystemExit(f"TASHKIL_NOT_ACCEPTED: {check['errors_by_code']}")
    _, rows, _ = tashkil.read_table(args.table)
    signature = json.loads(args.signature.read_text(encoding="utf-8"))
    manifest = json.loads(
        (args.corpus_dir / "manifest.json").read_text(encoding="utf-8")
    )
    text_sha = {e["source"]: e["text_sha256"] for e in manifest["sources"]}
    report = build(
        rows,
        json.loads(args.reading.read_text(encoding="utf-8")),
        signature,
        check["table_sha256"],
        text_sha,
    )
    if args.check:
        if json.loads(args.check.read_text(encoding="utf-8")) != json.loads(
            json.dumps(report)
        ):
            print("CLAIMS_DRIFTED: stored report differs from a fresh run")
            return 1
        print("claims check: passed")
        return 0
    if args.out:
        args.out.write_text(
            json.dumps(report, ensure_ascii=False, indent=1, default=str) + "\n",
            encoding="utf-8",
        )
    c = report["counts"]
    print(
        f"segments {c['segments']}  by status {c['by_judgment_status']}  by failed stage {c['by_failed_stage']}  by route {c['by_handoff_route']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
