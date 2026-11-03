"""S5 first step: a quotation claim per segment through the real knowledge kernel; expectations fixed by hand
from the kernel's laws read in backend/knowledge_constitution/transitions.py, rank.py and action.py:
- no trace (segment not fully read)  -> BLOCKED at TRACE_CANDIDATE, handoff HUMAN_REVIEW, no claim licensed
- trace with provenance_ok (signed)  -> SUPPORTED at rank SUPPORTED; action threshold VERIFIED not met
                                        -> failed stage ACTION_LICENSE, handoff DEFERRAL_QUEUE
- trace without provenance (agent)   -> SUPPORTED but rank and ceiling CANDIDATE
"""

import hashlib
import importlib.util
import json
import os
import pathlib

import pytest

HERE = pathlib.Path(__file__).resolve().parent


def _load(name):
    spec = importlib.util.spec_from_file_location(name, HERE.parent / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


claims = _load("claims")
seal = _load("seal_corpus")
tashkil = _load("tashkil")
qiraa = _load("qiraa")

from tests.test_tashkil_qiraa import SOURCE, _fill, _sign

TABLE_SHA = "a" * 64


def _word(tok, ok=True):
    return {
        "token": tok,
        "bridge": "READY",
        "certificate": "GENERATED_BY_LAW" if ok else "",
        "certificate_reason": "" if ok else "UNLICENSED_SHAPE",
    }


def _reading(rows_words, table_sha=TABLE_SHA):
    return {
        "tashkil": {"table_sha256": table_sha},
        "governor_table_sha256": "g" * 64,
        "rows": [
            {"segment_id": sid, "words": words, "governors": []}
            for sid, words in rows_words.items()
        ],
    }


ROWS = [
    {
        "segment_id": "s.txt:L1",
        "segment_sha256": "1" * 64,
        "unvocalized": "ما زال الخطر قائما.",
        "vocalized": "مَا زَالَ ٱَلْخَطَرُ قَائِمًا.",
        "vocalizer": "h",
    },
    {
        "segment_id": "s.txt:L2",
        "segment_sha256": "2" * 64,
        "unvocalized": "هل وثقت السياسة؟",
        "vocalized": "هَلْ وُثِّقَتِ ٱَلْسِّيَاسَةُ؟",
        "vocalizer": "h",
    },
    {
        "segment_id": "s.txt:L3",
        "segment_sha256": "3" * 64,
        "unvocalized": "غير مملوء",
        "vocalized": "",
        "vocalizer": "",
    },
]
READING = _reading(
    {
        "s.txt:L1": [_word("مَا"), _word("زَالَ"), _word("ٱَلْخَطَرُ"), _word("قَائِمًا")],
        "s.txt:L2": [_word("هَلْ"), _word("وُثِّقَتِ"), _word("ٱَلْسِّيَاسَةُ", ok=False)],
    }
)
SIGNED = {
    "scope": "TASHKIL_SIGNED",
    "signed_by": "reviewer-1",
    "signed_on": "2026-11-03",
}
AGENT = {
    "scope": "TASHKIL_AGENT_SAMPLE_UNSIGNED",
    "signed_by": "agent-sample",
    "signed_on": "2026-11-03",
}


def test_signed_fully_read_segment_is_supported_but_never_licensed():
    report = claims.build(ROWS, READING, SIGNED, TABLE_SHA, {"s.txt": "t" * 64})
    assert report["counts"] == {
        "segments": 2,
        "by_judgment_status": {"SUPPORTED": 1, "BLOCKED": 1},
        "by_failed_stage": {"ACTION_LICENSE": 1, "TRACE_CANDIDATE": 1},
        "by_handoff_route": {"DEFERRAL_QUEUE": 1, "HUMAN_REVIEW": 1},
    }
    s1 = report["segments"][0]
    env = s1["envelope"]
    assert (
        env["judgment_status"],
        env["rank"],
        env["rank_ceiling"],
        env["failed_stage"],
    ) == ("SUPPORTED", "SUPPORTED", "SUPPORTED", "ACTION_LICENSE")
    assert (
        env["action_license"]["granted"] is False
        and env["handoff"]["route"] == "DEFERRAL_QUEUE"
    )
    assert env["applicability_result"] == "NOT_EVALUATED" and env[
        "normative_source_ids"
    ] == ["nca:s.txt"]
    assert set(claims.REQUIRED_ENVELOPE_KEYS) <= set(env)
    assert (
        s1["objects"]["claim_candidate"]["predicate"]
        == "the source states: ما زال الخطر قائما."
    )  # verbatim, unvocalized
    assert (
        s1["objects"]["trace_candidates"][0]["owner"] == "reviewer-1"
        and s1["objects"]["trace_candidates"][0]["provenance_ok"] is True
    )


def test_unread_segment_has_no_trace_and_is_blocked_for_human_review():
    report = claims.build(ROWS, READING, SIGNED, TABLE_SHA, {"s.txt": "t" * 64})
    s2 = report["segments"][1]
    assert (
        s2["objects"]["trace_candidates"] == []
        and s2["objects"]["evidence_bindings"] == []
    )
    env = s2["envelope"]
    assert (env["judgment_status"], env["failed_stage"], env["handoff"]["route"]) == (
        "BLOCKED",
        "TRACE_CANDIDATE",
        "HUMAN_REVIEW",
    )
    assert any(r["code"] == "missing_trace_candidates" for r in env["residuals"])
    assert s2["reading"] == {
        "words": 3,
        "certified": 2,
        "not_certified": ["ٱَلْسِّيَاسَةُ"],
        "governors": [],
        "fully_read": False,
    }


def test_agent_sample_caps_rank_at_candidate():
    report = claims.build(ROWS, READING, AGENT, TABLE_SHA, {"s.txt": "t" * 64})
    env = report["segments"][0]["envelope"]
    assert (env["judgment_status"], env["rank"], env["rank_ceiling"]) == (
        "SUPPORTED",
        "CANDIDATE",
        "CANDIDATE",
    )
    assert env["action_license"]["granted"] is False


def test_mutant_reading_of_another_table_is_refused():
    with pytest.raises(SystemExit, match="CLAIMS_READING_NOT_FOR_THIS_TABLE"):
        claims.build(ROWS, _reading({}, table_sha="b" * 64), SIGNED, TABLE_SHA, {})


def test_mutant_segment_without_reading_row_is_unread():
    # planted mutation: the S4 report lacks the row entirely -> no trace, blocked (never "fully read" by default)
    report = claims.build(ROWS[:1], _reading({}), SIGNED, TABLE_SHA, {})
    assert report["segments"][0]["reading"] is None
    assert report["segments"][0]["envelope"]["failed_stage"] == "TRACE_CANDIDATE"


def test_fully_read_requires_bridge_ready_and_certificate():
    assert claims.fully_read({"words": [_word("x")]}) is True
    assert claims.fully_read({"words": [_word("x", ok=False)]}) is False
    assert claims.fully_read({"words": [dict(_word("x"), bridge="DEFER")]}) is False
    assert claims.fully_read({"words": []}) is False


ALGHANEM = os.environ.get("ALGHANEM_SRC")
NABT = os.environ.get("NABT_SRC")
MASHRU = os.environ.get("MASHRU_SRC")
have_all = all(p and pathlib.Path(p).exists() for p in (ALGHANEM, NABT, MASHRU))


@pytest.mark.skipif(not have_all, reason="ALGHANEM_SRC / NABT_SRC / MASHRU_SRC not set")
def test_real_chain_on_the_agent_sample(tmp_path):
    (tmp_path / "s.txt").write_text(SOURCE, encoding="utf-8")
    (tmp_path / "manifest.json").write_text(
        json.dumps(seal.seal(tmp_path), ensure_ascii=False), encoding="utf-8"
    )
    table = tmp_path / "tashkil-s.tsv"
    tashkil.write_skeleton(tmp_path, "s.txt", table)
    _fill(table)
    sig = _sign(table)
    rows, seal_info = qiraa.load_accepted_rows(
        tmp_path, table, sig, HERE.parent / "vocalizers.json"
    )
    gov, digest = qiraa.mashru_table(pathlib.Path(MASHRU))
    reading = qiraa.read_table(
        rows,
        qiraa.alghanem_bridge(pathlib.Path(ALGHANEM)),
        qiraa.nabt_certifier(pathlib.Path(NABT)),
        gov,
        digest,
        tashkil_seal=seal_info,
    )
    report = claims.build(
        rows,
        reading,
        json.loads(sig.read_text(encoding="utf-8")),
        hashlib.sha256(table.read_bytes()).hexdigest(),
        {"s.txt": "x"},
    )
    # by hand from the S4 run: the three article-before-solar words are not certified, so three segments
    # have no trace; «ما زال الخطر قائما» is fully read, and the agent scope caps it at CANDIDATE
    assert report["counts"]["by_judgment_status"] == {"BLOCKED": 3, "SUPPORTED": 1}
    assert report["counts"]["by_failed_stage"] == {
        "TRACE_CANDIDATE": 3,
        "ACTION_LICENSE": 1,
    }
    ok = next(
        s for s in report["segments"] if s["envelope"]["judgment_status"] == "SUPPORTED"
    )
    assert ok["segment_id"] == "s.txt:L4" and ok["envelope"]["rank"] == "CANDIDATE"
    assert [g["governor"] for g in ok["reading"]["governors"]] == ["ما", "ما", "ما زال"]
