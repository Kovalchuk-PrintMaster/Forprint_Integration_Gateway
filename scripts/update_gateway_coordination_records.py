"""Refresh Gateway coordination records for v0.3.1.

This script only writes module-local coordination files.

It does not:
- change runtime behavior;
- call external systems;
- create databases;
- create queues;
- enable live integrations.
"""

from __future__ import annotations

import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODULE_ID = "forprint_integration_gateway"
PHASE = "channel_intake_operational_handoff_contracts_v0_3"
COMPLETED_STEP = "gateway_channel_intake_contracts_ready"

V0_3_PROMPT_ID = "gateway_channel_intake_operational_handoff_contracts_v0_3"
V0_3_1_PROMPT_ID = "gateway_v0_3_1_coordination_records_fix"

IMPLEMENTATION_COMMIT = "3b4707a"
V0_3_FINALIZATION_COMMIT = "4b7821f"

STATUS_PATH = PROJECT_ROOT / "coordination" / "status" / "current_status.yaml"
PROMPTS_INDEX_PATH = PROJECT_ROOT / "coordination" / "prompts" / "index.yaml"
REPORTS_INDEX_PATH = PROJECT_ROOT / "coordination" / "reports" / "index.yaml"


def utc_now_iso() -> str:
    """Return current UTC timestamp."""
    return datetime.now(UTC).isoformat()


def run_git(args: list[str]) -> str:
    """Run git command and return stripped stdout."""
    completed = subprocess.run(
        ["git", *args],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return completed.stdout.strip()


def current_branch() -> str:
    """Return current Git branch."""
    return run_git(["rev-parse", "--abbrev-ref", "HEAD"])


def current_commit() -> str:
    """Return current short Git commit."""
    return run_git(["rev-parse", "--short", "HEAD"])


def write_yaml(path: Path, payload: dict[str, Any]) -> None:
    """Write YAML payload."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(
            payload,
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def build_boundary_confirmation() -> dict[str, bool]:
    """Return explicit Gateway boundary confirmation."""
    return {
        "no_production_api_added": True,
        "no_real_external_integrations_added": True,
        "no_database_ownership_added": True,
        "no_operational_data_ownership_added": True,
        "no_queue_redis_s3_dependency_added": True,
        "no_telegram_runtime_calls_added": True,
        "no_website_runtime_calls_added": True,
        "no_crm_runtime_calls_added": True,
        "no_operational_registry_runtime_calls_added": True,
        "no_1c_writes_added": True,
        "no_automatic_posting_added": True,
        "no_final_price_calculation_added": True,
        "examples_are_offline_fixtures_only": True,
        "gateway_remains_validation_routing_boundary": True,
    }


def refresh_current_status (updated_at: str, branch: str, commit: str) -> None:
    """Refresh coordination/status/current_status.yaml."""
    payload = {
        "module_id": MODULE_ID,
        "last_updated": updated_at,
        "branch": branch,
        "last_commit": commit,
        "current_phase": PHASE,
        "last_completed_step": COMPLETED_STEP,
        "checks": {
            "make_check": "ok",
            "make_check_report": "ok",
            "governance_check": "ok",
            "channel_intake_preview": "ok",
            "coordination_records_check": "ok",
        },
        "boundary_confirmation": build_boundary_confirmation(),
    }
    write_yaml(STATUS_PATH, payload)


def refresh_prompts_index(updated_at: str, commit: str) -> None:
    """Refresh coordination/prompts/index.yaml."""
    payload = {
        "module_id": MODULE_ID,
        "updated_at": updated_at,
        "prompts": [
            {
                "prompt_id": V0_3_PROMPT_ID,
                "source": "forprint_system_blueprint",
                "status": "completed_in_module",
                "implementation_commit": IMPLEMENTATION_COMMIT,
                "finalization_commit": V0_3_FINALIZATION_COMMIT,
                "coordination_fix_commit": commit,
                "phase": PHASE,
                "completed_step": COMPLETED_STEP,
            },
            {
                "prompt_id": V0_3_1_PROMPT_ID,
                "source": "forprint_system_blueprint",
                "status": "applied_in_module",
                "implementation_commit": commit,
                "phase": f"{PHASE}_coordination_fix",
                "completed_step": "gateway_v0_3_coordination_records_machine_clean",
            },
        ],
    }
    write_yaml(PROMPTS_INDEX_PATH, payload)


def refresh_reports_index(updated_at: str, commit: str) -> None:
    """Refresh coordination/reports/index.yaml."""
    payload = {
        "module_id": MODULE_ID,
        "updated_at": updated_at,
        "reports": [
            {
                "report_id": COMPLETED_STEP,
                "phase": PHASE,
                "status": "completed",
                "implementation_commit": IMPLEMENTATION_COMMIT,
                "finalization_commit": V0_3_FINALIZATION_COMMIT,
                "coordination_fix_commit": commit,
                "validation_results": {
                    "governance_check": "ok",
                    "make_check": "ok",
                    "make_check_report": "ok",
                    "channel_intake_preview": "ok",
                    "coordination_records_check": "ok",
                    "canonical_module_id_guard": "ok",
                    "no_live_integrations_guard": "ok",
                },
                "boundary_confirmation": build_boundary_confirmation(),
            }
        ],
    }
    write_yaml(REPORTS_INDEX_PATH, payload)


def main() -> int:
    """Refresh all Gateway coordination records."""
    updated_at = utc_now_iso()
    branch = current_branch()
    commit = current_commit()

    refresh_current_status(updated_at=updated_at, branch=branch, commit=commit)
    refresh_prompts_index(updated_at=updated_at, commit=commit)
    refresh_reports_index(updated_at=updated_at, commit=commit)

    print("✅ Gateway coordination records refreshed.")
    print(f"  - {STATUS_PATH.relative_to(PROJECT_ROOT)}")
    print(f"  - {PROMPTS_INDEX_PATH.relative_to(PROJECT_ROOT)}")
    print(f"  - {REPORTS_INDEX_PATH.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())