"""Typed payloads. Every ranking response states this is not a diagnosis."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from phenorank import SAFETY_DISCLAIMER

Polarity = Literal["positive", "negated", "uncertain"]
MeasureName = Literal["resnik", "phenomizer"]


class ExtractedMention(BaseModel):
    surface: str
    hpo_id: str
    polarity: Polarity
    start: int
    end: int


class GoldMention(BaseModel):
    surface: str
    hpo_id: str
    polarity: Polarity


class Vignette(BaseModel):
    vignette_id: str
    text: str
    mentions: list[GoldMention]
    unmapped: list[str] = Field(default_factory=list)


class ExtractionResult(BaseModel):
    disclaimer: str = SAFETY_DISCLAIMER
    mentions: list[ExtractedMention]
    unmapped: list[str] = Field(default_factory=list)

    @property
    def positive_ids(self) -> list[str]:
        return [m.hpo_id for m in self.mentions if m.polarity == "positive"]

    @property
    def negated_ids(self) -> list[str]:
        return [m.hpo_id for m in self.mentions if m.polarity == "negated"]

    @property
    def uncertain_ids(self) -> list[str]:
        return [m.hpo_id for m in self.mentions if m.polarity == "uncertain"]


class RankedCandidate(BaseModel):
    disease_id: str
    name: str
    score: float
    rank: int
    driving_phenotypes: list[str]
    expected_but_absent: list[str]
    additional_test: str


class RankResponse(BaseModel):
    disclaimer: str = SAFETY_DISCLAIMER
    text: str
    measure: MeasureName
    mentions: list[ExtractedMention]
    unmapped: list[str] = Field(default_factory=list)
    candidates: list[RankedCandidate]
    insufficient_to_discriminate: bool
    discrimination_note: str


class SampleCase(BaseModel):
    sample_id: str
    file: str
    path_exercised: str
    expected_behavior: str
