from __future__ import annotations

from pathlib import Path

from phenorank.extract import extract
from phenorank.ontology import load_ontology

SAMPLE = Path(__file__).resolve().parents[2] / "data" / "sample"


def test_never_emits_term_outside_subset() -> None:
    onto = load_ontology()
    result = extract("Toddler with sparkly toenail dystrophy and hypotonia.")
    assert result.unmapped
    assert all(mention.hpo_id in onto.terms for mention in result.mentions)
    assert "HP:9999999" not in {m.hpo_id for m in result.mentions}


def test_negation_and_ruled_out() -> None:
    aware = extract("No seizures. Ruled out ataxia. Hypotonia is present.")
    polarities = {m.hpo_id: m.polarity for m in aware.mentions}
    assert polarities["HP:0001250"] == "negated"
    assert polarities["HP:0001251"] == "negated"
    assert polarities["HP:0001290"] == "positive"
    naive = extract("No seizures. Ruled out ataxia.", polarity_aware=False)
    assert all(m.polarity == "positive" for m in naive.mentions)


def test_uncertainty() -> None:
    result = extract("Child with possible ataxia and seizures.")
    polarities = {m.hpo_id: m.polarity for m in result.mentions}
    assert polarities["HP:0001251"] == "uncertain"
    assert polarities["HP:0001250"] == "positive"


def test_lay_language_maps() -> None:
    text = (SAMPLE / "lay.txt").read_text(encoding="utf-8")
    result = extract(text)
    ids = {m.hpo_id for m in result.mentions}
    assert "HP:0001290" in ids
    assert "HP:0000252" in ids
    assert "HP:0000486" in ids


def test_unmapped_never_approximated() -> None:
    text = (SAMPLE / "unmapped.txt").read_text(encoding="utf-8")
    result = extract(text)
    assert any("sparkly toenail" in item.lower() for item in result.unmapped)
    assert all(m.hpo_id != "HP:0000951" for m in result.mentions)


def test_disclaimer_on_extraction() -> None:
    result = extract("seizures")
    assert "NOT a diagnosis" in result.disclaimer
    assert result.positive_ids == ["HP:0001250"]
    assert result.negated_ids == []
    assert result.uncertain_ids == []
