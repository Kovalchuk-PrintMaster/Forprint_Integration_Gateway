"""Validate Gateway v0.3 coordination records."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODULE_ID = "forprint_integration_gateway"
PHASE = "channel_intake_operational_handoff_contracts_v0_3"
COMPLETED_STEP = "gateway_channel_intake_contracts_ready"
V0_3_PROMPT_ID = "gateway_channel_intake_operational_handoff_contracts_v0_3"
IMPLEMENTATION_COMMIT = "3b4707a"

STATUS_PATH = PROJECT_ROOT / "coordination" / "status" / "current_status.yaml"
PROMPTS_INDEX_PATH = PROJECT_ROOT / "coordination" / "prompts" / "index.yaml"
REPORTS_INDEX_PATH = PROJECT_ROOT / "coordination" / "reports" / "index.yaml"

SCAN_DIRS = [
    "app",
    "tests",
    "scripts",
    "examples",
    "docs",
    "coordination",
    "reports",
]

FORBIDDEN_MODULE_ID = "forprint_" + "calculator_engine"

PLACEHOLDER_PATTERNS = [
    "{now}",
    "{branch}",
    "{commit}",
    '"{now}"',
    '"{branch}"',
    '"{commit}"',
]

LIVE_ENABLED_PATTERNS = [
    "live_runtime_enabled" + ": true",
    '"live_runtime_enabled"' + ": true",
    "is_live_delivery_enabled" + ": true",
    '"is_live_delivery_enabled"' + ": true",
    "is_live_write_enabled" + ": true",
    '"is_live_write_enabled"' + ": true",
    "mobile_app_runtime_enabled" + ": true",
    '"mobile_app_runtime_enabled"' + ": true",
]


class CoordinationCheckError(RuntimeError):
    """Raised when coordination records are invalid."""


def load_yaml(path: Path) -> dict[str, Any]:
    """Load YAML file and ensure it is a dictionary."""
    if not path.exists():
        raise CoordinationCheckError(f"Missing YAML file: {path.relative_to(PROJECT_ROOT)}")

    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise CoordinationCheckError(
            f"Invalid YAML: {path.relative_to(PROJECT_ROOT)}: {exc}"
        ) from exc

    if not isinstance(loaded, dict):
        raise CoordinationCheckError(
            f"YAML root must be mapping: {path.relative_to(PROJECT_ROOT)}"
        )

    return loaded


def assert_no_placeholders() -> None:
    """Ensure coordination files do not contain unresolved placeholders."""
    paths = [STATUS_PATH, PROMPTS_INDEX_PATH, REPORTS_INDEX_PATH]

    for path in paths:
        content = path.read_text(encoding="utf-8")

        for pattern in PLACEHOLDER_PATTERNS:
            if pattern in content:
                raise CoordinationCheckError(
                    f"Unresolved placeholder '{pattern}' in {path.relative_to(PROJECT_ROOT)}"
                )

        if re.search(r":\s*pending\s*$", content, flags=re.MULTILINE):
            raise CoordinationCheckError(
                f"Pending status remains in {path.relative_to(PROJECT_ROOT)}"
            )


def assert_current_status() -> None:
    """Validate current_status.yaml."""
    status = load_yaml(STATUS_PATH)

    expected_values = {
        "module_id": MODULE_ID,
        "branch": "main",
        "current_phase": PHASE,
        "last_completed_step": COMPLETED_STEP,
    }

    for key, expected in expected_values.items():
        actual = status.get(key)
        if actual != expected:
            raise CoordinationCheckError(
                f"{STATUS_PATH.relative_to(PROJECT_ROOT)}: {key}={actual!r}, "
                f"expected {expected!r}"
            )

    last_commit = str(status.get("last_commit", ""))
    if not re.fullmatch(r"[0-9a-f]{7,12}", last_commit):
        raise CoordinationCheckError(
            f"last_commit must be real short Git hash, got {last_commit!r}"
        )

    checks = status.get("checks")
    if not isinstance(checks, dict):
        raise CoordinationCheckError("current_status.yaml must contain checks mapping")

    required_checks = {
        "make_check",
        "make_check_report",
        "governance_check",
        "channel_intake_preview",
        "coordination_records_check",
    }

    for check_name in required_checks:
        if checks.get(check_name) != "ok":
            raise CoordinationCheckError(f"Check {check_name} must be ok")


def assert_prompts_index() -> None:
    """Validate coordination/prompts/index.yaml."""
    data = load_yaml(PROMPTS_INDEX_PATH)

    prompts = data.get("prompts")
    if not isinstance(prompts, list):
        raise CoordinationCheckError("coordination/prompts/index.yaml must contain prompts list")

    matching = [
        prompt
        for prompt in prompts
        if isinstance(prompt, dict) and prompt.get("prompt_id") == V0_3_PROMPT_ID
    ]

    if not matching:
        raise CoordinationCheckError(f"Missing prompt record: {V0_3_PROMPT_ID}")

    prompt = matching[0]
    expected_values = {
        "source": "forprint_system_blueprint",
        "status": "completed_in_module",
        "implementation_commit": IMPLEMENTATION_COMMIT,
        "phase": PHASE,
        "completed_step": COMPLETED_STEP,
    }

    for key, expected in expected_values.items():
        actual = prompt.get(key)
        if actual != expected:
            raise CoordinationCheckError(
                f"Prompt {V0_3_PROMPT_ID}: {key}={actual!r}, expected {expected!r}"
            )


def assert_reports_index() -> None:
    """Validate coordination/reports/index.yaml."""
    data = load_yaml(REPORTS_INDEX_PATH)

    if data.get("module_id") != MODULE_ID:
        raise CoordinationCheckError("reports index module_id is invalid")

    reports = data.get("reports")
    if not isinstance(reports, list):
        raise CoordinationCheckError("coordination/reports/index.yaml must contain reports list")

    matching = [
        report
        for report in reports
        if isinstance(report, dict) and report.get("report_id") == COMPLETED_STEP
    ]

    if not matching:
        raise CoordinationCheckError(f"Missing report record: {COMPLETED_STEP}")

    report = matching[0]

    expected_values = {
        "phase": PHASE,
        "status": "completed",
        "implementation_commit": IMPLEMENTATION_COMMIT,
    }

    for key, expected in expected_values.items():
        actual = report.get(key)
        if actual != expected:
            raise CoordinationCheckError(
                f"Report {COMPLETED_STEP}: {key}={actual!r}, expected {expected!r}"
            )

    validation_results = report.get("validation_results")
    if not isinstance(validation_results, dict):
        raise CoordinationCheckError("Report validation_results must be mapping")

    for key, value in validation_results.items():
        if value != "ok":
            raise CoordinationCheckError(f"Report validation result {key} must be ok")

    boundary = report.get("boundary_confirmation")
    if not isinstance(boundary, dict):
        raise CoordinationCheckError("Report boundary_confirmation must be mapping")

    for key, value in boundary.items():
        if value is not True:
            raise CoordinationCheckError(f"Boundary confirmation {key} must be true")


def assert_reports_index_is_tracked() -> None:
    """Ensure coordination/reports/index.yaml is tracked by Git."""
    completed = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "coordination/reports/index.yaml"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    if completed.returncode != 0:
        raise CoordinationCheckError(
            "coordination/reports/index.yaml must be tracked. "
            "Use: git add -f coordination/reports/index.yaml"
        )


def iter_text_files() -> list[Path]:
    """Return text-like files to scan."""
    files: list[Path] = []

    for dirname in SCAN_DIRS:
        root = PROJECT_ROOT / dirname
        if not root.exists():
            continue

        for path in root.rglob("*"):
            if not path.is_file():
                continue

            if ".venv" in path.parts:
                continue

            if path.suffix in {
                ".py",
                ".json",
                ".yaml",
                ".yml",
                ".md",
                ".txt",
                ".toml",
            }:
                files.append(path)

    return files


def assert_no_forbidden_module_ids() -> None:
    """Fail if non-canonical module id remains."""
    offenders: list[str] = []

    for path in iter_text_files():
        content = path.read_text(encoding="utf-8")
        if FORBIDDEN_MODULE_ID in content:
            offenders.append(str(path.relative_to(PROJECT_ROOT)))

    if offenders:
        raise CoordinationCheckError(
            "Non-canonical module id remains: " + ", ".join(sorted(offenders))
        )


def assert_no_live_integrations_enabled() -> None:
    """Fail if live integration flags are enabled in checked files."""
    offenders: list[str] = []

    for path in iter_text_files():
        content = path.read_text(encoding="utf-8")
        for pattern in LIVE_ENABLED_PATTERNS:
            if pattern in content:
                offenders.append(f"{path.relative_to(PROJECT_ROOT)} contains {pattern}")

    if offenders:
        raise CoordinationCheckError(
            "Live integration flag enabled: " + "; ".join(sorted(offenders))
        )


def main() -> int:
    """Run Gateway coordination records check."""
    checks = [
        ("YAML files", lambda: [load_yaml(STATUS_PATH), 
                                load_yaml(PROMPTS_INDEX_PATH), 
                                load_yaml(REPORTS_INDEX_PATH)]),
        ("No placeholders", assert_no_placeholders),
        ("Current status", assert_current_status),
        ("Prompts index", assert_prompts_index),
        ("Reports index", assert_reports_index),
        ("Reports index tracked", assert_reports_index_is_tracked),
        ("Canonical module id guard", assert_no_forbidden_module_ids),
        ("No live integration flags", assert_no_live_integrations_enabled),
    ]

    print("== Gateway coordination records check ==")

    for name, check in checks:
        check()
        print(f"✅ {name}")

    print("✅ Gateway coordination records are machine-clean.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CoordinationCheckError as exc:
        print(f"❌ Gateway coordination records check failed: {exc}")
        raise SystemExit(1) from exc