# Architecture (Phase 1)

Hypothesis generation, **not** a diagnosis. Every typed payload includes
`SAFETY_DISCLAIMER`. No credentials are required. The committed HPO subset
is the only term space the engine may emit.

## Data contracts

| Object | Role |
| --- | --- |
| `ExtractionResult` | Mentions (`hpo_id`, `polarity` ∈ {positive, negated, uncertain}), `unmapped`, disclaimer |
| `RankResponse` | Mentions + ranked `RankedCandidate` rows + `insufficient_to_discriminate` |
| `RankedCandidate` | `disease_id`, `name`, `score`, `rank`, `driving_phenotypes`, `expected_but_absent`, `additional_test` |
| `hpo_subset.json` | Closed DAG. A term not in this file is never emitted as an HPO id |
| `lexicon.json` | Phrase → subset id, plus committed out-of-ontology phrases |
| `diseases.json` | Ten designed annotation profiles |

POST `/rank` (optional) accepts `{ "vignette": "<text>" }` and returns
`RankResponse` JSON. There is no auth.

## Event topology

```
vignette --extract--> mentions + unmapped
                 |           |
                 |           +-- unmapped phrases reported, never approximated
                 v
          positive ids only (uncertain/negated held out)
                 |
                 +-- Resnik or Phenomizer-style set similarity
                 v
            RankResponse + explanation trail
```

The overlap-count scorer is a **baseline** used in `make eval`. It is not a
third shipped similarity.

## CLI surface (Phase 2)

- `phenorank extract --vignette PATH`
- `phenorank rank --vignette PATH [--explain] [--compare-naive]`
- `phenorank serve` — optional POST `/rank`
- `phenorank demo` — committed walkthrough

## Constraints

1. Never emit `HP:` ids outside `hpo_subset.json`.
2. Naive extractor (`polarity_aware=False`) labels every mention positive.
3. Uncertain mentions do not enter the positive query set.
4. Nonspecific-only queries set `insufficient_to_discriminate`.
5. No live HPO/OMIM/API credentials.
