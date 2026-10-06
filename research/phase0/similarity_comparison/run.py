"""Resnik vs Phenomizer-style ranking on simulated patients."""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb

from phenorank.ontology import load_ontology
from phenorank.similarity import score_pair

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


def _accuracy(patients: list[dict[str, object]], measure: str) -> dict[str, float]:
    onto = load_ontology()
    top1 = 0
    top3 = 0
    rows: list[tuple[str, str, float, int]] = []
    for patient in patients:
        query = list(patient["hpo_ids"])  # type: ignore[arg-type]
        ranked = sorted(
            (
                (score_pair(query, disease.hpo_ids, measure, onto), disease.id)
                for disease in onto.diseases
            ),
            reverse=True,
        )
        gold = str(patient["gold_disease"])
        order = [disease_id for _, disease_id in ranked]
        hit1 = int(order[0] == gold)
        hit3 = int(gold in order[:3])
        top1 += hit1
        top3 += hit3
        rows.append((str(patient["patient_id"]), gold, ranked[0][0], hit1))
    conn = duckdb.connect(":memory:")
    conn.execute(
        "CREATE TABLE ranks (patient_id VARCHAR, gold VARCHAR, top_score DOUBLE, hit1 INTEGER)"
    )
    conn.executemany("INSERT INTO ranks VALUES (?, ?, ?, ?)", rows)
    sql_top1 = float(conn.execute("SELECT AVG(hit1) FROM ranks").fetchone()[0])  # type: ignore[index]
    n = len(patients)
    return {
        "top1": top1 / n,
        "top3": top3 / n,
        "sql_top1": sql_top1,
        "n": float(n),
    }


def main() -> None:
    patients = _patients()
    (HERE / "probe_set").mkdir(parents=True, exist_ok=True)
    write_json(HERE / "probe_set" / "patients.json", {"seed": SEED, "patients": patients})
    resnik = _accuracy(patients, "resnik")
    phenomizer = _accuracy(patients, "phenomizer")
    winner = "phenomizer" if phenomizer["top1"] >= resnik["top1"] else "resnik"
    decision = (
        f"Default measure = {winner}. Criterion: higher top-1 on the committed "
        "simulated patients. Only Resnik and Phenomizer-style are compared."
    )
    payload = {
        "seed": SEED,
        "n_patients": len(patients),
        "resnik": resnik,
        "phenomizer": phenomizer,
        "default_measure": winner,
        "decision": decision,
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    write_json(RESULTS / "results.json", payload)
    table = md_table(
        ["measure", "top-1", "top-3", "n"],
        [
            [
                "resnik (asymmetric)",
                pct(resnik["top1"]),
                pct(resnik["top3"]),
                str(int(resnik["n"])),
            ],
            [
                "phenomizer (symmetric)",
                pct(phenomizer["top1"]),
                pct(phenomizer["top3"]),
                str(int(phenomizer["n"])),
            ],
        ],
    )
    md = f"# similarity_comparison results\n\n{decision}\n\n{table}\n"
    (RESULTS / "results.md").write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
