PYTHON=.venv_gateway/bin/python
PIP=.venv_gateway/bin/pip

.PHONY: install test lint format check clean

install:
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"

test:
	$(PYTHON) -m pytest -q

lint:
	$(PYTHON) -m ruff check app tests

format:
	$(PYTHON) -m ruff format app tests

check: lint test

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name "*.egg-info" -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -prune -exec rm -rf {} +