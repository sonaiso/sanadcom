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


seal = _load("seal_corpus")
base = _load("nabt_baseline")

# نصّ قصير كتبه الوكيل للاختبار؛ ليس نصًّا من وثائق الهيئة
SAMPLE_UNVOC = "يجب تحديد وتوثيق متطلبات الأمن السيبراني 3 مرات سنويا\n"
SAMPLE_VOC = "كَتَبَ مُحَمَّدٌ\n"


@pytest.fixture
def corpus(tmp_path):
    (tmp_path / "a.txt").write_text(SAMPLE_UNVOC, encoding="utf-8")
    (tmp_path / "b.txt").write_text(SAMPLE_VOC, encoding="utf-8")
    data = seal.seal(tmp_path)
    (tmp_path / "manifest.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return tmp_path


def test_seal_counts_by_hand(corpus):
    m = json.loads((corpus / "manifest.json").read_text(encoding="utf-8"))
    a = next(e for e in m["sources"] if e["source"] == "a.txt")
    assert a["words"] == 9  # counted by hand, digits included as tokens
    assert a["arabic_chars"] == 44  # 3+5+6+7+5+9+4+5, recounted by hand after a first miscount of 41
    assert a["text_sha256"] == seal.sha256_bytes(SAMPLE_UNVOC.encode("utf-8"))
    assert seal.check(corpus, corpus / "manifest.json") == []


def test_seal_detects_drift(corpus):
    # blocked example: a single changed character in a sealed text must fail --check
    (corpus / "a.txt").write_text(SAMPLE_UNVOC.replace("يجب", "ينبغي"), encoding="utf-8")
    problems = seal.check(corpus, corpus / "manifest.json")
    assert any("DEPOSIT_DRIFTED_FROM_SOURCE" in p for p in problems)


def test_baseline_aggregates_with_fake_reader(corpus):
    def fake(word):
        return ("READY", "") if any("ً" <= ch <= "ْ" for ch in word) else ("DEFER", "HARAKA_IS_ABSENT")

    report = base.baseline(base.load_texts(corpus), fake)
    assert report["sources"]["a.txt"]["tokens"] == 8  # Arabic runs only: the digit 3 is not a word
    assert report["sources"]["a.txt"]["READY"] == 0 and report["sources"]["a.txt"]["DEFER"] == 8
    assert report["sources"]["b.txt"] == {"tokens": 2, "unique": 2, "READY": 2, "DEFER": 0, "REJECT": 0, "by_reason": {}}
    assert report["totals"] == {"tokens": 10, "unique": 10, "READY": 2, "DEFER": 8, "REJECT": 0}


def test_baseline_counts_rejects_separately(corpus):
    report = base.baseline({"x": "كَُتَبَ"}, lambda w: ("REJECT", "CONFLICTING_MARKS"))
    assert report["sources"]["x"]["REJECT"] == 1 and report["sources"]["x"]["by_reason"] == {"CONFLICTING_MARKS": 1}


NABT_SRC = os.environ.get("NABT_SRC")


@pytest.mark.skipif(not NABT_SRC or not pathlib.Path(NABT_SRC, "nabt").exists(), reason="NABT_SRC not set")
def test_real_nabt_defers_unvocalized_and_reads_vocalized(corpus):
    read = base.nabt_reader(pathlib.Path(NABT_SRC))
    report = base.baseline(base.load_texts(corpus), read)
    a, b = report["sources"]["a.txt"], report["sources"]["b.txt"]
    assert a["READY"] == 0 and a["DEFER"] == 8 and set(a["by_reason"]) == {"MISSING_VOCALIZATION"}
    assert b["READY"] == 1  # كَتَبَ reads; مُحَمَّدٌ has shadda and tanwin, which NABT's strict reader defers
    assert b["DEFER"] == 1 and set(b["by_reason"]) == {"UNSUPPORTED_ORTHOGRAPHY"}
