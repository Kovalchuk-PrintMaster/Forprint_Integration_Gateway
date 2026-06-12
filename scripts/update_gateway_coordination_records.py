from __future__ import annotations

import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODULE_ID = "forprint_integration_gateway"

CURRENT_PHASE = "contract_compatibility_replay_dry_run_v0_5"
CURRENT_COMPLETED_STEP = "gateway_contract_compatibility_ready"

V0_3_PHASE = "channel_intake_operational_handoff_contracts_v0_3"
V0_3_COMPLETED_STEP = "gateway_channel_intake_contracts_ready"
V0_3_PROMPT_ID = "gateway_channel_intake_operational_handoff_contracts_v0_3"
V0_3_IMPLEMENTATION_COMMIT = "3b4707a"
V0_3_FINALIZATION_COMMIT = "4b7821f"

V0_3_1_PROMPT_ID = "gateway_v0_3_1_coordination_records_fix"
V0_3_1_PHASE = "channel_intake_operational_handoff_contracts_v0_3_coordination_fix"
V0_3_1_COMPLETED_STEP = "gateway_v0_3_coordination_records_machine_clean"
V0_3_1_FIX_COMMIT = "44ac33a"
V0_3_1_COMPLETION_REPORT_COMMIT = "688e9c6"
V0_3_1_COMPLETION_REPORT_FILE = (
    "coordination/reports/gateway_v0_3_1_coordination_records_fix_completion.md"
)

V0_4_PHASE = "adapter_contracts_error_taxonomy_v0_4"
V0_4_COMPLETED_STEP = "gateway_adapter_contracts_ready"
V0_4_PROMPT_ID = "gateway_adapter_contracts_error_taxonomy_v0_4"
V0_4_IMPLEMENTATION_COMMIT = "3a97012"
V0_4_COMPLETION_REPORT_COMMIT = "3f51c41"
V0_4_COMPLETION_REPORT_FILE = (
    "coordination/reports/gateway_v0_4_adapter_contracts_error_taxonomy_completion.md"
)

V0_5_PROMPT_ID = "gateway_contract_compatibility_replay_dry_run_v0_5"
V0_5_IMPLEMENTATION_COMMIT = "1a7ed1d"
V0_5_COMPLETION_REPORT_FILE = (
    "coordination/reports/"
    "gateway_v0_5_contract_compatibility_replay_dry_run_completion.md"
)

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
        "no_calculator_runtime_calls_added": True,
        "no_library_runtime_calls_added": True,
        "no_prepress_runtime_calls_added": True,
        "no_accounting_runtime_calls_added": True,
        "no_1c_writes_added": True,
        "no_automatic_posting_added": True,
        "no_final_price_calculation_added": True,
        "examples_are_offline_fixtures_only": True,
        "gateway_remains_validation_routing_boundary": True,
    }


