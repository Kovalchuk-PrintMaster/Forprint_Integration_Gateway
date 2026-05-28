"""Local example fixture loader for ForPrint Integration Gateway.

This helper is used only for local examples, tests and smoke scripts.

It does not load canonical contracts.
It does not connect to ForPrint Library.
It does not turn Gateway into a contract source of truth.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from forprint_integration_gateway.models.envelope import IntegrationRequest, IntegrationResponse

PROJECT_ROOT = Path(__file__).resolve().parents[3]
EXAMPLES_DIR = PROJECT_ROOT / "examples"


def load_json_file(path: str | Path) -> dict[str, Any]:
    """Load JSON file as dictionary."""
    file_path = Path(path)

    return json.loads(file_path.read_text(encoding="utf-8"))


def load_yaml_file(path: str | Path) -> dict[str, Any]:
    """Load YAML file as dictionary."""
    file_path = Path(path)

    return yaml.safe_load(file_path.read_text(encoding="utf-8")) or {}


def load_example_request(filename: str) -> IntegrationRequest:
    """Load example request from examples/requests."""
    payload = load_json_file(EXAMPLES_DIR / "requests" / filename)

    return IntegrationRequest(**payload)


def load_example_response(filename: str) -> IntegrationResponse:
    """Load example response from examples/responses."""
    payload = load_json_file(EXAMPLES_DIR / "responses" / filename)

    return IntegrationResponse(**payload)


def load_contract_fixture(filename: str) -> dict[str, Any]:
    """Load documentation-only contract fixture from examples/contracts."""
    return load_yaml_file(EXAMPLES_DIR / "contracts" / filename)