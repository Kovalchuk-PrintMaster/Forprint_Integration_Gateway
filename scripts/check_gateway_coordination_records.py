"""Validate Gateway coordination records."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODULE_ID = "forprint_integration_gateway"
CURRENT_PHASE = "adapter_contracts_error_taxonomy_v0_4"
CURRENT_COMPLETED_STEP = "gateway_adapter_contracts_ready"

V0_3_PHASE = "channel_intake_operational_handoff_contracts_v0_3"
V0_3_COMPLETED_STEP = "gateway_channel_intake_contracts_ready"
V0_3_PROMPT_ID = "gateway_channel_intake_operational_handoff_contracts_v0_3"
V0_3_IMPLEMENTATION_COMMIT = "3b4707a"

V0_3_1_REPORT_ID = "gateway_v0_3_1_coordination_records_fix"
V0_3_1_REPORT_FILE = (
    PROJECT_ROOT
    / "coordination"
    / "reports"
    / "gateway_v0_3_1_coordination_records_fix_completion.md"
)

V0_4_PROMPT_ID = "gateway_adapter_contracts_error_taxonomy_v0_4"
V0_4_IMPLEMENTATION_COMMIT = "3a97012"
V0_4_REPORT_FILE = (
    PROJECT_ROOT
    / "coordination"
    / "reports"
    / "gateway_v0_4_adapter_contracts_error_taxonomy_completion.md"
)

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
    "live_enabled" + ": true",
    '"live_enabled"' + ": true",
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
        raise CoordinationCheckError(f"YAML root must be mapping: {path.relative_to(PROJECT_ROOT)}")

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
        "current_phase": CURRENT_PHASE,
        "last_completed_step": CURRENT_COMPLETED_STEP,
    }

    for key, expected in expected_values.items():
        actual = status.get(key)
        if actual != expected:
            raise CoordinationCheckError(
                f"{STATUS_PATH.relative_to(PROJECT_ROOT)}: {key}={actual!r}, expected {expected!r}"
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
        "adapter_contracts_check",
        "adapter_readiness_preview",
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

    prompt_by_id = {
        prompt.get("prompt_id"): prompt for prompt in prompts if isinstance(prompt, dict)
    }

    v0_3 = prompt_by_id.get(V0_3_PROMPT_ID)
    if not isinstance(v0_3, dict):
        raise CoordinationCheckError(f"Missing prompt record: {V0_3_PROMPT_ID}")

    if v0_3.get("implementation_commit") != V0_3_IMPLEMENTATION_COMMIT:
        raise CoordinationCheckError(f"Prompt {V0_3_PROMPT_ID} implementation commit invalid")

    v0_4 = prompt_by_id.get(V0_4_PROMPT_ID)
    if not isinstance(v0_4, dict):
        raise CoordinationCheckError(f"Missing prompt record: {V0_4_PROMPT_ID}")

    expected_values = {
        "source": "forprint_system_blueprint",
        "status": "completed_in_module",
        "implementation_commit": V0_4_IMPLEMENTATION_COMMIT,
        "phase": CURRENT_PHASE,
        "completed_step": CURRENT_COMPLETED_STEP,
        "report_file": str(V0_4_REPORT_FILE.relative_to(PROJECT_ROOT)),
    }

    for key, expected in expected_values.items():
        actual = v0_4.get(key)
        if actual != expected:
            raise CoordinationCheckError(
                f"Prompt {V0_4_PROMPT_ID}: {key}={actual!r}, expected {expected!r}"
            )


def assert_reports_index() -> None:
    """Validate coordination/reports/index.yaml."""
    data = load_yaml(REPORTS_INDEX_PATH)

    if data.get("module_id") != MODULE_ID:
        raise CoordinationCheckError("reports index module_id is invalid")

    reports = data.get("reports")
    if not isinstance(reports, list):
        raise CoordinationCheckError("coordination/reports/index.yaml must contain reports list")

    report_by_id = {
        report.get("report_id"): report for report in reports if isinstance(report, dict)
    }

    v0_3 = report_by_id.get(V0_3_COMPLETED_STEP)
    if not isinstance(v0_3, dict):
        raise CoordinationCheckError(f"Missing report record: {V0_3_COMPLETED_STEP}")

    if v0_3.get("phase") != V0_3_PHASE:
        raise CoordinationCheckError(f"Report {V0_3_COMPLETED_STEP} phase invalid")

    v0_3_1 = report_by_id.get(V0_3_1_REPORT_ID)
    if not isinstance(v0_3_1, dict):
        raise CoordinationCheckError(f"Missing report record: {V0_3_1_REPORT_ID}")

    if v0_3_1.get("status") != "completed":
        raise CoordinationCheckError(f"Report {V0_3_1_REPORT_ID} must be completed")

    if v0_3_1.get("report_file") != str(V0_3_1_REPORT_FILE.relative_to(PROJECT_ROOT)):
        raise CoordinationCheckError(f"Report {V0_3_1_REPORT_ID} must reference completion file")

    v0_4 = report_by_id.get(V0_4_PROMPT_ID)
    if not isinstance(v0_4, dict):
        raise CoordinationCheckError(f"Missing report record: {V0_4_PROMPT_ID}")

    expected_values = {
        "phase": CURRENT_PHASE,
        "status": "completed",
        "implementation_commit": V0_4_IMPLEMENTATION_COMMIT,
        "report_file": str(V0_4_REPORT_FILE.relative_to(PROJECT_ROOT)),
    }

    for key, expected in expected_values.items():
        actual = v0_4.get(key)
        if actual != expected:
            raise CoordinationCheckError(
                f"Report {V0_4_PROMPT_ID}: {key}={actual!r}, expected {expected!r}"
            )

    validation_results = v0_4.get("validation_results")
    if not isinstance(validation_results, dict):
        raise CoordinationCheckError("v0.4 report validation_results must be mapping")

    for key, value in validation_results.items():
        if value != "ok":
            raise CoordinationCheckError(f"v0.4 validation result {key} must be ok")

    boundary = v0_4.get("boundary_confirmation")
    if not isinstance(boundary, dict):
        raise CoordinationCheckError("v0.4 boundary_confirmation must be mapping")

    for key, value in boundary.items():
        if value is not True:
            raise CoordinationCheckError(f"Boundary confirmation {key} must be true")


def assert_tracked(path: Path, label: str) -> None:
    """Ensure path is tracked by Git."""
    relative_path = str(path.relative_to(PROJECT_ROOT))
    completed = subprocess.run(
        ["git", "ls-files", "--error-unmatch", relative_path],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    if completed.returncode != 0:
        raise CoordinationCheckError(f"{label} must be tracked. Use: git add -f {relative_path}")


def assert_reports_are_tracked() -> None:
    """Ensure report files are tracked."""
    assert_tracked(REPORTS_INDEX_PATH, "coordination/reports/index.yaml")
    assert_tracked(V0_3_1_REPORT_FILE, "v0.3.1 completion report")
    assert_tracked(V0_4_REPORT_FILE, "v0.4 completion report")


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
            if path.relative_to(PROJECT_ROOT).as_posix() in {
                "reports/gateway_check_report.json",
                "reports/gateway_check_report.md",
                "reports/gateway_module_status.json",
            }:
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
        (
            "YAML files",
            lambda: [
                load_yaml(STATUS_PATH),
                load_yaml(PROMPTS_INDEX_PATH),
                load_yaml(REPORTS_INDEX_PATH),
            ],
        ),
        ("No placeholders", assert_no_placeholders),
        ("Current status", assert_current_status),
        ("Prompts index", assert_prompts_index),
        ("Reports index", assert_reports_index),
        ("Reports tracked", assert_reports_are_tracked),
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
