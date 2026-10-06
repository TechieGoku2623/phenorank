export PATH := $(HOME)/.local/bin:$(PATH)
UV ?= uv

.PHONY: setup lint test research eval demo record

setup:
	$(UV) sync --extra dev

lint:
	$(UV) run ruff check src tests research
	$(UV) run ruff format --check src tests research
	$(UV) run mypy

test:
	$(UV) run pytest

research:
	$(UV) run python research/phase0/run_all.py

eval:
	$(UV) run python research/phase0/term_extraction/run.py
	$(UV) run python research/phase0/similarity_comparison/run.py
	$(UV) run python research/phase0/noise_degradation/run.py
	$(UV) run python research/phase0/render_docs.py

demo:
	$(UV) run phenorank demo-plan

record:
	@echo "Asciinema recordings are a Phase 3 deliverable."
	@echo "Phase 0 has no rank CLI to record."
