from __future__ import annotations

from typer.testing import CliRunner

from phenorank import SAFETY_DISCLAIMER
from phenorank.cli import app, repo_root
from phenorank.ontology import load_ontology

runner = CliRunner()


def test_demo_plan_lists_five_designed_paths() -> None:
    result = runner.invoke(app, ["demo-plan"])
    assert result.exit_code == 0, result.stdout
    assert "classic.txt" in result.stdout
    assert "negation.txt" in result.stdout
    assert "nonspecific.txt" in result.stdout
    assert "lay.txt" in result.stdout
    assert "unmapped.txt" in result.stdout
    assert "Hypothesis generation, NOT a diagnosis" in result.stdout


def test_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "phenorank" in result.stdout


def test_sample_path_and_repo_root() -> None:
    result = runner.invoke(app, ["sample-path"])
    assert result.exit_code == 0
    assert "data/sample" in result.stdout
    assert (repo_root() / "pyproject.toml").is_file()


def test_extract_classic_tags_positive_ids() -> None:
    result = runner.invoke(app, ["extract", "--vignette", "data/sample/classic.txt"])
    assert result.exit_code == 0, result.stdout
    assert SAFETY_DISCLAIMER in result.stdout
    assert "HP:0001250" in result.stdout
    assert "positive" in result.stdout
    onto = load_ontology()
    for token in result.stdout.split():
        if token.startswith("HP:"):
            assert onto.has_term(token)


def test_rank_classic_explain() -> None:
    result = runner.invoke(app, ["rank", "--vignette", "data/sample/classic.txt", "--explain"])
    assert result.exit_code == 0, result.stdout
    assert "OMIM:606777" in result.stdout
    assert "driving:" in result.stdout
    assert "expected-but-absent:" in result.stdout
    assert "next test:" in result.stdout
    assert SAFETY_DISCLAIMER in result.stdout
    assert result.stdout.count("NOT a diagnosis") >= 2


def test_rank_negation_compare_naive_different_top1() -> None:
    result = runner.invoke(
        app, ["rank", "--vignette", "data/sample/negation.txt", "--compare-naive"]
    )
    assert result.exit_code == 0, result.stdout
    assert "OMIM:176270" in result.stdout
    assert "top-1 differs:        true" in result.stdout
    assert "naive top-1:" in result.stdout


def test_rank_nonspecific_insufficient() -> None:
    result = runner.invoke(app, ["rank", "--vignette", "data/sample/nonspecific.txt"])
    assert result.exit_code == 0, result.stdout
    assert "insufficient_to_discriminate: True" in result.stdout
    assert "Insufficient" in result.stdout


def test_extract_unmapped_not_approximated() -> None:
    result = runner.invoke(app, ["extract", "--vignette", "data/sample/unmapped.txt"])
    assert result.exit_code == 0, result.stdout
    assert "sparkly toenail" in result.stdout.lower()
    assert "not approximated" in result.stdout
    assert "HP:0000951" not in result.stdout


def test_extract_missing_vignette() -> None:
    result = runner.invoke(app, ["extract", "--vignette", "data/sample/missing.txt"])
    assert result.exit_code != 0


def test_demo_walkthrough() -> None:
    result = runner.invoke(app, ["demo"])
    assert result.exit_code == 0, result.stdout
    assert "OMIM:606777" in result.stdout
    assert "top-1 differs" in result.stdout
    assert "sparkly toenail" in result.stdout.lower()
    assert SAFETY_DISCLAIMER in result.stdout
