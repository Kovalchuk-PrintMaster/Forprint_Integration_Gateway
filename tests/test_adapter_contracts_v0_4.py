"""Tests for Gateway v0.4 adapter contracts."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from forprint_integration_gateway.services.adapter_contracts import (
    load_adapter_contracts,
    validate_all_adapter_contracts,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_adapter_contract_examples_are_valid() -> None:
    """All v0.4 adapter descriptor fixtures are valid."""
    assert validate_all_adapter_contracts() == []


def test_all_required_adapter_descriptors_exist() -> None:
    """Required adapter descriptors exist."""
    contracts = load_adapter_contracts()
    adapter_ids = {contract["adapter_id"] for contract in contracts}

    assert {
        "telegram_bot_to_gateway",
        "website_to_gateway",
        "forprint_crm_to_gateway",
        "mobile_app_to_gateway",
        "gateway_to_crm",
        "gateway_to_operational_registry",
        "gateway_to_calculator_engine",
        "gateway_to_prepress_hub",
        "gateway_to_accounting_registry",
    }.issubset(adapter_ids)


def test_no_adapter_is_live_enabled() -> None:
    """No adapter descriptor enables live delivery."""
    for contract in load_adapter_contracts():
        assert contract["live_enabled"] is False


def test_accounting_registry_adapter_forbids_posting_and_one_c_writes() -> None:
    """Accounting Registry adapter remains blocked from posting and 1C writes."""
    contracts = {
        contract["adapter_id"]: contract
        for contract in load_adapter_contracts()
    }

    accounting = contracts["gateway_to_accounting_registry"]
    assert accounting["live_enabled"] is False
    assert accounting["runtime_status"] == "blocked"
    assert accounting["restrictions"]["automatic_posting_allowed"] is False
    assert accounting["restrictions"]["one_c_write_allowed"] is False


def test_mobile_app_adapter_remains_planned_future() -> None:
    """Mobile App adapter remains planned/future only."""
    contracts = {
        contract["adapter_id"]: contract
        for contract in load_adapter_contracts()
    }

    mobile_app = contracts["mobile_app_to_gateway"]
    assert mobile_app["source_module"] == "mobile_app"
    assert mobile_app["runtime_status"] == "planned"
    assert mobile_app["live_enabled"] is False
    assert mobile_app["metadata"]["planned_future_channel"] is True


def test_error_taxonomy_contains_required_categories() -> None:
    """Error taxonomy contains required categories."""
    taxonomy = json.loads(
        (
            PROJECT_ROOT
            / "examples"
            / "adapter_contracts"
            / "error_taxonomy_v0_4.json"
        ).read_text(encoding="utf-8")
    )

    categories = {error["category"] for error in taxonomy["errors"]}

    assert {
        "validation",
        "routing",
        "idempotency",
        "correlation",
        "adapter_availability",
        "forbidden_live_delivery",
        "unsupported_module",
        "boundary_violation",
        "external_runtime_disabled",
        "malformed_envelope",
        "incompatible_contract_version",
    }.issubset(categories)


def test_adapter_readiness_preview_exits_successfully() -> None:
    """Adapter readiness preview runs successfully."""
    completed = subprocess.run(
        [sys.executable, "scripts/run_adapter_readiness_preview.py"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "Adapter readiness preview completed successfully" in completed.stdout