"""Phase 0 CLI. Ranking commands land in Phase 2."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from phenorank import SAFETY_DISCLAIMER, __version__
from phenorank.config import get_settings
from phenorank.logging import configure_logging
from phenorank.schemas import SampleCase

app = typer.Typer(no_args_is_help=True, add_completion=False)
console = Console(width=140)


def _load_samples() -> list[SampleCase]:
    path = get_settings().sample_dir / "manifest.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [SampleCase.model_validate(item) for item in raw["samples"]]


@app.callback()
def _main() -> None:
    configure_logging()


@app.command("version")
def version() -> None:
    """Print the package version."""

    console.print(f"phenorank {__version__}")


@app.command("demo-plan")
def demo_plan() -> None:
    """Print the five designed vignettes and the path each exercises."""

    samples = _load_samples()
    console.print("[bold]phenorank designed sample vignettes[/bold]\n")
    for sample in samples:
        console.print(f"[bold]{sample.file}[/bold]  {sample.sample_id}")
        console.print(f"  path:     {sample.path_exercised}")
        console.print(f"  expected: {sample.expected_behavior}\n")
    console.print()
    console.print(SAFETY_DISCLAIMER)
    console.print(
        "\n`phenorank rank` is Phase 2. This listing is the dry-run. "
        "Every payload states hypothesis generation, not a diagnosis."
    )
    console.print(f"Sample manifest: {get_settings().sample_dir / 'manifest.json'}")


@app.command("sample-path")
def sample_path() -> None:
    """Print the committed sample directory path."""

    console.print(str(get_settings().sample_dir.resolve()))


def repo_root() -> Path:
    return get_settings().repo_root
