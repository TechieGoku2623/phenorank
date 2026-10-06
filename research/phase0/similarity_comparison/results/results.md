# similarity_comparison results

Default measure = phenomizer. Criterion: higher top-1 on the committed simulated patients. Overlap-count is the baseline, not a shipped similarity. DuckDB argmax=overlap.

| measure | top-1 | top-5 | top-20 | MRR | n |
| --- | --- | --- | --- | --- | --- |
| overlap-count (baseline) | 0.955 | 1.000 | 1.000 | 0.977 | 22 |
| resnik (asymmetric) | 0.955 | 1.000 | 1.000 | 0.977 | 22 |
| phenomizer (symmetric) | 0.955 | 1.000 | 1.000 | 0.970 | 22 |
