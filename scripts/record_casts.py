"""Write asciinema v2 casts of the Phase 3 walkthrough. No credentials."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "demo"
WIDTH = 120
HEIGHT = 40


def _run(args: list[str], *, cwd: Path | None = None) -> str:
    proc = subprocess.run(
        args,
        cwd=str(cwd or ROOT),
        check=True,
        capture_output=True,
        text=True,
        env={**dict(**__import__("os").environ), "TERM": "xterm-256color"},
    )
    return proc.stdout


def _cast(path: Path, title: str, blocks: list[tuple[str, str]]) -> None:
    header = {
        "version": 2,
        "width": WIDTH,
        "height": HEIGHT,
        "timestamp": int(time.time()),
        "title": title,
        "env": {"SHELL": "/bin/bash", "TERM": "xterm-256color"},
    }
    events: list[list[object]] = []
    clock = 0.05
    for command, output in blocks:
        prompt = f"$ {command}\r\n"
        events.append([round(clock, 4), "o", prompt])
        clock += 0.12
        text = output.replace("\n", "\r\n")
        if not text.endswith("\r\n"):
            text += "\r\n"
        events.append([round(clock, 4), "o", text])
        clock += max(0.35, min(8.0, 0.015 * len(text)))
        events.append([round(clock, 4), "o", "\r\n"])
        clock += 0.08
    lines = [json.dumps(header, separators=(",", ":"))]
    lines.extend(json.dumps(event, separators=(",", ":")) for event in events)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> None:
    DEMO.mkdir(parents=True, exist_ok=True)
    extract_classic = _run(
        [sys.executable, "-m", "phenorank.cli", "extract", "--vignette", "data/sample/classic.txt"]
    )
    extract_neg = _run(
        [sys.executable, "-m", "phenorank.cli", "extract", "--vignette", "data/sample/negation.txt"]
    )
    _cast(
        DEMO / "01-extract-polarity.cast",
        "phenorank extract polarity",
        [
            ("phenorank extract --vignette data/sample/classic.txt", extract_classic),
            ("phenorank extract --vignette data/sample/negation.txt", extract_neg),
        ],
    )
    compare = _run(
        [
            sys.executable,
            "-m",
            "phenorank.cli",
            "rank",
            "--vignette",
            "data/sample/negation.txt",
            "--compare-naive",
        ]
    )
    explain = _run(
        [
            sys.executable,
            "-m",
            "phenorank.cli",
            "rank",
            "--vignette",
            "data/sample/classic.txt",
            "--explain",
        ]
    )
    _cast(
        DEMO / "02-negation-comparison.cast",
        "phenorank negation comparison",
        [
            ("phenorank rank --vignette data/sample/classic.txt --explain", explain),
            ("phenorank rank --vignette data/sample/negation.txt --compare-naive", compare),
        ],
    )
    nonspecific = _run(
        [sys.executable, "-m", "phenorank.cli", "rank", "--vignette", "data/sample/nonspecific.txt"]
    )
    unmapped = _run(
        [sys.executable, "-m", "phenorank.cli", "extract", "--vignette", "data/sample/unmapped.txt"]
    )
    eval_out = _run(["make", "eval"], cwd=ROOT)
    _cast(
        DEMO / "03-uncertainty-and-eval.cast",
        "phenorank uncertainty and eval",
        [
            ("phenorank rank --vignette data/sample/nonspecific.txt", nonspecific),
            ("phenorank extract --vignette data/sample/unmapped.txt", unmapped),
            ("make eval", eval_out),
        ],
    )


if __name__ == "__main__":
    main()
