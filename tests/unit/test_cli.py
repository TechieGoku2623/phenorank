from __future__ import annotations

from typer.testing import CliRunner

from phenorank.cli import app, repo_root

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
