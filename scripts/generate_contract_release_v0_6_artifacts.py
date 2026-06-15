"""Generate Gateway v0.6 offline contract release artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RELEASE_DIR = PROJECT_ROOT / "contracts" / "gateway" / "v0_6"
ARTIFACTS_DIR = RELEASE_DIR / "artifacts"

SUPPORTED_CONSUMERS = [
    "forprint_crm",
    "forprint_operational_registry",
    "calculator_engine",
    "forprint_prepress_hub",
    "forprint_accounting_registry",
    "telegram_bot",
    "website",
    "mobile_app",
]

SUPPORTED_PRODUCERS = [
    "telegram_bot",
    "website",
    "forprint_crm",
    "mobile_app",
    "forprint_integration_gateway",
]

ARTIFACT_IDS = [
    "channel_intake",
    "adapter_contracts",
    "error_taxonomy",
    "delivery_policy",
    "compatibility_matrix",
    "dry_run_delivery_planner",
    "replay_fixtures",
    "consumer_acceptance",
]


def write_yaml(path: Path, payload: dict[str, Any]) -> None:
    """Write YAML file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def write_text(path: Path, content: str) -> None:
    """Write text file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_release_manifest() -> dict[str, Any]:
    """Build release manifest."""
    return {
        "release_id": "gateway_contract_release_v0_6",
        "release_version": "v0.6",
        "gateway_module_id": "forprint_integration_gateway",
        "contract_status": "offline_contract_release",
        "updated_at": "2026-06-12T16:00:59.641525+00:00",
        "live_delivery_enabled": False,
        "source_commits": {
            "v0_4_implementation": "3a97012",
            "v0_4_completion_report": "3f51c41",
            "v0_5_implementation": "1a7ed1d",
            "v0_5_completion_report": "6e8626f",
        },
        "supported_consumer_modules": SUPPORTED_CONSUMERS,
        "supported_producer_modules": SUPPORTED_PRODUCERS,
        "compatibility_baseline": {
            "channel_intake": "v0.3",
            "adapter_contracts": "v0.4",
            "compatibility_matrix": "v0.5",
            "replay_fixtures": "v0.5",
            "contract_release": "v0.6",
        },
        "artifacts": [
            {
                "artifact_id": artifact_id,
                "path": f"contracts/gateway/v0_6/artifacts/{artifact_id}.yaml",
                "machine_readable": True,
                "human_readable": True,
            }
            for artifact_id in ARTIFACT_IDS
        ]
        + [
            {
                "artifact_id": "consumer_bundles",
                "path": "contracts/gateway/v0_6/consumer_bundles.yaml",
                "machine_readable": True,
                "human_readable": True,
            },
            {
                "artifact_id": "consumer_acceptance_fixtures",
                "path": "contracts/gateway/v0_6/consumer_acceptance_fixtures.json",
                "machine_readable": True,
                "human_readable": False,
            },
            {
                "artifact_id": "backward_compatibility_gates",
                "path": "contracts/gateway/v0_6/backward_compatibility_gates.json",
                "machine_readable": True,
                "human_readable": False,
            },
            {
                "artifact_id": "changelog",
                "path": "contracts/gateway/v0_6/changelog.md",
                "machine_readable": False,
                "human_readable": True,
            },
        ],
        "boundary_confirmation": {
            "offline_only": True,
            "dry_run_only": True,
            "contract_only": True,
            "no_live_api": True,
            "no_database": True,
            "no_queues": True,
            "no_redis": True,
            "no_s3": True,
            "no_runtime_adapter_calls": True,
            "no_one_c_writes": True,
            "no_automatic_posting": True,
            "no_final_price_calculation": True,
            "no_generated_production_sdks": True,
        },
    }


def build_consumer_bundles() -> dict[str, Any]:
    """Build consumer bundle descriptors."""
    return {
        "bundle_set_id": "gateway_consumer_bundles_v0_6",
        "release_version": "v0.6",
        "live_delivery_enabled": False,
        "bundles": [
            {
                "bundle_id": "crm_contract_bundle_v0_6",
                "consumer_module": "forprint_crm",
                "purpose": [
                    "order intake from Telegram/Website",
                    "operator-facing workflow handoff",
                    "client lookup requests",
                    "no ownership of all operational truth",
                ],
                "accepted_contracts": ["forprint_crm.order_intake"],
                "producer_modules": ["telegram_bot", "website"],
                "live_enabled": False,
            },
            {
                "bundle_id": "operational_registry_contract_bundle_v0_6",
                "consumer_module": "forprint_operational_registry",
                "purpose": [
                    "client lookup candidates",
                    "order handoff candidates",
                    "operational truth ownership",
                    "dry-run candidate acceptance only",
                ],
                "accepted_contracts": [
                    "forprint_operational_registry.client_lookup_candidate",
                    "forprint_operational_registry.order_handoff_candidate",
                ],
                "producer_modules": ["forprint_crm", "telegram_bot"],
                "live_enabled": False,
            },
            {
                "bundle_id": "calculator_engine_contract_bundle_v0_6",
                "consumer_module": "calculator_engine",
                "purpose": [
                    "quote preview request contracts",
                    "no final price calculation inside Gateway",
                    "calculator remains pricing owner",
                ],
                "accepted_contracts": ["calculator_engine.quote_preview"],
                "producer_modules": ["website"],
                "live_enabled": False,
            },
            {
                "bundle_id": "prepress_hub_contract_bundle_v0_6",
                "consumer_module": "forprint_prepress_hub",
                "purpose": [
                    "file/prepress job candidate contracts",
                    "future Mobile App file request scenario",
                    "no real file transfer",
                ],
                "accepted_contracts": [
                    "forprint_prepress_hub.prepress_job_candidate"
                ],
                "producer_modules": ["mobile_app"],
                "live_enabled": False,
            },
            {
                "bundle_id": "accounting_registry_contract_bundle_v0_6",
                "consumer_module": "forprint_accounting_registry",
                "purpose": [
                    "accounting reference candidate only",
                    "no posting",
                    "no 1C writes",
                    "no automatic accounting mutation",
                ],
                "accepted_contracts": [
                    "forprint_accounting_registry.accounting_reference_candidate"
                ],
                "producer_modules": ["forprint_integration_gateway"],
                "live_enabled": False,
            },
            {
                "bundle_id": "telegram_bot_contract_bundle_v0_6",
                "consumer_module": "telegram_bot",
                "purpose": [
                    "channel intake producer contract",
                    "no live Telegram API call from Gateway",
                ],
                "accepted_contracts": ["telegram_bot.channel_intake_producer"],
                "producer_modules": ["telegram_bot"],
                "live_enabled": False,
            },
            {
                "bundle_id": "website_contract_bundle_v0_6",
                "consumer_module": "website",
                "purpose": [
                    "website form intake producer contract",
                    "no live Website runtime call from Gateway",
                ],
                "accepted_contracts": ["website.channel_intake_producer"],
                "producer_modules": ["website"],
                "live_enabled": False,
            },
            {
                "bundle_id": "mobile_app_contract_bundle_v0_6",
                "consumer_module": "mobile_app",
                "purpose": [
                    "planned/future only",
                    "must remain non-active runtime",
                ],
                "accepted_contracts": ["mobile_app.future_channel_intake_producer"],
                "producer_modules": ["mobile_app"],
                "runtime_status": "planned",
                "live_enabled": False,
            },
        ],
    }


def build_acceptance_fixtures() -> dict[str, Any]:
    """Build consumer acceptance fixtures."""
    return {
        "fixture_set_id": "gateway_consumer_acceptance_fixtures_v0_6",
        "release_version": "v0.6",
        "fixtures": [
            {
                "fixture_id": "crm_accepts_order_intake_contract",
                "consumer_module": "forprint_crm",
                "producer_source_flow": "telegram_bot.new_order_request",
                "expected_contract_version": "v0.6",
                "expected_compatibility_state": "compatible",
                "expected_dry_run_plan_status": "ready",
                "required_fields": ["client_identity_hint", "summary"],
                "forbidden_fields": ["live_delivery_enabled"],
                "live_enabled": False,
                "expected_boundary_status": "clear",
                "expected_result": "accepted",
            },
            {
                "fixture_id": "operational_registry_accepts_order_handoff_candidate",
                "consumer_module": "forprint_operational_registry",
                "producer_source_flow": "telegram_bot.new_order_request",
                "expected_contract_version": "v0.6",
                "expected_compatibility_state": "compatible_dry_run_only",
                "expected_dry_run_plan_status": "ready",
                "required_fields": ["source_intake_id", "target_owner_module"],
                "forbidden_fields": ["live_write_enabled"],
                "live_enabled": False,
                "expected_boundary_status": "clear",
                "expected_result": "accepted",
            },
            {
                "fixture_id": "operational_registry_accepts_client_lookup_candidate",
                "consumer_module": "forprint_operational_registry",
                "producer_source_flow": "forprint_crm.client_lookup_request",
                "expected_contract_version": "v0.6",
                "expected_compatibility_state": "compatible",
                "expected_dry_run_plan_status": "ready",
                "required_fields": ["client_identity_hint", "lookup_reason"],
                "forbidden_fields": ["database_write"],
                "live_enabled": False,
                "expected_boundary_status": "clear",
                "expected_result": "accepted",
            },
            {
                "fixture_id": "calculator_accepts_quote_preview_dry_run",
                "consumer_module": "calculator_engine",
                "producer_source_flow": "website.price_estimate_request",
                "expected_contract_version": "v0.6",
                "expected_compatibility_state": "compatible_dry_run_only",
                "expected_dry_run_plan_status": "ready",
                "required_fields": ["product_hint", "quantity_hint"],
                "forbidden_fields": ["final_price_calculation"],
                "live_enabled": False,
                "expected_boundary_status": "clear",
                "expected_result": "accepted",
            },
            {
                "fixture_id": "prepress_accepts_future_prepress_job_candidate",
                "consumer_module": "forprint_prepress_hub",
                "producer_source_flow": "mobile_app.file_prepress_request",
                "expected_contract_version": "v0.6",
                "expected_compatibility_state": "planned_future",
                "expected_dry_run_plan_status": "ready",
                "required_fields": ["file_ref", "prepress_hint"],
                "forbidden_fields": ["real_file_transfer"],
                "live_enabled": False,
                "expected_boundary_status": "clear",
                "expected_result": "accepted",
            },
            {
                "fixture_id": "accounting_rejects_posting_write_attempts",
                "consumer_module": "forprint_accounting_registry",
                "producer_source_flow": "telegram_bot.new_order_request",
                "expected_contract_version": "v0.6",
                "expected_compatibility_state": "blocked_by_policy",
                "expected_dry_run_plan_status": "blocked",
                "required_fields": ["accounting_reference_candidate"],
                "forbidden_fields": ["automatic_posting", "one_c_write"],
                "live_enabled": False,
                "expected_boundary_status": "blocked",
                "expected_result": "blocked",
            },
            {
                "fixture_id": "telegram_producer_channel_intake_accepted",
                "consumer_module": "telegram_bot",
                "producer_source_flow": "telegram_bot.new_order_request",
                "expected_contract_version": "v0.6",
                "expected_compatibility_state": "compatible",
                "expected_dry_run_plan_status": "ready",
                "required_fields": ["intake_id", "channel_source"],
                "forbidden_fields": ["telegram_runtime_call"],
                "live_enabled": False,
                "expected_boundary_status": "clear",
                "expected_result": "accepted",
            },
            {
                "fixture_id": "website_producer_channel_intake_accepted",
                "consumer_module": "website",
                "producer_source_flow": "website.price_estimate_request",
                "expected_contract_version": "v0.6",
                "expected_compatibility_state": "compatible_dry_run_only",
                "expected_dry_run_plan_status": "ready",
                "required_fields": ["intake_id", "channel_source"],
                "forbidden_fields": ["website_runtime_call"],
                "live_enabled": False,
                "expected_boundary_status": "clear",
                "expected_result": "accepted",
            },
            {
                "fixture_id": "mobile_app_fixture_remains_planned_future",
                "consumer_module": "mobile_app",
                "producer_source_flow": "mobile_app.file_prepress_request",
                "expected_contract_version": "v0.6",
                "expected_compatibility_state": "planned_future",
                "expected_dry_run_plan_status": "ready",
                "required_fields": ["planned_future_channel"],
                "forbidden_fields": ["active_mobile_runtime"],
                "runtime_status": "planned",
                "live_enabled": False,
                "expected_boundary_status": "clear",
                "expected_result": "accepted",
            },
        ],
    }


def build_backward_compatibility_gates() -> dict[str, Any]:
    """Build backward compatibility gates."""
    return {
        "gate_set_id": "gateway_backward_compatibility_gates_v0_6",
        "release_version": "v0.6",
        "gates": [
            {
                "gate_id": "v0_3_channel_intake_examples",
                "previous_layer": "v0.3",
                "protected_concept": "channel intake examples still pass",
                "expected_status": "pass",
            },
            {
                "gate_id": "v0_4_adapter_readiness",
                "previous_layer": "v0.4",
                "protected_concept": "adapter readiness still passes",
                "expected_status": "pass",
            },
            {
                "gate_id": "v0_5_compatibility_matrix",
                "previous_layer": "v0.5",
                "protected_concept": "compatibility matrix still passes",
                "expected_status": "pass",
            },
            {
                "gate_id": "v0_5_replay_fixtures",
                "previous_layer": "v0.5",
                "protected_concept": "replay fixtures still pass",
                "expected_status": "pass",
            },
            {
                "gate_id": "canonical_route_targets",
                "previous_layer": "all",
                "protected_concept": "route target module ids remain canonical",
                "expected_status": "pass",
            },
            {
                "gate_id": "no_live_delivery",
                "previous_layer": "all",
                "protected_concept": "no live delivery is enabled",
                "expected_status": "pass",
            },
            {
                "gate_id": "accounting_policy_block",
                "previous_layer": "all",
                "protected_concept": "Accounting/1C/posting are blocked",
                "expected_status": "pass",
            },
            {
                "gate_id": "mobile_app_future_planned",
                "previous_layer": "all",
                "protected_concept": "Mobile App remains future/planned",
                "expected_status": "pass",
            },
        ],
    }


def build_artifact_payload(artifact_id: str) -> dict[str, Any]:
    """Build generic release artifact payload."""
    return {
        "artifact_id": artifact_id,
        "release_version": "v0.6",
        "gateway_module_id": "forprint_integration_gateway",
        "live_delivery_enabled": False,
        "status": "offline_contract_artifact",
        "description": (
            f"Gateway v0.6 packaged artifact for {artifact_id}. "
            "This is a contract-only offline descriptor."
        ),
        "boundary_confirmation": {
            "offline_only": True,
            "dry_run_only": True,
            "no_runtime_transport": True,
        },
    }


def main() -> int:
    """Generate artifacts."""
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    for artifact_id in ARTIFACT_IDS:
        write_yaml(
            ARTIFACTS_DIR / f"{artifact_id}.yaml",
            build_artifact_payload(artifact_id),
        )

    write_yaml(RELEASE_DIR / "release_manifest.yaml", build_release_manifest())
    write_yaml(RELEASE_DIR / "consumer_bundles.yaml", build_consumer_bundles())
    write_json(
        RELEASE_DIR / "consumer_acceptance_fixtures.json",
        build_acceptance_fixtures(),
    )
    write_json(
        RELEASE_DIR / "backward_compatibility_gates.json",
        build_backward_compatibility_gates(),
    )

    write_text(
        RELEASE_DIR / "changelog.md",
        """# Gateway Contract Release v0.6 Changelog

## v0.3

Introduced offline channel intake and Operational Registry handoff contracts.

## v0.4

Introduced adapter descriptors, delivery policy, runtime status and error taxonomy.

## v0.5

Introduced compatibility matrix, replay fixtures and dry-run delivery planner.

## v0.6

Packages accepted Gateway contracts into a stable offline release package for consumers.

Adds:

- release manifest;
- consumer bundles;
- consumer acceptance fixtures;
- backward compatibility gates;
- deprecation policy documentation;
- release and acceptance previews.

## Known non-live limitations

This release does not include live transport, production SDKs, DB writes, queues,
Redis, S3, runtime adapter calls, 1C writes, automatic posting or final price
calculation.

## Next allowed evolution

Next evolution should be approved by ForPrint System Blueprint.
""",
    )

    print("✅ Gateway v0.6 contract release artifacts generated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())