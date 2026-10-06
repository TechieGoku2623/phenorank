"""Run every Phase 0 harness and regenerate the memo and evaluation tables."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HARNESSES = (
    HERE / "term_extraction" / "probe_set" / "build.py",
    HERE / "term_extraction" / "run.py",
    HERE / "similarity_comparison" / "run.py",
    HERE / "noise_degradation" / "run.py",
    HERE / "render_docs.py",
)


def main() -> None:
    for script in HARNESSES:
        print(f"\n=== {script.relative_to(ROOT)} ===\n")
        subprocess.run([sys.executable, str(script)], check=True, cwd=ROOT)


if __name__ == "__main__":
    main()
