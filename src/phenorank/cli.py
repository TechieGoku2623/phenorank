"""Phase 1–3 CLI: extract, rank, optional POST /rank, demo walkthrough."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from phenorank import SAFETY_DISCLAIMER, __version__
from phenorank.config import get_settings
from phenorank.extract import extract
from phenorank.logging import configure_logging
from phenorank.ontology import load_ontology
from phenorank.rank import rank_text
from phenorank.render import render_compare, render_extract, render_rank
from phenorank.schemas import MeasureName, SampleCase

app = typer.Typer(no_args_is_help=True, add_completion=False)
console = Console(width=100, highlight=False, soft_wrap=True)


def _load_samples() -> list[SampleCase]:
    path = get_settings().sample_dir / "manifest.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [SampleCase.model_validate(item) for item in raw["samples"]]


def _read_vignette(path: Path) -> str:
    if not path.is_file():
        raise typer.BadParameter(f"vignette not found: {path}")
    return path.read_text(encoding="utf-8")


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
        "\nWalkthrough: `phenorank extract --vignette …` then "
        "`phenorank rank --vignette … --explain` / `--compare-naive`. "
        "Every payload states hypothesis generation, not a diagnosis."
    )
    console.print(f"Sample manifest: {get_settings().sample_dir / 'manifest.json'}")


@app.command("sample-path")
def sample_path() -> None:
    """Print the committed sample directory path."""

    console.print(str(get_settings().sample_dir.resolve()))


@app.command("extract")
def extract_cmd(
    vignette: Path = typer.Option(..., "--vignette", help="Path to a free-text vignette."),
) -> None:
    """Map a vignette onto the committed HPO subset with polarity tags."""

    text = _read_vignette(vignette)
    onto = load_ontology()
    result = extract(text, ontology=onto)
    for mention in result.mentions:
        if not onto.has_term(mention.hpo_id):
            raise typer.Exit(code=2)
    print(render_extract(result, onto))


@app.command("rank")
def rank_cmd(
    vignette: Path = typer.Option(..., "--vignette", help="Path to a free-text vignette."),
    explain: bool = typer.Option(False, "--explain", help="Print driving / absent / next test."),
    compare_naive: bool = typer.Option(
        False, "--compare-naive", help="Side-by-side polarity-aware vs naive ranks."
    ),
    measure: MeasureName = typer.Option("phenomizer", "--measure"),
    summary: bool = typer.Option(False, "--summary", help="Top-2 plus next-test line"),
) -> None:
    """Rank designed disease profiles. Hypothesis generation, not a diagnosis."""

    text = _read_vignette(vignette)
    onto = load_ontology()
    aware = rank_text(text, polarity_aware=True, measure=measure, ontology=onto)
    if compare_naive:
        naive = rank_text(text, polarity_aware=False, measure=measure, ontology=onto)
        print(render_compare(aware, naive))
        return
    print(render_rank(aware, explain=explain, limit=2 if summary else 8))


@app.command("eval")
def eval_cmd(
    summary: bool = typer.Option(True, "--summary/--full"),
) -> None:
    """Print accuracy under degraded input from the committed eval table."""

    path = get_settings().repo_root / "docs" / "EVALUATION.md"
    n = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# Evaluation"):
            continue
        print(line[:100])
        if line.strip():
            n += 1
        if n >= 14:
            break


@app.command("serve")
def serve_cmd(
    host: str = typer.Option("127.0.0.1", "--host"),
    port: int = typer.Option(8765, "--port"),
) -> None:
    """Optional research HTTP server. POST /rank. No credentials."""

    from phenorank.api import serve

    serve(host=host, port=port)


@app.command("demo")
def demo() -> None:
    """Full Phase 3 walkthrough on the committed vignettes. No network."""

    sample = get_settings().sample_dir
    steps: list[tuple[str, list[str]]] = [
        ("extract classic (polarity tags)", ["extract", "--vignette", str(sample / "classic.txt")]),
        (
            "rank classic --explain",
            ["rank", "--vignette", str(sample / "classic.txt"), "--explain"],
        ),
        (
            "rank negation --compare-naive",
            ["rank", "--vignette", str(sample / "negation.txt"), "--compare-naive"],
        ),
        (
            "rank nonspecific (insufficient)",
            ["rank", "--vignette", str(sample / "nonspecific.txt")],
        ),
        (
            "extract unmapped (not approximated)",
            ["extract", "--vignette", str(sample / "unmapped.txt")],
        ),
    ]
    console.print("[bold]phenorank demo walkthrough[/bold]")
    console.print(SAFETY_DISCLAIMER)
    console.print()
    for title, args in steps:
        console.print(f"\n=== {title} ===\n")
        console.print(f"$ phenorank {' '.join(args)}\n")
        app(args, standalone_mode=False)
    console.print("\nThen run `make eval` for top-1/5/20, MRR, overlap baseline, noise curve.")
    console.print(SAFETY_DISCLAIMER)


def repo_root() -> Path:
    return get_settings().repo_root


if __name__ == "__main__":
    app()
