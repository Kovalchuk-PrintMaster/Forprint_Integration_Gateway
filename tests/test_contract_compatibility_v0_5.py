"""Tests for Gateway v0.5 contract compatibility and replay fixtures."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from forprint_integration_gateway.services.contract_compatibility import (
    load_compatibility_matrix,
    replay_all_fixtures,
    validate_all_contract_compatibility,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_contract_compatibility_fixtures_are_valid() -> None:
    """Compatibility matrix and replay fixtures are valid."""
    assert validate_all_contract_compatibility() == []


def test_required_source_flows_and_targets_exist() -> None:
    """Required source flows and target contracts are represented."""
    matrix = load_compatibility_matrix()
    source_flows = {rule["source_flow"] for rule in matrix["rules"]}
    target_contracts = {rule["target_contract"] for rule in matrix["rules"]}

    assert {
        "telegram_bot.new_order_request",
        "website.price_estimate_request",
        "forprint_crm.client_lookup_request",
        "mobile_app.file_prepress_request",
    }.issubset(source_flows)

    assert {
        "forprint_crm.order_intake",
        "forprint_operational_registry.client_lookup_candidate",
        "forprint_operational_registry.order_handoff_candidate",
        "calculator_engine.quote_preview",
        "forprint_prepress_hub.prepress_job_candidate",
        "forprint_accounting_registry_service.accounting_reference_candidate",
    }.issubset(target_contracts)


def test_replay_fixtures_pass_expected_results() -> None:
    """All replay fixtures produce expected results."""
    results = replay_all_fixtures()
    assert results
    assert all(result.passed for result in results)


def test_negative_paths_are_blocked() -> None:
    """Negative fixtures are blocked as expected."""
    results = {
        result.fixture_id: result
        for result in replay_all_fixtures()
        if result.fixture_type.value == "negative"
    }

    assert results
    assert all(result.actual_result.value == "blocked" for result in results.values())
    assert all(result.boundary_status == "blocked" for result in results.values())


def test_no_replay_plan_enables_live_delivery() -> None:
    """Replay plans never enable live delivery."""
    for result in replay_all_fixtures():
        assert result.delivery_plan.live_delivery_enabled is False


def test_compatibility_matrix_preview_exits_successfully() -> None:
    """Compatibility matrix preview runs successfully."""
    completed = subprocess.run(
        [sys.executable, "scripts/run_compatibility_matrix_preview.py"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "Compatibility matrix preview completed successfully" in completed.stdout


def test_replay_fixtures_preview_exits_successfully() -> None:
    """Replay fixtures preview runs successfully."""
    completed = subprocess.run(
        [sys.executable, "scripts/run_replay_fixtures_preview.py"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "Replay fixtures preview completed successfully" in completed.stdout