# Data

Phase 0 does not download HPO releases, OMIM, or clinic notes. The committed
objects are:

- `data/sample/*.txt` — five designed demo vignettes (see `data/sample/README.md`)
- `data/sample/hpo_subset.json` — toy ontology DAG
- `data/sample/diseases.json` — ten designed annotation profiles
- `data/sample/lexicon.json` — phrase map plus out-of-ontology phrases
- `research/phase0/term_extraction/probe_set/vignettes.json` — 50 hand-labeled
  synthetic vignettes

No patient-identifiable data. No restricted-access corpus. No live API.

HPO and disease-annotation license notes for production sources are in
`docs/phase-0/research-memo.md` §3. Full-ontology redistribution is out of
scope. Ingest in later phases writes a manifest (source URL, retrieval
timestamp, term count, sha256) and keeps raw files in gitignored bronze
storage.

OMIM narrative text is not committed. Profiles use public identifiers and
designed HPO lists only.
