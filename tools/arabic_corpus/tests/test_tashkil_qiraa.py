"""Slices S3 (signed vocalization) and S4 (governed reading): expectations fixed by hand, mutations named.

The sample text is written by the agent for the tests; it is not authority text and never a reference.
Integration tests run only when ALGHANEM_SRC, NABT_SRC and MASHRU_SRC point at checkouts; their expected
values were obtained by calling those projects directly in the authoring session, not through these tools.
"""

import hashlib
import importlib.util
import json
import os
import pathlib
import re

import pytest

HERE = pathlib.Path(__file__).resolve().parent


def _load(name):
    spec = importlib.util.spec_from_file_location(name, HERE.parent / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


seal = _load("seal_corpus")
tashkil = _load("tashkil")
qiraa = _load("qiraa")

# agent-written sample (unvocalized "source"); a blank line between L2 and L3 shows that ids follow line numbers
SOURCE = (
    "يجب على الجهة تحديد سياسة الأمن السيبراني.\n"
    "إن السياسة تراجع سنويا.\n"
    "\n"
    "ما زال الخطر قائما.\n"
    "هل وثقت السياسة؟\n"
    "تحدد الجهة أدوار الأمن السيبراني.\n"
)
# the same rows vocalized by the agent on the bridge convention (ٱَ + lam sukun for the article, sukun on long و/ي)
VOCALIZED = {
    "s.txt:L1": "يَجِبُ عَلَى ٱَلْجِهَةِ تَحْدِيْدُ سِيَاسَةِ ٱَلْأَمْنِ ٱَلْسِّيْبْرَانِيِّ.",
    "s.txt:L2": "إِنَّ ٱَلْسِّيَاسَةَ تُرَاجَعُ سَنَوِيًّا.",
    "s.txt:L4": "مَا زَالَ ٱَلْخَطَرُ قَائِمًا.",
    "s.txt:L5": "هَلْ وُثِّقَتِ ٱَلْسِّيَاسَةُ؟",
}
VOCALIZERS = HERE.parent / "vocalizers.json"


@pytest.fixture
def corpus(tmp_path):
    (tmp_path / "s.txt").write_text(SOURCE, encoding="utf-8")
    data = seal.seal(tmp_path)
    (tmp_path / "manifest.json").write_text(
        json.dumps(data, ensure_ascii=False), encoding="utf-8"
    )
    return tmp_path


def _fill(table: pathlib.Path, vocalized=VOCALIZED, vocalizer="agent-sample"):
    lines = table.read_text(encoding="utf-8").split("\n")
    out = [lines[0]]
    for line in lines[1:]:
        if not line:
            continue
        seg, digest, unvoc, _, _ = line.split("\t")
        voc = vocalized.get(seg, "")
        out.append("\t".join([seg, digest, unvoc, voc, vocalizer if voc else ""]))
    table.write_text("\n".join(out) + "\n", encoding="utf-8")


def _sign(table: pathlib.Path, scope="TASHKIL_AGENT_SAMPLE_UNSIGNED", **extra):
    sig = {
        "signed_by": "agent-sample",
        "signed_on": "2026-11-03",
        "file": table.name,
        "sha256": hashlib.sha256(table.read_bytes()).hexdigest(),
        "scope": scope,
        **extra,
    }
    path = table.with_name("owner-" + table.stem + ".json")
    path.write_text(json.dumps(sig, ensure_ascii=False, indent=1), encoding="utf-8")
    return path


@pytest.fixture
def filled(corpus):
    table = corpus / "tashkil-s.tsv"
    tashkil.write_skeleton(corpus, "s.txt", table)
    _fill(table)
    sig = _sign(table)
    return corpus, table, sig


def test_skeleton_rows_and_ids_by_hand(corpus):
    table = corpus / "t.tsv"
    assert tashkil.write_skeleton(corpus, "s.txt", table) == 5  # six lines, one blank
    _, rows, errors = tashkil.read_table(table)
    assert errors == []
    assert [r["segment_id"] for r in rows] == [
        "s.txt:L1",
        "s.txt:L2",
        "s.txt:L4",
        "s.txt:L5",
        "s.txt:L6",
    ]
    assert rows[2]["unvocalized"] == "ما زال الخطر قائما."
    assert (
        rows[2]["segment_sha256"]
        == hashlib.sha256("ما زال الخطر قائما.".encode()).hexdigest()
    )


def test_letters_only_by_hand():
    assert tashkil.letters_only("ٱَلْجِهَةِ") == "الجهة"
    assert tashkil.letters_only("سَنَوِيًّا") == "سنويا"
    assert (
        tashkil.letters_only("قَائِمًا") == "قائما"
    )  # the hamza seat is a letter and stays


def test_agent_sample_is_accepted_with_counts(filled):
    corpus, table, sig = filled
    report = tashkil.check_table(corpus, table, sig, VOCALIZERS)
    assert report["accepted"] is True and report["errors"] == []
    assert report["counts"] == {"segments": 5, "filled": 4, "unfilled": 1, "errors": 0}
    assert report["scope"] == "TASHKIL_AGENT_SAMPLE_UNSIGNED"


def test_mutant_signature_drift_is_refused(filled):
    corpus, table, sig = filled
    table.write_text(
        table.read_text(encoding="utf-8") + "\n", encoding="utf-8"
    )  # one byte changes the seal
    report = tashkil.check_table(corpus, table, sig, VOCALIZERS)
    assert report["errors_by_code"] == {"TASHKIL_SIGNATURE_DRIFTED": 1}


def test_missing_signature_is_refused(filled):
    corpus, table, _ = filled
    report = tashkil.check_table(corpus, table, None, VOCALIZERS)
    assert "TASHKIL_SIGNATURE_MISSING" in report["errors_by_code"]


def test_mutant_vocalizer_changed_a_letter(corpus):
    table = corpus / "t.tsv"
    tashkil.write_skeleton(corpus, "s.txt", table)
    bad = dict(
        VOCALIZED, **{"s.txt:L1": VOCALIZED["s.txt:L1"].replace("ٱَلْجِهَةِ", "ٱَلْجِهَهِ")}
    )  # ة -> ه
    _fill(table, bad)
    sig = _sign(table)
    report = tashkil.check_table(corpus, table, sig, VOCALIZERS)
    assert report["errors_by_code"] == {"TASHKIL_CHANGES_LETTERS": 1}
    assert report["errors"][0]["detail"] == "s.txt:L1"


def test_unknown_vocalizer_and_agent_in_signed_scope(corpus):
    table = corpus / "t.tsv"
    tashkil.write_skeleton(corpus, "s.txt", table)
    _fill(table, vocalizer="nobody")
    sig = _sign(table)
    assert tashkil.check_table(corpus, table, sig, VOCALIZERS)["errors_by_code"] == {
        "TASHKIL_VOCALIZER_UNKNOWN": 4
    }
    _fill(table)  # agent rows
    sig = _sign(table, scope="TASHKIL_SIGNED", owner_words="موافق")
    assert tashkil.check_table(corpus, table, sig, VOCALIZERS)["errors_by_code"] == {
        "TASHKIL_AGENT_ROW_IN_SIGNED_SCOPE": 4
    }
    sig = _sign(table, scope="TASHKIL_SIGNED")  # signed scope without the owner's words
    assert (
        "TASHKIL_SIGNATURE_INCOMPLETE"
        in tashkil.check_table(corpus, table, sig, VOCALIZERS)["errors_by_code"]
    )


def test_mutant_segment_sha_tampered(filled):
    corpus, table, _ = filled
    text = table.read_text(encoding="utf-8").replace(
        "s.txt:L4\t", "s.txt:L3\t"
    )  # L3 is the blank line
    table.write_text(text, encoding="utf-8")
    sig = _sign(table)
    report = tashkil.check_table(corpus, table, sig, VOCALIZERS)
    assert report["errors_by_code"] == {"TASHKIL_SEGMENT_NOT_IN_SEALED_SOURCE": 1}


# ---- S4 aggregation with fakes (no Alghanem, NABT or Mashru needed) ------------------------------


def fake_bridge(word):
    return ("DEFER", "FAKE_ARTICLE", "") if "ٱ" in word else ("READY", "", word)


def fake_cert(canonical):
    return ("GENERATED_BY_LAW", "", "7")


FAKE_TABLE = [("إنّ", 2, False), ("ما زال", 1, False), ("هل", 12, False)]


def _rows():
    return [{"segment_id": k, "vocalized": v} for k, v in VOCALIZED.items()] + [
        {"segment_id": "s.txt:L6", "vocalized": ""}
    ]


def test_reading_counts_by_hand():
    report = qiraa.read_table(_rows(), fake_bridge, fake_cert, FAKE_TABLE, "deadbeef")
    # tokens per row: 7, 4, 4, 3 = 18; article words (ٱ) are 3+1+1+1 = 6 deferred by the fake bridge
    assert report["totals"] == {"words": 18, "READY": 12, "DEFER": 6, "governors": 3}
    assert report["bridge_reasons"] == {"FAKE_ARTICLE": 6}
    assert report["certificates"] == {"GENERATED_BY_LAW": 12}
    assert len(report["rows"]) == 4 and all(
        r["punctuation_stripped"] == 1 for r in report["rows"]
    )
    gov = {
        r["segment_id"]: [
            (g["governor"], g["class"], g["span"]) for g in r["governors"]
        ]
        for r in report["rows"]
    }
    assert gov == {
        "s.txt:L1": [],
        "s.txt:L2": [("إنّ", 2, [0])],
        "s.txt:L4": [("ما زال", 1, [0, 1])],
        "s.txt:L5": [("هل", 12, [0])],
    }
    assert report["governor_classes"] == {
        "1 كان وأخواتها": 1,
        "12 أدوات الاستفهام": 1,
        "2 إنّ وأخواتها": 1,
    }
    assert (
        report["rows"][0]["authority"] == "LOOKUP_NOT_PARSE"
        and "document_reading" not in report["rows"][0]
    )


def test_mutant_governor_class_comes_from_the_table_not_from_code():
    # planted mutation GOVERNOR_CLASS_HARDCODED: with "ما زال" moved to class 2 in the table the report must follow
    table = [("ما زال", 2, True)]
    report = qiraa.read_table(_rows(), fake_bridge, fake_cert, table, "x")
    g = report["rows"][2]["governors"][0]
    assert (g["class"], g["class_name"], g["implied"]) == (2, "إنّ وأخواتها", True)


def test_governor_marks_decide_between_homographs_by_hand():
    table = [
        ("إنّ", 2, False),
        ("إنْ", 10, False),
        ("ما", 10, False),
        ("ما", 12, False),
        ("ظنَّ", 3, False),
    ]
    rows = [{"segment_id": "x", "vocalized": "إِنَّ مَا ظَنَّ"}]
    report = qiraa.read_table(rows, fake_bridge, fake_cert, table, "x")
    found = [
        (g["token"], g["governor"], g["class"]) for g in report["rows"][0]["governors"]
    ]
    # إِنَّ carries the shadda of إنّ, not the sukun of إنْ; مَا matches both unmarked entries (kept); ظَنَّ matches ظنَّ
    assert found == [
        ("إِنَّ", "إنّ", 2),
        ("مَا", "ما", 10),
        ("مَا", "ما", 12),
        ("ظَنَّ", "ظنَّ", 3),
    ]
    assert (
        qiraa.marks_compatible("إنْ", "إِنَّ") is False
        and qiraa.marks_compatible("ما زال", "مَا زَالَ") is True
    )


def test_document_reader_hook_is_reported():
    report = qiraa.read_table(
        _rows()[:1],
        fake_bridge,
        fake_cert,
        FAKE_TABLE,
        "x",
        doc=lambda row: ("DEFER", ["UNSUPPORTED_CLAUSE"]),
    )
    assert report["rows"][0]["document_reading"] == {
        "status": "DEFER",
        "residual_codes": ["UNSUPPORTED_CLAUSE"],
    }


# ---- integration with the real projects ---------------------------------------------------------

ALGHANEM = os.environ.get("ALGHANEM_SRC")
NABT = os.environ.get("NABT_SRC")
MASHRU = os.environ.get("MASHRU_SRC")
have_all = all(p and pathlib.Path(p).exists() for p in (ALGHANEM, NABT, MASHRU))


@pytest.mark.skipif(
    not (MASHRU and pathlib.Path(MASHRU).exists()), reason="MASHRU_SRC not set"
)
def test_governor_class_names_match_mashru():
    text = pathlib.Path(MASHRU, "Jisr", "Awamil.lean").read_text(encoding="utf-8")
    found = {
        int(n): name
        for n, name in re.findall(
            r'\|\s*(\d+)\s*=>\s*"([^"]+)"',
            text.split("def sinfIsm")[1].split("def ")[0],
        )
    }
    assert found == qiraa.GOVERNOR_CLASSES


@pytest.mark.skipif(not have_all, reason="ALGHANEM_SRC / NABT_SRC / MASHRU_SRC not set")
def test_real_pipeline_on_the_agent_sample():
    bridge = qiraa.alghanem_bridge(pathlib.Path(ALGHANEM))
    cert = qiraa.nabt_certifier(pathlib.Path(NABT))
    doc = qiraa.nabt_document_reader(pathlib.Path(NABT))
    table, digest = qiraa.mashru_table(pathlib.Path(MASHRU))
    assert len(table) == 100 and digest.startswith(
        "37bb5242432ec077"
    )  # counted and hashed on the file directly
    # values below were obtained by calling gate.bridge / nabt directly in the authoring session
    assert bridge("تَحْدِيدُ") == (
        "DEFER",
        "HARAKA_IS_ABSENT_AND_IS_NEVER_GUESSED",
        "",
    )  # long ي needs its sukun
    assert bridge("ٱَلْجِهَةِ") == ("READY", "", "ءَلْجِهَتِ")
    report = qiraa.read_table(_rows(), bridge, cert, table, digest, doc)
    words = {w["token"]: w for r in report["rows"] for w in r["words"]}
    assert words["يَجِبُ"]["certificate"] == "GENERATED_BY_LAW" and words["يَجِبُ"][
        "numeric_code"
    ].startswith("1468914")
    assert words["إِنَّ"]["canonical"] == "ءِنْنَ" and words["قَائِمًا"]["canonical"] == "قَاْءِمَنْ"
    gov = {(g["governor"], g["class"]) for r in report["rows"] for g in r["governors"]}
    assert {("إنّ", 2), ("ما زال", 1), ("هل", 12), ("على", 7)} <= gov
    refused = {
        w["token"]: w.get("residual")
        for r in report["rows"]
        for w in r["words"]
        if w["certificate_reason"]
    }
    assert refused == {
        t: "ARTICLE_LAM_BEFORE_SOLAR_NOT_ASSIMILATED"
        for t in ("ٱَلْسِّيْبْرَانِيِّ", "ٱَلْسِّيَاسَةَ", "ٱَلْسِّيَاسَةُ")
    }
    # governors by hand: على(7) إنّ(2) ما(10) ما(12) «ما زال»(1) هل(12) = 6. A first hand count said 5: it
    # forgot that the unmarked homograph ما stays two candidates (10 and 12), which the tool keeps on purpose.
    assert report["totals"] == {"words": 18, "READY": 18, "governors": 6}
    assert report["rows"][3]["document_reading"]["status"] == "DEFER"
    assert (
        "CASE_ROLE_MISMATCH" in report["rows"][3]["document_reading"]["residual_codes"]
    )
