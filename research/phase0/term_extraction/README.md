# term_extraction

## What is measured

Precision and recall of HPO mention extraction on 50 hand-labeled synthetic
vignettes, reported separately for positive, negated, and uncertain mentions.
The polarity-aware extractor (rules + committed lexicon) is compared to a
naive baseline that labels every mention positive.

## Why it decides something

If negation and uncertainty are ignored, ranking treats "no seizures" as a
seizure. That is the failure mode `negation.txt` exists to catch. This
harness decides whether the rule+lexicon extractor is good enough to ship as
the Phase 2 default, or whether a model-based extractor is required.

## How to run

```bash
uv run python research/phase0/term_extraction/run.py
```

Seed: 0. The vignettes are designed and committed under `probe_set/vignettes.json`.

## Gold-label source

Gold spans and polarities were written with the vignettes. They are not model
outputs. The extractor may only emit terms from the committed HPO subset.
