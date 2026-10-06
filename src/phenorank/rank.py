"""Rank disease profiles from extracted phenotypes. Not a diagnosis."""

from __future__ import annotations

from phenorank import SAFETY_DISCLAIMER
from phenorank.extract import extract
from phenorank.ontology import DiseaseProfile, Ontology, load_ontology
from phenorank.schemas import MeasureName, RankedCandidate, RankResponse
from phenorank.similarity import score_pair

NONSPECIFIC = frozenset(
    {
        "HP:0001263",  # global developmental delay
        "HP:0001508",  # failure to thrive
        "HP:0001249",  # intellectual disability
        "HP:0004322",  # short stature
        "HP:0001270",  # motor delay
    }
)

SUGGESTED_TEST = {
    "HP:0001250": "EEG for seizures",
    "HP:0001251": "neurologic exam / MRI for ataxia",
    "HP:0003128": "serum lactate",
    "HP:0001638": "echocardiogram",
    "HP:0001642": "echocardiogram for pulmonic stenosis",
    "HP:0000957": "dermatologic exam / NF1 panel",
    "HP:0001010": "ophthalmology / pigmentation exam",
    "HP:0000639": "ophthalmology for nystagmus",
    "HP:0001332": "neurology exam for dystonia",
    "HP:0002376": "developmental history for regression",
    "HP:0000733": "exam for stereotypies",
    "HP:0001324": "CK / muscle evaluation",
    "HP:0000508": "dysmorphology exam for ptosis",
}


def _driving(query: list[str], disease_terms: list[str], ontology: Ontology) -> list[str]:
    driving: list[str] = []
    for term in query:
        if not ontology.has_term(term):
            continue
        best = max(
            (score_pair([term], [other], "resnik", ontology) for other in disease_terms),
            default=0.0,
        )
        if best >= ontology.information_content(term) * 0.5:
            driving.append(f"{term} {ontology.name_of(term)}")
    return driving


def _absent(query: list[str], disease_terms: list[str], ontology: Ontology) -> list[str]:
    query_set = set(query)
    absent: list[str] = []
    for term in disease_terms:
        if term not in query_set and term not in NONSPECIFIC:
            absent.append(f"{term} {ontology.name_of(term)}")
    return absent


def _additional_test(
    top_terms: list[str],
    runner_terms: list[str],
    ontology: Ontology,
) -> str:
    unique = [term for term in top_terms if term not in runner_terms]
    if not unique:
        unique = [term for term in top_terms if term not in NONSPECIFIC]
    if not unique:
        return "A more specific phenotype or targeted test is needed to change the ranking."
    term = max(unique, key=ontology.information_content)
    named = SUGGESTED_TEST.get(term)
    if named is not None:
        return f"{named} would change the ranking."
    return f"Testing for {ontology.name_of(term)} ({term}) would change the ranking."


def rank_text(
    text: str,
    *,
    polarity_aware: bool = True,
    measure: MeasureName = "phenomizer",
    ontology: Ontology | None = None,
) -> RankResponse:
    onto = ontology if ontology is not None else load_ontology()
    extracted = extract(text, polarity_aware=polarity_aware, ontology=onto)
    query = list(dict.fromkeys(extracted.positive_ids))
    if not polarity_aware:
        query = list(dict.fromkeys(m.hpo_id for m in extracted.mentions))
    negated = set(extracted.negated_ids) if polarity_aware else set()

    scored: list[tuple[float, list[str], DiseaseProfile]] = []
    for disease in onto.diseases:
        base = score_pair(query, disease.hpo_ids, measure, onto)
        penalty = 1.0
        for term in negated:
            if term in disease.hpo_ids:
                penalty *= 0.45
        scored.append((base * penalty, disease.hpo_ids, disease))

    scored.sort(key=lambda row: row[0], reverse=True)
    candidates: list[RankedCandidate] = []
    for index, (score, terms, disease) in enumerate(scored, start=1):
        runner_terms = scored[1][1] if len(scored) > 1 and index == 1 else scored[0][1]
        candidates.append(
            RankedCandidate(
                disease_id=disease.id,
                name=disease.name,
                score=score,
                rank=index,
                driving_phenotypes=_driving(query, terms, onto),
                expected_but_absent=_absent(query, terms, onto),
                additional_test=_additional_test(terms, runner_terms, onto),
            )
        )

    specific = [term for term in query if term not in NONSPECIFIC]
    top = candidates[0].score if candidates else 0.0
    second = candidates[1].score if len(candidates) > 1 else 0.0
    close = top > 0 and (top - second) / top < 0.12
    insufficient = (not specific) or top < 0.15 or (close and not specific)
    note = (
        "Insufficient to discriminate: only non-specific phenotypes, wide low-confidence set."
        if insufficient
        else "Distinctive phenotypes support a ranked hypothesis list, not a diagnosis."
    )
    return RankResponse(
        disclaimer=SAFETY_DISCLAIMER,
        text=text,
        measure=measure,
        mentions=extracted.mentions,
        unmapped=extracted.unmapped,
        candidates=candidates,
        insufficient_to_discriminate=insufficient,
        discrimination_note=note,
    )
