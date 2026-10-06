"""Ranking metrics: top-k, MRR, and the overlap-count baseline.

Overlap-count is a baseline, not a shipped similarity. The product ranker
uses Resnik or Phenomizer-style scores only.
"""

from __future__ import annotations

from phenorank.ontology import Ontology, load_ontology
from phenorank.similarity import score_pair


def overlap_count(query: list[str], disease: list[str], ontology: Ontology | None = None) -> float:
    """Shared-term count. Terms outside the committed subset are ignored."""

    onto = ontology if ontology is not None else load_ontology()
    known_q = {term for term in query if onto.has_term(term)}
    known_d = {term for term in disease if onto.has_term(term)}
    return float(len(known_q & known_d))


def rank_diseases(
    query: list[str],
    measure: str,
    ontology: Ontology | None = None,
) -> list[tuple[float, str]]:
    onto = ontology if ontology is not None else load_ontology()
    scored: list[tuple[float, str]] = []
    for disease in onto.diseases:
        if measure == "overlap":
            score = overlap_count(query, disease.hpo_ids, onto)
        else:
            score = score_pair(query, disease.hpo_ids, measure, onto)
        scored.append((score, disease.id))
    scored.sort(key=lambda row: (row[0], row[1]), reverse=True)
    return scored


def ranking_metrics(
    patients: list[dict[str, object]],
    measure: str,
    ontology: Ontology | None = None,
) -> dict[str, float]:
    """top-1 / top-5 / top-20 hit rate and MRR against gold disease ids."""

    onto = ontology if ontology is not None else load_ontology()
    n = len(patients)
    if n == 0:
        return {"top1": 0.0, "top5": 0.0, "top20": 0.0, "mrr": 0.0, "n": 0.0}
    hits = {1: 0, 5: 0, 20: 0}
    reciprocal = 0.0
    for patient in patients:
        raw_query = patient["hpo_ids"]
        if not isinstance(raw_query, list):
            raise TypeError("patient hpo_ids must be a list")
        query = [str(item) for item in raw_query]
        gold = str(patient["gold_disease"])
        order = [disease_id for _, disease_id in rank_diseases(query, measure, onto)]
        if gold not in order:
            continue
        rank = order.index(gold) + 1
        reciprocal += 1.0 / rank
        for k in hits:
            if rank <= k:
                hits[k] += 1
    return {
        "top1": hits[1] / n,
        "top5": hits[5] / n,
        "top20": hits[20] / n,
        "mrr": reciprocal / n,
        "n": float(n),
    }
