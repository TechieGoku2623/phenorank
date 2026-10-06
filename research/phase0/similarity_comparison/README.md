# similarity_comparison

## What is measured

Top-1 / top-5 / top-20 hit rate and MRR of Resnik (asymmetric mean-best IC),
the Phenomizer-style symmetric measure, and an overlap-count baseline on
committed simulated patients with known disease labels.

## Why it decides something

Phase 2 must pick one default measure. This harness decides whether the
symmetric Phenomizer-style score beats asymmetric Resnik enough to be the
default, without inventing a third similarity.

## How to run

```bash
uv run python research/phase0/similarity_comparison/run.py
```

Seed: 0. Patients are generated from the committed disease profiles.
