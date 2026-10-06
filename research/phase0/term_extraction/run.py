"""Polarity-aware vs naive extraction on 50 hand-labeled vignettes."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from phenorank.extract import extract
from phenorank.schemas import Vignette

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import md_table, pct, write_json  # noqa: E402

HERE = Path(__file__).resolve().parent
PROBE = HERE / "probe_set" / "vignettes.json"
RESULTS = HERE / "results"
POLARITIES = ("positive", "negated", "uncertain")


def _prf(tp: int, fp: int, fn: int) -> tuple[float, float, float]:
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return precision, recall, f1


def _score(vignettes: list[Vignette], polarity_aware: bool) -> dict[str, object]:
    per = {polarity: {"tp": 0, "fp": 0, "fn": 0} for polarity in POLARITIES}
    unmapped_tp = 0
    unmapped_gold = 0
    for vignette in vignettes:
        predicted = extract(vignette.text, polarity_aware=polarity_aware)
        pred_sets = {
            polarity: {(m.hpo_id, polarity) for m in predicted.mentions if m.polarity == polarity}
            for polarity in POLARITIES
        }
        gold_sets = {
            polarity: {(m.hpo_id, polarity) for m in vignette.mentions if m.polarity == polarity}
            for polarity in POLARITIES
        }
        for polarity in POLARITIES:
            gold = gold_sets[polarity]
            pred = pred_sets[polarity]
            per[polarity]["tp"] += len(gold & pred)
            per[polarity]["fp"] += len(pred - gold)
            per[polarity]["fn"] += len(gold - pred)
        gold_unmapped = {item.lower() for item in vignette.unmapped}
        pred_unmapped = {item.lower() for item in predicted.unmapped}
        unmapped_gold += len(gold_unmapped)
        unmapped_tp += len(gold_unmapped & pred_unmapped)
    out: dict[str, object] = {}
    for polarity, counts in per.items():
        precision, recall, f1 = _prf(counts["tp"], counts["fp"], counts["fn"])
        out[polarity] = {**counts, "precision": precision, "recall": recall, "f1": f1}
    out["unmapped_recall"] = (unmapped_tp / unmapped_gold) if unmapped_gold else 1.0
    out["unmapped_gold"] = unmapped_gold
    return out


def main() -> None:
    raw = json.loads(PROBE.read_text(encoding="utf-8"))
    vignettes = [Vignette.model_validate(item) for item in raw["vignettes"]]
    aware = _score(vignettes, True)
    naive = _score(vignettes, False)
    rows = []
    for polarity in POLARITIES:
        a = aware[polarity]  # type: ignore[index]
        n = naive[polarity]  # type: ignore[index]
        rows.append(
            [
                polarity,
                pct(a["f1"]),
                pct(a["precision"]),
                pct(a["recall"]),
                pct(n["f1"]),
                pct(n["precision"]),
                pct(n["recall"]),
            ]
        )
    decision = (
        "Ship the polarity-aware rule+lexicon extractor as the Phase 2 default. "
        "The naive baseline never emits negated or uncertain labels."
    )
    payload = {
        "n_vignettes": len(vignettes),
        "polarity_aware": aware,
        "naive_baseline": naive,
        "decision": decision,
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    write_json(RESULTS / "results.json", payload)
    table = md_table(
        [
            "polarity",
            "aware F1",
            "aware P",
            "aware R",
            "naive F1",
            "naive P",
            "naive R",
        ],
        rows,
    )
    md = (
        "# term_extraction results\n\n"
        f"n={len(vignettes)} hand-labeled vignettes.\n\n"
        f"{table}\n\n"
        f"Unmapped recall (aware): {pct(float(aware['unmapped_recall']))}.\n\n"
        f"{decision}\n"
    )
    (RESULTS / "results.md").write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
