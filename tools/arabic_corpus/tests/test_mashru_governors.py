"""Mirror of Mashru's governor deposits: the oracle is what Mashru proves about them (mujam_98, mujam_45,
bila_hukm_2, naql_fi_jadwal, awamil_table in Jisr/AqsamAwamil.lean and SLGE/Wad.lean), read in the session."""

import importlib.util
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


mg = _load("mashru_governors")
MASHRU = os.environ.get("MASHRU_SRC")
have = bool(MASHRU) and pathlib.Path(MASHRU).exists()


def test_tajrid_by_hand():
    assert mg.tajrid("حتى (جر)") == "حتى"
    assert mg.tajrid("ما زال") == "مازال"
    assert mg.tajrid("إنّ") == "إن" and mg.tajrid("ظنَّ") == "ظن"


def test_case_codes_match_mashru_ramz_arbaa():
    assert [
        k
        for k, v in sorted(
            mg.CASE_NAME.items(),
            key=lambda kv: ["رفع", "نصب", "جرّ", "جزم"].index(kv[1]),
        )
    ] == [1, 0, 2, 3]


def test_explain_is_generated_from_data_only():
    card = {
        "governor": "إنّ",
        "class": 2,
        "class_name": "إنّ وأخواتها",
        "kinds": [
            {"kind": "harf", "source": "qatr-family", "family": "innaF", "line": 187}
        ],
        "equations": [
            [
                {
                    "role": 0,
                    "role_name": "الاسم/المفعول الأوّل",
                    "case": 0,
                    "case_name": "نصب",
                },
                {
                    "role": 1,
                    "role_name": "الخبر/المفعول الثاني",
                    "case": 1,
                    "case_name": "رفع",
                },
            ]
        ],
        "links": [],
    }
    assert (
        mg.explain(card)
        == "«إنّ»: حرف (قطر الندى (عائلة innaF، السطر 187))؛ من إنّ وأخواتها: تنصب الاسم/المفعول الأوّل وترفع الخبر/المفعول الثاني."
    )
    empty = dict(
        card, kinds=[], equations=[[]], class_name="أدوات الاستفهام", governor="هل"
    )
    assert (
        mg.explain(empty)
        == "«هل»: قسمُه بلا حكم في Mashru؛ من أدوات الاستفهام: لا فرضَ إعرابيٍّ لها في الجدول."
    )


@pytest.mark.skipif(not have, reason="MASHRU_SRC not set")
def test_counts_equal_what_mashru_proves():
    data = mg.cards(pathlib.Path(MASHRU))
    c = data["counts"]
    assert (c["governors"], c["with_kind"], c["from_families"], c["two_kinds"]) == (
        100,
        98,
        45,
        3,
    )  # mujam_98, mujam_45
    assert c["without_ruling"] == ["شرع", "بدأ"]  # bila_hukm_2
    kinds = [",".join(k["kind"] for k in card["kinds"]) for card in data["cards"]]
    assert (kinds.count("harf"), kinds.count("fil"), kinds.count("ism")) == (
        50,
        27,
        18,
    )  # mujam_98
    naql = mg.load_naql(pathlib.Path(MASHRU))
    assert (
        len(naql) == 56 and sum(1 for n in naql if n["inferred"]) == 12
    )  # naql_fi_jadwal
    assert [
        sum(1 for n in naql if n["book"] == b)
        for b in ("janadani", "mughni", "alfiyya", "sibawayhi")
    ] == [23, 21, 8, 4]
    fams = mg.load_families(pathlib.Path(MASHRU))
    assert [
        len(fams[f]) for f in ("jarrF", "nasbF", "jazm1F", "kanaF", "innaF", "zannaF")
    ] == [14, 4, 4, 11, 7, 8]  # awamil_table


@pytest.mark.skipif(not have, reason="MASHRU_SRC not set")
def test_cards_by_hand_from_the_lean_files():
    by = {
        (c["governor"], c["class"]): c for c in mg.cards(pathlib.Path(MASHRU))["cards"]
    }
    assert by[("إنّ", 2)]["kinds"] == [
        {"kind": "harf", "source": "qatr-family", "family": "innaF", "line": 187}
    ]
    assert by[("على", 7)]["kinds"][0]["line"] == 338 and by[("على", 7)][
        "equations"
    ] == [[{"role": 6, "role_name": "المجرور", "case": 2, "case_name": "جرّ"}]]
    assert by[("هل", 12)]["kinds"] == [
        {
            "kind": "harf",
            "source": "mughni",
            "line": 8095,
            "quote": "حرف موضوع لطلب التصديق الإيجابي",
            "inferred": False,
        }
    ]
    assert sorted(k["kind"] for k in by[("خلا", 7)]["kinds"]) == ["fil", "harf"]
    assert (
        by[("ما", 12)]["kinds"][0]["inferred"] is True
        and by[("ما", 10)]["kinds"][0]["source"] == "sibawayhi"
    )
    assert (
        by[("شرع", 6)]["kinds"] == []
        and by[("ما زال", 1)]["kinds"][0]["family"] == "kanaF"
    )
    assert by[("هل", 12)]["equations"] == [[]]


@pytest.mark.skipif(not have, reason="MASHRU_SRC not set")
def test_mutant_card_follows_a_tampered_table(tmp_path):
    # planted mutation CLASS_HARDCODED: copy Mashru, move «على» to class 2; the card must say class 2 and lose its family kind
    import shutil

    dst = tmp_path / "m"
    for sub in ("SLGE", "Jisr"):
        shutil.copytree(pathlib.Path(MASHRU) / sub, dst / sub)
    t = dst / "SLGE" / "AwamilTable.lean"
    t.write_text(
        t.read_text(encoding="utf-8").replace('("على", 7, false)', '("على", 2, false)'),
        encoding="utf-8",
    )
    by = {(c["governor"], c["class"]): c for c in mg.cards(dst)["cards"]}
    assert (
        ("على", 2) in by
        and by[("على", 2)]["kinds"] == []
        and by[("على", 2)]["class_name"] == "إنّ وأخواتها"
    )


@pytest.mark.skipif(not have, reason="MASHRU_SRC not set")
def test_mirror_matches_the_lean_generated_deposit():
    lean = {}
    for line in (
        (HERE.parent / "deposits" / "mashru-mujam2.tsv")
        .read_text(encoding="utf-8")
        .split("\n")
    ):
        if line.strip():
            g, s, k = line.split("\t")
            lean[(g, int(s))] = k
    mine = {
        (c["governor"], c["class"]): ",".join(k["kind"] for k in c["kinds"]) or "none"
        for c in mg.cards(pathlib.Path(MASHRU))["cards"]
    }
    assert len(lean) == 100 and lean == mine
