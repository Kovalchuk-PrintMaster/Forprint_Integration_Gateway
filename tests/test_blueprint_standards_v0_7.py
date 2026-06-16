"""Tests for Gateway v0.7 Blueprint standards visibility."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from forprint_integration_gateway.services.blueprint_standards import (
    build_standards_snapshot,
    list_blueprint_standards,
    validate_blueprint_standards_visibility,
    validate_standards_snapshot,
    write_standards_snapshot,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_blueprint_standards_index_is_readable() -> None:
    """Blueprint standards index is readable."""
    standards = list_blueprint_standards()
    assert standards


def test_blueprint_standards_visibility_is_advisory() -> None:
    """Standards visibility does not imply full hard enforcement."""
    assert validate_blueprint_standards_visibility() == []


def test_standards_snapshot_can_be_built() -> None:
    """Snapshot can be built with advisory semantics."""
    snapshot = build_standards_snapshot()

    assert snapshot["module_id"] == "forprint_integration_gateway"
    assert snapshot["standards_count"] >= 1
    assert snapshot["advisory_semantics_confirmation"][
        "standards_are_advisory_by_default"
    ] is True
    assert snapshot["advisory_semantics_confirmation"][
        "no_destructive_refactor_from_standards_alone"
    ] is True


def test_standards_snapshot_can_be_written_and_validated() -> None:
    """Snapshot can be written and validated."""
    write_standards_snapshot()
    assert validate_standards_snapshot() == []


def test_blueprint_standards_list_command_runs() -> None:
    """Standards list target script runs."""
    completed = subprocess.run(
        [sys.executable, "scripts/list_blueprint_standards.py"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "Gateway Blueprint standards list" in completed.stdout


def test_blueprint_standards_check_command_runs() -> None:
    """Standards check target script runs."""
    write_standards_snapshot()

    completed = subprocess.run(
        [sys.executable, "scripts/check_blueprint_standards.py"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "Gateway standards visibility is ready" in completed.stdout


def test_blueprint_standards_sync_command_runs() -> None:
    """Standards sync target script runs."""
    completed = subprocess.run(
        [sys.executable, "scripts/sync_blueprint_standards.py"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "standards snapshot refreshed" in completed.stdout


def test_standards_do_not_force_full_compliance() -> None:
    """Gateway treats standards as advisory unless activated."""
    snapshot = build_standards_snapshot()
    confirmation = snapshot["advisory_semantics_confirmation"]

    assert confirmation["standards_are_advisory_by_default"] is True
    assert confirmation["prompts_define_concrete_work_now"] is True
    assert confirmation["directives_are_mandatory_when_explicitly_active"] is True