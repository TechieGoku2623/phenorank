"""Polarity-aware HPO extractor. Never emits a term outside the committed subset."""

from __future__ import annotations

import re

from phenorank.ontology import Ontology, load_ontology
from phenorank.schemas import ExtractedMention, ExtractionResult, Polarity

_NEGATION = re.compile(
    r"\b(no|not|without|denied|denies|ruled out|negative for|absent|never|free of)\b",
    re.IGNORECASE,
)
_UNCERTAIN = re.compile(
    r"\b(possible|possibly|maybe|suspected|questionable|borderline|probable)\b",
    re.IGNORECASE,
)
_WORD = r"(?<![A-Za-z0-9]){phrase}(?![A-Za-z0-9])"


def _sentence_prefix(text: str, start: int) -> str:
    left = text[:start]
    last_stop = max(left.rfind("."), left.rfind("!"), left.rfind("?"))
    return left[last_stop + 1 :]


def _has_lexicon_phrase(text: str, lexicon: dict[str, str]) -> bool:
    for phrase in lexicon:
        pattern = re.compile(_WORD.format(phrase=re.escape(phrase)), re.IGNORECASE)
        if pattern.search(text):
            return True
    return False


def _polarity(text: str, start: int, lexicon: dict[str, str]) -> Polarity:
    """Apply the nearest cue in this sentence if it binds to this mention."""

    prefix = _sentence_prefix(text, start)
    cues: list[tuple[int, Polarity]] = []
    for match in _NEGATION.finditer(prefix):
        cues.append((match.end(), "negated"))
    for match in _UNCERTAIN.finditer(prefix):
        cues.append((match.end(), "uncertain"))
    if not cues:
        return "positive"
    cues.sort()
    cue_end, polarity = cues[-1]
    if _has_lexicon_phrase(prefix[cue_end:], lexicon):
        return "positive"
    return polarity


def _overlaps(start: int, end: int, taken: list[tuple[int, int]]) -> bool:
    return any(
        start < existing_end and end > existing_start for existing_start, existing_end in taken
    )


def extract(
    text: str,
    *,
    polarity_aware: bool = True,
    ontology: Ontology | None = None,
) -> ExtractionResult:
    """Map free text onto the committed HPO subset.

    The naive baseline (`polarity_aware=False`) labels every mention positive.
    Unmapped committed phrases are reported and never approximated to a neighbor.
    """

    onto = ontology if ontology is not None else load_ontology()
    taken: list[tuple[int, int]] = []
    mentions: list[ExtractedMention] = []
    unmapped: list[str] = []

    unmapped_sorted = sorted(onto.unmapped_phrases, key=len, reverse=True)
    for phrase in unmapped_sorted:
        pattern = re.compile(_WORD.format(phrase=re.escape(phrase)), re.IGNORECASE)
        for match in pattern.finditer(text):
            if _overlaps(match.start(), match.end(), taken):
                continue
            taken.append((match.start(), match.end()))
            unmapped.append(match.group(0))

    phrases = sorted(onto.lexicon, key=len, reverse=True)
    for phrase in phrases:
        pattern = re.compile(_WORD.format(phrase=re.escape(phrase)), re.IGNORECASE)
        hpo_id = onto.lexicon[phrase]
        if not onto.has_term(hpo_id):
            continue
        for match in pattern.finditer(text):
            if _overlaps(match.start(), match.end(), taken):
                continue
            taken.append((match.start(), match.end()))
            polarity = (
                _polarity(text, match.start(), onto.lexicon) if polarity_aware else "positive"
            )
            mentions.append(
                ExtractedMention(
                    surface=match.group(0),
                    hpo_id=hpo_id,
                    polarity=polarity,
                    start=match.start(),
                    end=match.end(),
                )
            )

    mentions.sort(key=lambda item: item.start)
    return ExtractionResult(mentions=mentions, unmapped=unmapped)
