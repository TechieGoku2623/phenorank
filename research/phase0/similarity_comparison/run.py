"""Resnik vs Phenomizer-style ranking plus overlap-count baseline.

Reports top-1 / top-5 / top-20 and MRR on simulated patients.
"""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb

from phenorank.metrics import ranking_metrics
from phenorank.ontology import load_ontology

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import md_table, pct, write_json  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
SEED = 0
DROPS = (0, 1)


def _patients() -> list[dict[str, object]]:
    onto = load_ontology()
    patients: list[dict[str, object]] = []
    index = 0
    for disease in onto.diseases:
        terms = list(disease.hpo_ids)
        for drop in DROPS:
            if drop >= len(terms):
                continue
            kept = terms if drop == 0 else terms[:-drop]
            patients.append(
                {
                    "patient_id": f"p{index:03d}",
                    "gold_disease": disease.id,
                    "hpo_ids": kept,
                }
            )
            index += 1
    return patients


def main() -> None:
    patients = _patients()
    (HERE / "probe_set").mkdir(parents=True, exist_ok=True)
    write_json(HERE / "probe_set" / "patients.json", {"seed": SEED, "patients": patients})
    overlap = ranking_metrics(patients, "overlap")
    resnik = ranking_metrics(patients, "resnik")
    phenomizer = ranking_metrics(patients, "phenomizer")
    conn = duckdb.connect(":memory:")
    conn.execute("CREATE TABLE m (measure VARCHAR, top1 DOUBLE, mrr DOUBLE)")
    conn.executemany(
        "INSERT INTO m VALUES (?, ?, ?)",
        [
            ("overlap", overlap["top1"], overlap["mrr"]),
            ("resnik", resnik["top1"], resnik["mrr"]),
            ("phenomizer", phenomizer["top1"], phenomizer["mrr"]),
        ],
    )
    sql_best = str(
        conn.execute("SELECT measure FROM m ORDER BY top1 DESC, mrr DESC LIMIT 1").fetchone()[0]
    )
    winner = "phenomizer" if phenomizer["top1"] >= resnik["top1"] else "resnik"
    decision = (
        f"Default measure = {winner}. Criterion: higher top-1 on the committed "
        "simulated patients. Overlap-count is the baseline, not a shipped similarity. "
        f"DuckDB argmax={sql_best}."
    )
    payload = {
        "seed": SEED,
        "n_patients": len(patients),
        "overlap_baseline": overlap,
        "resnik": resnik,
        "phenomizer": phenomizer,
        "default_measure": winner,
        "decision": decision,
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    write_json(RESULTS / "results.json", payload)
    table = md_table(
        ["measure", "top-1", "top-5", "top-20", "MRR", "n"],
        [
            [
                "overlap-count (baseline)",
                pct(overlap["top1"]),
                pct(overlap["top5"]),
                pct(overlap["top20"]),
                pct(overlap["mrr"]),
                str(int(overlap["n"])),
            ],
            [
                "resnik (asymmetric)",
                pct(resnik["top1"]),
                pct(resnik["top5"]),
                pct(resnik["top20"]),
                pct(resnik["mrr"]),
                str(int(resnik["n"])),
            ],
            [
                "phenomizer (symmetric)",
                pct(phenomizer["top1"]),
                pct(phenomizer["top5"]),
                pct(phenomizer["top20"]),
                pct(phenomizer["mrr"]),
                str(int(phenomizer["n"])),
            ],
        ],
    )
    md = f"# similarity_comparison results\n\n{decision}\n\n{table}\n"
    (RESULTS / "results.md").write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
