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
	@echo "=== phenorank extract classic ==="
	$(UV) run phenorank extract --vignette data/sample/classic.txt
	@echo
	@echo "=== phenorank rank classic --explain ==="
	$(UV) run phenorank rank --vignette data/sample/classic.txt --explain
	@echo
	@echo "=== phenorank rank negation --compare-naive ==="
	$(UV) run phenorank rank --vignette data/sample/negation.txt --compare-naive
	@echo
	@echo "=== phenorank rank nonspecific ==="
	$(UV) run phenorank rank --vignette data/sample/nonspecific.txt
	@echo
	@echo "=== phenorank extract unmapped ==="
	$(UV) run phenorank extract --vignette data/sample/unmapped.txt

record:
	$(UV) run python scripts/record_casts.py
