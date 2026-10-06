from __future__ import annotations

import os

from phenorank.config import get_settings
from phenorank.logging import configure_logging


def test_settings_point_at_committed_sample_dir() -> None:
    settings = get_settings()
    assert (settings.sample_dir / "classic.txt").is_file()
    assert (settings.sample_dir / "hpo_subset.json").is_file()
    assert (settings.research_dir / "run_all.py").is_file()
    assert settings.pretty_logs is True


def test_configure_logging_dev_and_prod() -> None:
    configure_logging()
    os.environ["PHENORANK_ENV"] = "prod"
    try:
        configure_logging()
    finally:
        os.environ.pop("PHENORANK_ENV", None)
    configure_logging()
