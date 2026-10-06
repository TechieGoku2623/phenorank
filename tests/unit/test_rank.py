from __future__ import annotations

from pathlib import Path

from phenorank.rank import rank_text

SAMPLE = Path(__file__).resolve().parents[2] / "data" / "sample"


def _text(name: str) -> str:
    return (SAMPLE / name).read_text(encoding="utf-8")


def test_classic_ranks_glut1_top1() -> None:
    result = rank_text(_text("classic.txt"))
    assert result.disclaimer.startswith("Hypothesis generation, NOT a diagnosis")
    assert result.candidates[0].disease_id == "OMIM:606777"
    assert result.insufficient_to_discriminate is False
    assert result.candidates[0].driving_phenotypes
    assert result.candidates[0].additional_test


def test_negation_naive_wrong_polarity_aware_right() -> None:
    text = _text("negation.txt")
    naive = rank_text(text, polarity_aware=False)
    aware = rank_text(text, polarity_aware=True)
    assert naive.candidates[0].disease_id != "OMIM:176270"
    assert aware.candidates[0].disease_id == "OMIM:176270"
    seizure_diseases = {
        "OMIM:606777",
        "OMIM:105830",
        "SYN:mito-enceph",
        "OMIM:312750",
        "SYN:seizure-ataxia-trap",
    }
    assert naive.candidates[0].disease_id in seizure_diseases


def test_nonspecific_insufficient() -> None:
    result = rank_text(_text("nonspecific.txt"))
    assert result.insufficient_to_discriminate is True
    assert "Insufficient" in result.discrimination_note


def test_unmapped_reported() -> None:
    result = rank_text(_text("unmapped.txt"))
    assert result.unmapped
    assert all(not item.startswith("HP:") for item in result.unmapped)


def test_resnik_measure_and_expected_absent() -> None:
    result = rank_text(_text("classic.txt"), measure="resnik")
    assert result.measure == "resnik"
    top = result.candidates[0]
    assert any("HP:" in item for item in top.expected_but_absent) or top.expected_but_absent == []
    assert "NOT a diagnosis" in result.disclaimer


def test_emptyish_text_still_typed() -> None:
    result = rank_text("nothing mapped here")
    assert result.candidates
    assert result.disclaimer
