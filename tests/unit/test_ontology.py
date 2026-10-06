from __future__ import annotations

import pytest

from phenorank.ontology import load_ontology
from phenorank.similarity import phenomizer_set, resnik_pair, resnik_set, score_pair


def test_ic_root_is_zero_and_leaf_positive() -> None:
    onto = load_ontology()
    assert onto.information_content("HP:0000001") == 0.0
    assert onto.information_content("HP:0001250") > 0.0
    assert onto.has_term("HP:0001250")
    assert "Seizure" in onto.name_of("HP:0001250")


def test_mica_and_resnik() -> None:
    onto = load_ontology()
    assert onto.mica("HP:0001250", "HP:0001251") == "HP:0000707"
    pair = resnik_pair("HP:0001250", "HP:0001251", onto)
    assert pair == onto.information_content("HP:0000707")
    assert resnik_pair("HP:9999999", "HP:0001250", onto) == 0.0


def test_set_measures() -> None:
    onto = load_ontology()
    query = ["HP:0001250", "HP:0001251"]
    disease = ["HP:0001250", "HP:0001251", "HP:0000252"]
    asymmetric = resnik_set(query, disease, onto)
    symmetric = phenomizer_set(query, disease, onto)
    assert asymmetric > 0
    assert symmetric > 0
    assert score_pair(query, disease, "resnik", onto) == asymmetric
    assert score_pair(query, disease, "phenomizer", onto) == symmetric
    assert resnik_set([], disease, onto) == 0.0
    with pytest.raises(ValueError, match="unknown measure"):
        score_pair(query, disease, "jaccard", onto)
    assert score_pair(query, disease, "overlap", onto) == 2.0


def test_descendants_include_self() -> None:
    onto = load_ontology()
    assert "HP:0001250" in onto.descendants("HP:0000707")
    assert "HP:0000001" in onto.ancestors("HP:0001250")
