# Phase 0 harnesses

`make research` runs these in order:

1. `term_extraction/probe_set/build.py` — rebuild the committed 50-vignette gold set
2. `term_extraction/run.py` — polarity-aware vs naive extraction accuracy
3. `similarity_comparison/run.py` — Resnik vs Phenomizer-style ranking
4. `noise_degradation/run.py` — top-1 accuracy as terms are dropped or noised
5. `render_docs.py` — write `docs/phase-0/research-memo.md`, `docs/EVALUATION.md`, and the measured tables in `README.md`

No number in the memo is typed by hand. If a quantity cannot be produced here, the memo says **unmeasured** and names the measurement that would settle it.
