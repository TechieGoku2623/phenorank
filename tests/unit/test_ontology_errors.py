from __future__ import annotations

import json
from pathlib import Path

import pytest

from phenorank.ontology import Ontology, Term, load_ontology


def test_load_ontology_rejects_bad_shape(tmp_path: Path) -> None:
    (tmp_path / "hpo_subset.json").write_text("[]\n", encoding="utf-8")
    (tmp_path / "diseases.json").write_text("{}\n", encoding="utf-8")
    (tmp_path / "lexicon.json").write_text("{}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="ontology JSON must be objects"):
        load_ontology(tmp_path)


def test_empty_ontology_ic() -> None:
    onto = Ontology({}, [], {}, [])
    assert onto.information_content("HP:0000001") == 0.0
    assert onto.mica("HP:0000001", "HP:0000001") == "HP:0000001"


def test_name_of_unknown() -> None:
    onto = Ontology({"HP:0000001": Term("HP:0000001", "All", [])}, [], {}, [])
    assert onto.name_of("missing") == "missing"
    assert onto.common_ancestors("HP:0000001", "HP:0000001") == frozenset({"HP:0000001"})


def test_lexicon_unknown_term(tmp_path: Path) -> None:
    (tmp_path / "hpo_subset.json").write_text(
        json.dumps({"terms": [{"id": "HP:0000001", "name": "All", "parents": []}]}) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "diseases.json").write_text(json.dumps({"diseases": []}) + "\n", encoding="utf-8")
    (tmp_path / "lexicon.json").write_text(
        json.dumps(
            {"entries": [{"hpo_id": "HP:9999999", "phrases": ["x"]}], "unmapped_phrases": []}
        )
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="unknown term"):
        load_ontology.cache_clear()
        load_ontology(tmp_path)
    load_ontology.cache_clear()
