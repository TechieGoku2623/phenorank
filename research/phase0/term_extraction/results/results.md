# term_extraction results

n=50 hand-labeled vignettes.

| polarity | aware F1 | aware P | aware R | naive F1 | naive P | naive R |
| --- | --- | --- | --- | --- | --- | --- |
| positive | 1.000 | 1.000 | 1.000 | 0.845 | 0.732 | 1.000 |
| negated | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| uncertain | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 |

Unmapped recall (aware): 1.000.

Ship the polarity-aware rule+lexicon extractor as the Phase 2 default. The naive baseline never emits negated or uncertain labels.
