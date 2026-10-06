"""Committed HPO subset and disease annotation profiles."""

from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path

from phenorank.config import get_settings


class Term:
    def __init__(self, term_id: str, name: str, parents: list[str]) -> None:
        self.id = term_id
        self.name = name
        self.parents = parents


class DiseaseProfile:
    def __init__(self, disease_id: str, name: str, hpo_ids: list[str]) -> None:
        self.id = disease_id
        self.name = name
        self.hpo_ids = list(hpo_ids)


class Ontology:
    def __init__(
        self,
        terms: dict[str, Term],
        diseases: list[DiseaseProfile],
        lexicon: dict[str, str],
        unmapped_phrases: list[str],
    ) -> None:
        self.terms = terms
        self.diseases = diseases
        self.lexicon = lexicon
        self.unmapped_phrases = unmapped_phrases
        self._children: dict[str, list[str]] = {tid: [] for tid in terms}
        for tid, term in terms.items():
            for parent in term.parents:
                self._children.setdefault(parent, []).append(tid)
        self._ancestors_cache: dict[str, frozenset[str]] = {}
        self._descendants_cache: dict[str, frozenset[str]] = {}
        self._ic = self._compute_ic()

    def has_term(self, term_id: str) -> bool:
        return term_id in self.terms

    def name_of(self, term_id: str) -> str:
        return self.terms[term_id].name if term_id in self.terms else term_id

    def ancestors(self, term_id: str) -> frozenset[str]:
        cached = self._ancestors_cache.get(term_id)
        if cached is not None:
            return cached
        if term_id not in self.terms:
            return frozenset({term_id})
        found: set[str] = {term_id}
        stack = [term_id]
        while stack:
            current = stack.pop()
            for parent in self.terms[current].parents:
                if parent not in found and parent in self.terms:
                    found.add(parent)
                    stack.append(parent)
        frozen = frozenset(found)
        self._ancestors_cache[term_id] = frozen
        return frozen

    def descendants(self, term_id: str) -> frozenset[str]:
        cached = self._descendants_cache.get(term_id)
        if cached is not None:
            return cached
        found: set[str] = {term_id}
        stack = [term_id]
        while stack:
            current = stack.pop()
            for child in self._children.get(current, []):
                if child not in found:
                    found.add(child)
                    stack.append(child)
        frozen = frozenset(found)
        self._descendants_cache[term_id] = frozen
        return frozen

    def common_ancestors(self, left: str, right: str) -> frozenset[str]:
        return self.ancestors(left) & self.ancestors(right)

    def information_content(self, term_id: str) -> float:
        return self._ic.get(term_id, 0.0)

    def mica(self, left: str, right: str) -> str:
        shared = self.common_ancestors(left, right)
        if not shared:
            return "HP:0000001"
        return max(shared, key=self.information_content)

    def _compute_ic(self) -> dict[str, float]:
        n_diseases = len(self.diseases)
        if n_diseases == 0:
            return {tid: 0.0 for tid in self.terms}
        annotated: dict[str, set[str]] = {tid: set() for tid in self.terms}
        for disease in self.diseases:
            closed: set[str] = set()
            for term_id in disease.hpo_ids:
                if term_id in self.terms:
                    closed.update(self.ancestors(term_id))
            for term_id in closed:
                annotated[term_id].add(disease.id)
        ic: dict[str, float] = {}
        for term_id in self.terms:
            freq = len(annotated[term_id]) / n_diseases
            ic[term_id] = 0.0 if freq <= 0.0 else -math.log(freq)
        return ic


def _load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_ontology(sample_dir: Path | None = None) -> Ontology:
    root = sample_dir if sample_dir is not None else get_settings().sample_dir
    raw_terms = _load_json(root / "hpo_subset.json")
    raw_diseases = _load_json(root / "diseases.json")
    raw_lexicon = _load_json(root / "lexicon.json")
    if not isinstance(raw_terms, dict) or not isinstance(raw_diseases, dict):
        raise ValueError("ontology JSON must be objects")
    if not isinstance(raw_lexicon, dict):
        raise ValueError("lexicon JSON must be an object")
    terms_blob = raw_terms.get("terms")
    diseases_blob = raw_diseases.get("diseases")
    entries = raw_lexicon.get("entries")
    unmapped = raw_lexicon.get("unmapped_phrases", [])
    if not isinstance(terms_blob, list) or not isinstance(diseases_blob, list):
        raise ValueError("terms and diseases must be lists")
    if not isinstance(entries, list) or not isinstance(unmapped, list):
        raise ValueError("lexicon entries/unmapped_phrases must be lists")
    terms = {
        str(item["id"]): Term(str(item["id"]), str(item["name"]), list(item["parents"]))
        for item in terms_blob
        if isinstance(item, dict)
    }
    diseases = [
        DiseaseProfile(str(item["id"]), str(item["name"]), list(item["hpo_ids"]))
        for item in diseases_blob
        if isinstance(item, dict)
    ]
    lexicon: dict[str, str] = {}
    for item in entries:
        if not isinstance(item, dict):
            continue
        hpo_id = str(item["hpo_id"])
        if hpo_id not in terms:
            raise ValueError(f"lexicon maps to unknown term {hpo_id}")
        phrases = item.get("phrases", [])
        if not isinstance(phrases, list):
            continue
        for phrase in phrases:
            lexicon[str(phrase).lower()] = hpo_id
    unmapped_phrases = [str(item).lower() for item in unmapped]
    return Ontology(terms, diseases, lexicon, unmapped_phrases)
