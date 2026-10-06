"""Accuracy as phenotype input is dropped or noised. Seed 0."""

from __future__ import annotations

import sys
from pathlib import Path

from phenorank.ontology import load_ontology
from phenorank.similarity import score_pair

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import md_table, pct, write_json  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
SEED = 0
DROP_FRACS = (0.0, 0.3, 0.5)
NOISE_COUNTS = (0, 1, 2)
NOISE_POOL = ["HP:0001873", "HP:0000077", "HP:0001943"]


def _top1(query: list[str], gold: str) -> int:
    onto = load_ontology()
    ranked = sorted(
        (
            (score_pair(query, disease.hpo_ids, "phenomizer", onto), disease.id)
            for disease in onto.diseases
        ),
        reverse=True,
    )
    return int(ranked[0][1] == gold)


def main() -> None:
    onto = load_ontology()
    cells: dict[str, dict[str, float]] = {}
    rows: list[list[str]] = []
    for drop in DROP_FRACS:
        for noise in NOISE_COUNTS:
            hits = 0
            n = 0
            for disease in onto.diseases:
                terms = list(disease.hpo_ids)
                keep_n = max(1, int(round(len(terms) * (1.0 - drop))))
                query = terms[:keep_n]
                extra = [term for term in NOISE_POOL if term not in query][:noise]
                hits += _top1(query + extra, disease.id)
                n += 1
            acc = hits / n
            key = f"drop_{drop:.1f}_noise_{noise}"
            cells[key] = {"accuracy": acc, "n": float(n), "drop": drop, "noise": noise}
            rows.append([f"{drop:.1f}", str(noise), pct(acc), str(n)])
    clean = cells["drop_0.0_noise_0"]["accuracy"]
    harsh = cells["drop_0.5_noise_2"]["accuracy"]
    survives = harsh >= 0.5
    decision = (
        "The approach survives realistic input (harsh-cell top-1 ≥ 0.50)."
        if survives
        else "Accuracy collapses under drop+noise; Phase 2 needs elicitation before ranking."
    )
    payload = {
        "seed": SEED,
        "cells": cells,
        "clean_top1": clean,
        "harsh_top1": harsh,
        "survives_realistic_input": survives,
        "decision": decision,
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    write_json(RESULTS / "results.json", payload)
    table = md_table(["drop fraction", "noise terms", "top-1", "n diseases"], rows)
    md = (
        f"# noise_degradation results\n\n{decision}\n\n"
        f"Clean top-1={pct(clean)}; harsh (drop 0.5 + 2 noise) top-1={pct(harsh)}.\n\n"
        f"{table}\n"
    )
    (RESULTS / "results.md").write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
