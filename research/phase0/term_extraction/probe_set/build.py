"""Write the committed 50 hand-labeled vignettes."""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def vignettes() -> list[dict[str, object]]:
    return [
        _v(
            "v01",
            "Toddler with seizures and ataxia.",
            [_m("seizures", "HP:0001250"), _m("ataxia", "HP:0001251")],
        ),
        _v(
            "v02",
            "Floppy baby with poor feeding.",
            [_m("Floppy baby", "HP:0001290"), _m("poor feeding", "HP:0011968")],
        ),
        _v(
            "v03",
            "Child with microcephaly and global developmental delay.",
            [_m("microcephaly", "HP:0000252"), _m("global developmental delay", "HP:0001263")],
        ),
        _v(
            "v04",
            "Patient with ptosis and pulmonic stenosis.",
            [_m("ptosis", "HP:0000508"), _m("pulmonic stenosis", "HP:0001642")],
        ),
        _v(
            "v05",
            "Adult with nystagmus and visual impairment.",
            [_m("nystagmus", "HP:0000639"), _m("visual impairment", "HP:0000505")],
        ),
        _v(
            "v06",
            "Child with scoliosis and cafe-au-lait spots.",
            [_m("scoliosis", "HP:0002650"), _m("cafe-au-lait spots", "HP:0000957")],
        ),
        _v(
            "v07",
            "Infant with lactic acidosis and cardiomyopathy.",
            [_m("lactic acidosis", "HP:0003128"), _m("cardiomyopathy", "HP:0001638")],
        ),
        _v(
            "v08",
            "Toddler with dystonia and seizures.",
            [_m("dystonia", "HP:0001332"), _m("seizures", "HP:0001250")],
        ),
        _v(
            "v09",
            "Child with developmental regression and stereotypical behavior.",
            [
                _m("developmental regression", "HP:0002376"),
                _m("stereotypical behavior", "HP:0000733"),
            ],
        ),
        _v(
            "v10",
            "Infant with muscle weakness and hypotonia.",
            [_m("muscle weakness", "HP:0001324"), _m("hypotonia", "HP:0001290")],
        ),
        _v(
            "v11",
            "Patient with short stature and failure to thrive.",
            [_m("short stature", "HP:0004322"), _m("failure to thrive", "HP:0001508")],
        ),
        _v(
            "v12",
            "Child with intellectual disability and motor delay.",
            [_m("intellectual disability", "HP:0001249"), _m("motor delay", "HP:0001270")],
        ),
        _v(
            "v13",
            "Toddler with strabismus and ptosis.",
            [_m("strabismus", "HP:0000486"), _m("ptosis", "HP:0000508")],
        ),
        _v(
            "v14",
            "Infant with hypoglycemia and seizures.",
            [_m("hypoglycemia", "HP:0001943"), _m("seizures", "HP:0001250")],
        ),
        _v(
            "v15",
            "Child with thrombocytopenia and scoliosis.",
            [_m("thrombocytopenia", "HP:0001873"), _m("scoliosis", "HP:0002650")],
        ),
        _v(
            "v16",
            "Patient with cerebral atrophy and microcephaly.",
            [_m("cerebral atrophy", "HP:0002059"), _m("microcephaly", "HP:0000252")],
        ),
        _v(
            "v17",
            "Toddler with ataxia and dystonia.",
            [_m("ataxia", "HP:0001251"), _m("dystonia", "HP:0001332")],
        ),
        _v(
            "v18",
            "Child with hypopigmentation of the skin and nystagmus.",
            [_m("hypopigmentation of the skin", "HP:0001010"), _m("nystagmus", "HP:0000639")],
        ),
        _v(
            "v19",
            "Infant with poor feeding and failure to thrive.",
            [_m("poor feeding", "HP:0011968"), _m("failure to thrive", "HP:0001508")],
        ),
        _v(
            "v20",
            "Patient with cardiomyopathy and muscle weakness.",
            [_m("cardiomyopathy", "HP:0001638"), _m("muscle weakness", "HP:0001324")],
        ),
        _v(
            "v21",
            "Infant with hypotonia. No seizures.",
            [_m("hypotonia", "HP:0001290"), _m("seizures", "HP:0001250", "negated")],
        ),
        _v(
            "v22",
            "Child with microcephaly. Ruled out ataxia.",
            [_m("microcephaly", "HP:0000252"), _m("ataxia", "HP:0001251", "negated")],
        ),
        _v(
            "v23",
            "Toddler with feeding difficulties, without seizures.",
            [_m("feeding difficulties", "HP:0011968"), _m("seizures", "HP:0001250", "negated")],
        ),
        _v(
            "v24",
            "Patient with short stature, negative for nystagmus.",
            [_m("short stature", "HP:0004322"), _m("nystagmus", "HP:0000639", "negated")],
        ),
        _v(
            "v25",
            "Infant with hypotonia and feeding difficulties. No seizures. Ruled out ataxia.",
            [
                _m("hypotonia", "HP:0001290"),
                _m("feeding difficulties", "HP:0011968"),
                _m("seizures", "HP:0001250", "negated"),
                _m("ataxia", "HP:0001251", "negated"),
            ],
        ),
        _v(
            "v26",
            "Child with global developmental delay, denied seizures.",
            [
                _m("global developmental delay", "HP:0001263"),
                _m("seizures", "HP:0001250", "negated"),
            ],
        ),
        _v(
            "v27",
            "Toddler with ptosis, absent scoliosis.",
            [_m("ptosis", "HP:0000508"), _m("scoliosis", "HP:0002650", "negated")],
        ),
        _v(
            "v28",
            "Patient with muscle weakness, never ataxia.",
            [_m("muscle weakness", "HP:0001324"), _m("ataxia", "HP:0001251", "negated")],
        ),
        _v(
            "v29",
            "Infant with failure to thrive, free of seizures.",
            [_m("failure to thrive", "HP:0001508"), _m("seizures", "HP:0001250", "negated")],
        ),
        _v(
            "v30",
            "Child with intellectual disability, no dystonia.",
            [_m("intellectual disability", "HP:0001249"), _m("dystonia", "HP:0001332", "negated")],
        ),
        _v(
            "v31",
            "Toddler with strabismus, without nystagmus.",
            [_m("strabismus", "HP:0000486"), _m("nystagmus", "HP:0000639", "negated")],
        ),
        _v(
            "v32",
            "Patient with cardiomyopathy, ruled out lactic acidosis.",
            [_m("cardiomyopathy", "HP:0001638"), _m("lactic acidosis", "HP:0003128", "negated")],
        ),
        _v(
            "v33",
            "Infant with hypotonia, not seizures.",
            [_m("hypotonia", "HP:0001290"), _m("seizures", "HP:0001250", "negated")],
        ),
        _v(
            "v34",
            "Child with cafe-au-lait spots, no pulmonic stenosis.",
            [
                _m("cafe-au-lait spots", "HP:0000957"),
                _m("pulmonic stenosis", "HP:0001642", "negated"),
            ],
        ),
        _v(
            "v35",
            "Toddler with ataxia, denied developmental regression.",
            [_m("ataxia", "HP:0001251"), _m("developmental regression", "HP:0002376", "negated")],
        ),
        _v(
            "v36",
            "Child with seizures and possible ataxia.",
            [_m("seizures", "HP:0001250"), _m("ataxia", "HP:0001251", "uncertain")],
        ),
        _v(
            "v37",
            "Infant with hypotonia and suspected microcephaly.",
            [_m("hypotonia", "HP:0001290"), _m("microcephaly", "HP:0000252", "uncertain")],
        ),
        _v(
            "v38",
            "Toddler with maybe nystagmus and visual impairment.",
            [_m("nystagmus", "HP:0000639", "uncertain"), _m("visual impairment", "HP:0000505")],
        ),
        _v(
            "v39",
            "Patient with questionable ptosis and short stature.",
            [_m("ptosis", "HP:0000508", "uncertain"), _m("short stature", "HP:0004322")],
        ),
        _v(
            "v40",
            "Child with global developmental delay and possible seizures.",
            [
                _m("global developmental delay", "HP:0001263"),
                _m("seizures", "HP:0001250", "uncertain"),
            ],
        ),
        _v(
            "v41",
            "Infant with borderline hypotonia and feeding difficulties.",
            [_m("hypotonia", "HP:0001290", "uncertain"), _m("feeding difficulties", "HP:0011968")],
        ),
        _v(
            "v42",
            "Toddler with probable dystonia and ataxia.",
            [_m("dystonia", "HP:0001332", "uncertain"), _m("ataxia", "HP:0001251")],
        ),
        _v(
            "v43",
            "Patient with possibly lactic acidosis and cardiomyopathy.",
            [_m("lactic acidosis", "HP:0003128", "uncertain"), _m("cardiomyopathy", "HP:0001638")],
        ),
        _v(
            "v44",
            "Child with suspected scoliosis and cafe-au-lait spots.",
            [_m("scoliosis", "HP:0002650", "uncertain"), _m("cafe-au-lait spots", "HP:0000957")],
        ),
        _v(
            "v45",
            "Infant with possible strabismus and microcephaly.",
            [_m("strabismus", "HP:0000486", "uncertain"), _m("microcephaly", "HP:0000252")],
        ),
        _v(
            "v46",
            "Toddler with hypotonia and sparkly toenail dystrophy.",
            [_m("hypotonia", "HP:0001290")],
            ["sparkly toenail dystrophy"],
        ),
        _v(
            "v47",
            "Child with seizures and photonic elbow aura.",
            [_m("seizures", "HP:0001250")],
            ["photonic elbow aura"],
        ),
        _v(
            "v48",
            "Infant with feeding difficulties and lunar nail shimmer.",
            [_m("feeding difficulties", "HP:0011968")],
            ["lunar nail shimmer"],
        ),
        _v(
            "v49",
            "Patient with ataxia and velvet knuckle sign.",
            [_m("ataxia", "HP:0001251")],
            ["velvet knuckle sign"],
        ),
        _v(
            "v50",
            "Child with global developmental delay and prismatic scalp sheen.",
            [_m("global developmental delay", "HP:0001263")],
            ["prismatic scalp sheen"],
        ),
    ]


def _m(surface: str, hpo_id: str, polarity: str = "positive") -> dict[str, str]:
    return {"surface": surface, "hpo_id": hpo_id, "polarity": polarity}


def _v(
    vignette_id: str,
    text: str,
    mentions: list[dict[str, str]],
    unmapped: list[str] | None = None,
) -> dict[str, object]:
    return {
        "vignette_id": vignette_id,
        "text": text,
        "mentions": mentions,
        "unmapped": unmapped or [],
    }


def main() -> None:
    payload = {"n": 50, "seed": 0, "vignettes": vignettes()}
    path = HERE / "vignettes.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {path} n={len(payload['vignettes'])}")


if __name__ == "__main__":
    main()
