# noise_degradation

## What is measured

Top-1 ranking accuracy of the default Phenomizer-style measure as phenotype
input degrades: terms dropped and unrelated noise terms added.

## Why it decides something

Real notes omit findings and mention unrelated ones. If accuracy collapses
under modest drop/noise, the approach does not survive realistic input and
Phase 2 must add elicitation or a confirmation step.

## How to run

```bash
uv run python research/phase0/noise_degradation/run.py
```

Seed: 0. Uses the same disease profiles as `similarity_comparison`.
