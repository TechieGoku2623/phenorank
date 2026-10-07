"""Plain-text rendering for extract/rank CLI output."""

from __future__ import annotations

from phenorank import SAFETY_DISCLAIMER
from phenorank.ontology import Ontology, load_ontology
from phenorank.schemas import ExtractionResult, RankResponse


def render_extract(result: ExtractionResult, ontology: Ontology | None = None) -> str:
    onto = ontology if ontology is not None else load_ontology()
    lines = [SAFETY_DISCLAIMER, "", "extracted HPO mentions (committed subset only)", ""]
    if not result.mentions:
        lines.append("(no mapped mentions)")
    for mention in result.mentions:
        name = onto.name_of(mention.hpo_id)
        lines.append(
            f"  {mention.hpo_id:<12}  {mention.polarity:<10}  {name:<24}  "
            f"surface={mention.surface!r}"
        )
    lines.append("")
    if result.unmapped:
        lines.append("unmapped (reported, not approximated to a neighbor term):")
        for item in result.unmapped:
            lines.append(f"  - {item}")
    else:
        lines.append("unmapped: (none)")
    lines.append("")
    lines.append(f"positive={result.positive_ids}")
    lines.append(f"negated={result.negated_ids}")
    lines.append(f"uncertain={result.uncertain_ids}")
    lines.append("")
    lines.append(SAFETY_DISCLAIMER)
    return "\n".join(lines)


def _candidate_block(response: RankResponse, *, explain: bool, limit: int = 8) -> list[str]:
    lines: list[str] = []
    for candidate in response.candidates[:limit]:
        lines.append(
            f"  {candidate.rank:>2}. {candidate.score:6.3f}  "
            f"{candidate.disease_id:<22}  {candidate.name}"
        )
        if explain:
            driving = "; ".join(candidate.driving_phenotypes) or "(none)"
            absent = "; ".join(candidate.expected_but_absent) or "(none)"
            if len(driving) > 68:
                driving = driving[:65] + "..."
            if len(absent) > 68:
                absent = absent[:65] + "..."
            lines.append(f"      driving:              {driving}")
            lines.append(f"      expected-but-absent:  {absent}")
            next_test = candidate.additional_test
            if len(next_test) > 68:
                next_test = next_test[:65] + "..."
            lines.append(f"      next test:            {next_test}")
    return lines


def render_rank(response: RankResponse, *, explain: bool = False, limit: int = 8) -> str:
    lines = [
        SAFETY_DISCLAIMER,
        "",
        f"measure: {response.measure}",
        f"insufficient_to_discriminate: {response.insufficient_to_discriminate}",
        response.discrimination_note,
        "",
        "ranked candidates (hypothesis list, not a diagnosis)",
        "",
    ]
    lines.extend(_candidate_block(response, explain=explain, limit=limit))
    if response.unmapped:
        lines.append("")
        lines.append("unmapped (not approximated):")
        for item in response.unmapped:
            lines.append(f"  - {item}")
    lines.append("")
    lines.append(SAFETY_DISCLAIMER)
    return "\n".join(lines)


def render_compare(aware: RankResponse, naive: RankResponse) -> str:
    aware_top = aware.candidates[0] if aware.candidates else None
    naive_top = naive.candidates[0] if naive.candidates else None
    differ = (
        aware_top is not None
        and naive_top is not None
        and aware_top.disease_id != naive_top.disease_id
    )
    lines = [
        SAFETY_DISCLAIMER,
        "",
        "side-by-side ranking: polarity-aware vs naive (all mentions positive)",
        "",
        "rank  polarity-aware                         naive (all mentions +)",
    ]
    n = max(len(aware.candidates), len(naive.candidates))
    for i in range(min(n, 4)):
        a = aware.candidates[i] if i < len(aware.candidates) else None
        b = naive.candidates[i] if i < len(naive.candidates) else None
        a_id = a.disease_id if a else ""
        a_name = (a.name if a else "")[:28]
        b_id = b.disease_id if b else ""
        b_name = (b.name if b else "")[:28]
        lines.append(f"{i + 1:<4}  {a_id:<16} {a_name:<28}  {b_id:<16} {b_name}")
    lines.append("")
    if aware_top and naive_top:
        lines.append(f"polarity-aware top-1: {aware_top.disease_id}  {aware_top.name}")
        lines.append(f"naive top-1:          {naive_top.disease_id}  {naive_top.name}")
        lines.append(f"top-1 differs:        {str(differ).lower()}")
    lines.append("")
    lines.append(aware.discrimination_note)
    lines.append("")
    lines.append(SAFETY_DISCLAIMER)
    return "\n".join(lines)
