"""Resnik and Phenomizer-style set similarity on the committed toy ontology.

Resnik (Resnik 1995): IC of the most informative common ancestor.
Phenomizer-style (Köhler et al. 2009): symmetric mean of best Resnik matches.
No third measure is implemented.
"""

from __future__ import annotations

from phenorank.ontology import Ontology, load_ontology


def resnik_pair(left: str, right: str, ontology: Ontology | None = None) -> float:
    onto = ontology if ontology is not None else load_ontology()
    if not onto.has_term(left) or not onto.has_term(right):
        return 0.0
    return onto.information_content(onto.mica(left, right))


def resnik_set(
    query: list[str],
    disease: list[str],
    ontology: Ontology | None = None,
) -> float:
    """Asymmetric Resnik: mean over query terms of the best disease match."""

    onto = ontology if ontology is not None else load_ontology()
    known_query = [term for term in query if onto.has_term(term)]
    known_disease = [term for term in disease if onto.has_term(term)]
    if not known_query or not known_disease:
        return 0.0
    scores = [
        max(resnik_pair(q_term, d_term, onto) for d_term in known_disease) for q_term in known_query
    ]
    return sum(scores) / len(scores)


def phenomizer_set(
    query: list[str],
    disease: list[str],
    ontology: Ontology | None = None,
) -> float:
    """Symmetric Resnik used by Phenomizer (Köhler et al., AJHG 2009)."""

    onto = ontology if ontology is not None else load_ontology()
    forward = resnik_set(query, disease, onto)
    reverse = resnik_set(disease, query, onto)
    return 0.5 * (forward + reverse)


def score_pair(
    query: list[str],
    disease: list[str],
    measure: str,
    ontology: Ontology | None = None,
) -> float:
    if measure == "resnik":
        return resnik_set(query, disease, ontology)
    if measure == "phenomizer":
        return phenomizer_set(query, disease, ontology)
    if measure == "overlap":
        from phenorank.metrics import overlap_count

        return overlap_count(query, disease, ontology)
    raise ValueError(
        f"unknown measure {measure}; only resnik, phenomizer, and overlap are implemented"
    )
