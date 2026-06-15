"""Tests for Gateway v0.6 contract release package."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from forprint_integration_gateway.services.contract_release import (
    load_release_manifest,
    replay_backward_compatibility_gates,
    replay_consumer_acceptance_fixtures,
    validate_all_contract_release,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_contract_release_package_is_valid() -> None:
    """v0.6 release package validates."""
    assert validate_all_contract_release() == []


def test_release_manifest_has_required_consumers() -> None:
    """Release manifest includes required consumers."""
    manifest = load_release_manifest()

    assert {
        "forprint_crm",
        "forprint_operational_registry",
        "calculator_engine",
        "forprint_prepress_hub",
        "forprint_accounting_registry",
        "telegram_bot",
        "website",
        "mobile_app",
    }.issubset(set(manifest["supported_consumer_modules"]))

    assert manifest["live_delivery_enabled"] is False


def test_consumer_acceptance_fixtures_pass() -> None:
    """Consumer acceptance fixtures pass offline."""
    results = replay_consumer_acceptance_fixtures()
    assert results
    assert all(result["passed"] for result in results)


def test_backward_compatibility_gates_pass() -> None:
    """Backward compatibility gates pass offline."""
    results = replay_backward_compatibility_gates()
    assert results
    assert all(result["passed"] for result in results)


def test_contract_release_preview_exits_successfully() -> None:
    """Contract release preview runs successfully."""
    completed = subprocess.run(
        [sys.executable, "scripts/run_contract_release_preview.py"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "Contract release preview completed successfully" in completed.stdout


def test_consumer_acceptance_preview_exits_successfully() -> None:
    """Consumer acceptance preview runs successfully."""
    completed = subprocess.run(
        [sys.executable, "scripts/run_consumer_acceptance_preview.py"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "Consumer acceptance preview completed successfully" in completed.stdout


def test_backward_compatibility_preview_exits_successfully() -> None:
    """Backward compatibility preview runs successfully."""
    completed = subprocess.run(
        [sys.executable, "scripts/run_backward_compatibility_preview.py"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "Backward compatibility preview completed successfully" in completed.stdout