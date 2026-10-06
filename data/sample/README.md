# Sample vignettes

These five texts are designed, not sampled from a clinic. Each one exists to
exercise a path the walkthrough names. The committed HPO subset, disease
profiles, and lexicon live beside them so `make demo` and `make test` run
with no network and no live ontology API.

This directory contains no patient-identifiable data. The vignettes are
synthetic teaching cases. This is hypothesis generation, not a diagnosis.

| File | Why it is here |
| --- | --- |
| `classic.txt` | Distinctive GLUT1-like set. Must rank OMIM:606777 at top-1. |
| `negation.txt` | "No seizures" and "ruled out ataxia". Naive extraction ranks the wrong disease first; polarity-aware ranks Prader-Willi. |
| `nonspecific.txt` | Only GDD and failure to thrive. Wide low-confidence set, `insufficient_to_discriminate`. |
| `lay.txt` | Lay language (`floppy baby`, `small head`, `crossed eyes`) must map to committed HPO terms. |
| `unmapped.txt` | `sparkly toenail dystrophy` is not in the subset. Report unmapped; never approximate. |

Supporting files:

- `hpo_subset.json` — toy DAG used for Resnik IC and Phenomizer-style similarity
- `diseases.json` — ten annotation profiles
- `lexicon.json` — phrase → HPO map plus committed out-of-ontology phrases
- `manifest.json` — what `phenorank demo-plan` prints

No LLM cache is used in Phase 0. No live API.