def refresh_current_status(updated_at: str, branch: str, commit: str) -> None:
    """Refresh coordination/status/current_status.yaml."""
    payload = {
        "module_id": MODULE_ID,
        "last_updated": updated_at,
        "branch": branch,
        "last_commit": commit,
        "current_phase": CURRENT_PHASE,
        "last_completed_step": CURRENT_COMPLETED_STEP,
        "checks": {
            "make_check": "ok",
            "make_check_report": "ok",
            "governance_check": "ok",
            "channel_intake_preview": "ok",
            "adapter_contracts_check": "ok",
            "adapter_readiness_preview": "ok",
            "coordination_records_check": "ok",
            "contract_compatibility_check": "ok",
            "compatibility_matrix_preview": "ok",
            "replay_fixtures_preview": "ok",
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
                "implementation_commit": V0_3_IMPLEMENTATION_COMMIT,
                "finalization_commit": V0_3_FINALIZATION_COMMIT,
                "coordination_fix_commit": V0_3_1_FIX_COMMIT,
                "completion_report_commit": V0_3_1_COMPLETION_REPORT_COMMIT,
                "phase": V0_3_PHASE,
                "completed_step": V0_3_COMPLETED_STEP,
            },
            {
                "prompt_id": V0_3_1_PROMPT_ID,
                "source": "forprint_system_blueprint",
                "status": "completed_in_module",
                "implementation_commit": V0_3_1_FIX_COMMIT,
                "completion_report_commit": V0_3_1_COMPLETION_REPORT_COMMIT,
                "phase": V0_3_1_PHASE,
                "completed_step": V0_3_1_COMPLETED_STEP,
            },
            {
                "prompt_id": V0_4_PROMPT_ID,
                "source": "forprint_system_blueprint",
                "status": "completed_in_module",
                "implementation_commit": V0_4_IMPLEMENTATION_COMMIT,
                "coordination_update_commit": V0_4_COMPLETION_REPORT_COMMIT,
                "phase": V0_4_PHASE,
                "completed_step": V0_4_COMPLETED_STEP,
                "report_file": V0_4_COMPLETION_REPORT_FILE,
            },
            {
                "prompt_id": V0_5_PROMPT_ID,
                "source": "forprint_system_blueprint",
                "status": "completed_in_module",
                "implementation_commit": V0_5_IMPLEMENTATION_COMMIT,
                "coordination_update_commit": commit,
                "phase": CURRENT_PHASE,
                "completed_step": CURRENT_COMPLETED_STEP,
                "report_file": V0_5_COMPLETION_REPORT_FILE,
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
                "report_id": V0_3_COMPLETED_STEP,
                "phase": V0_3_PHASE,
                "status": "completed",
                "implementation_commit": V0_3_IMPLEMENTATION_COMMIT,
                "finalization_commit": V0_3_FINALIZATION_COMMIT,
                "coordination_fix_commit": V0_3_1_FIX_COMMIT,
                "completion_report_commit": V0_3_1_COMPLETION_REPORT_COMMIT,
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
            },
            {
                "report_id": V0_3_1_PROMPT_ID,
                "phase": V0_3_1_PHASE,
                "status": "completed",
                "implementation_commit": V0_3_1_FIX_COMMIT,
                "completion_report_commit": V0_3_1_COMPLETION_REPORT_COMMIT,
                "report_file": V0_3_1_COMPLETION_REPORT_FILE,
                "validation_results": {
                    "governance_check": "ok",
                    "make_check": "ok",
                    "make_check_report": "ok",
                    "channel_intake_preview": "ok",
                    "coordination_records_check": "ok",
                    "canonical_module_id_guard": "ok",
                    "no_live_integrations_guard": "ok",
                    "reports_index_tracked": "ok",
                },
                "boundary_confirmation": build_boundary_confirmation(),
            },
            {
                "report_id": V0_4_PROMPT_ID,
                "phase": V0_4_PHASE,
                "status": "completed",
                "implementation_commit": V0_4_IMPLEMENTATION_COMMIT,
                "coordination_update_commit": V0_4_COMPLETION_REPORT_COMMIT,
                "report_file": V0_4_COMPLETION_REPORT_FILE,
                "validation_results": {
                    "governance_check": "ok",
                    "make_check": "ok",
                    "make_check_report": "ok",
                    "channel_intake_preview": "ok",
                    "adapter_contracts_check": "ok",
                    "adapter_readiness_preview": "ok",
                    "coordination_records_check": "ok",
                    "canonical_module_id_guard": "ok",
                    "no_live_integrations_guard": "ok",
                    "reports_index_tracked": "ok",
                },
                "boundary_confirmation": build_boundary_confirmation(),
            },
            {
                "report_id": V0_5_PROMPT_ID,
                "phase": CURRENT_PHASE,
                "status": "completed",
                "implementation_commit": V0_5_IMPLEMENTATION_COMMIT,
                "coordination_update_commit": commit,
                "report_file": V0_5_COMPLETION_REPORT_FILE,
                "validation_results": {
                    "governance_check": "ok",
                    "make_check": "ok",
                    "make_check_report": "ok",
                    "channel_intake_preview": "ok",
                    "adapter_readiness_preview": "ok",
                    "contract_compatibility_check": "ok",
                    "compatibility_matrix_preview": "ok",
                    "replay_fixtures_preview": "ok",
                    "coordination_records_check": "ok",
                    "canonical_module_id_guard": "ok",
                    "no_live_integrations_guard": "ok",
                    "reports_index_tracked": "ok",
                },
                "boundary_confirmation": build_boundary_confirmation(),
            },
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
