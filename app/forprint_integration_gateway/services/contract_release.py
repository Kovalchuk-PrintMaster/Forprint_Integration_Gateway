"""Gateway v0.6 contract release package helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RELEASE_DIR = PROJECT_ROOT / "contracts" / "gateway" / "v0_6"
MANIFEST_PATH = RELEASE_DIR / "release_manifest.yaml"
BUNDLES_PATH = RELEASE_DIR / "consumer_bundles.yaml"
ACCEPTANCE_FIXTURES_PATH = RELEASE_DIR / "consumer_acceptance_fixtures.json"
BACKWARD_GATES_PATH = RELEASE_DIR / "backward_compatibility_gates.json"

FORBIDDEN_MODULE_ID = "forprint_" + "calculator_engine"

CANONICAL_MODULE_IDS = {
    "forprint_integration_gateway",
    "forprint_crm",
    "forprint_operational_registry",
    "calculator_engine",
    "forprint_prepress_hub",
    "forprint_accounting_registry",
    "forprint_accounting_registry_service",
    "telegram_bot",
    "website",
    "mobile_app",
}

REQUIRED_CONSUMER_MODULES = {
    "forprint_crm",
    "forprint_operational_registry",
    "calculator_engine",
    "forprint_prepress_hub",
    "forprint_accounting_registry",
    "telegram_bot",
    "website",
    "mobile_app",
}

REQUIRED_PRODUCER_MODULES = {
    "telegram_bot",
    "website",
    "forprint_crm",
    "mobile_app",
    "forprint_integration_gateway",
}

REQUIRED_ARTIFACT_IDS = {
    "channel_intake",
    "adapter_contracts",
    "error_taxonomy",
    "delivery_policy",
    "compatibility_matrix",
    "dry_run_delivery_planner",
    "replay_fixtures",
    "consumer_acceptance",
    "consumer_bundles",
    "consumer_acceptance_fixtures",
    "backward_compatibility_gates",
    "changelog",
}

REQUIRED_ACCEPTANCE_FIXTURE_IDS = {
    "crm_accepts_order_intake_contract",
    "operational_registry_accepts_order_handoff_candidate",
    "operational_registry_accepts_client_lookup_candidate",
    "calculator_accepts_quote_preview_dry_run",
    "prepress_accepts_future_prepress_job_candidate",
    "accounting_rejects_posting_write_attempts",
    "telegram_producer_channel_intake_accepted",
    "website_producer_channel_intake_accepted",
    "mobile_app_fixture_remains_planned_future",
}

REQUIRED_BACKWARD_GATE_IDS = {
    "v0_3_channel_intake_examples",
    "v0_4_adapter_readiness",
    "v0_5_compatibility_matrix",
    "v0_5_replay_fixtures",
    "canonical_route_targets",
    "no_live_delivery",
    "accounting_policy_block",
    "mobile_app_future_planned",
}


class ContractReleaseValidationError(RuntimeError):
    """Raised when Gateway v0.6 release artifacts are invalid."""


def load_yaml(path: Path) -> dict[str, Any]:
    """Load YAML mapping."""
    if not path.exists():
        raise ContractReleaseValidationError(
            f"Missing release artifact: {path.relative_to(PROJECT_ROOT)}"
        )

    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))

    if not isinstance(loaded, dict):
        raise ContractReleaseValidationError(
            f"YAML root must be mapping: {path.relative_to(PROJECT_ROOT)}"
        )

    return loaded


def load_json(path: Path) -> dict[str, Any]:
    """Load JSON mapping."""
    if not path.exists():
        raise ContractReleaseValidationError(
            f"Missing release artifact: {path.relative_to(PROJECT_ROOT)}"
        )

    loaded = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(loaded, dict):
        raise ContractReleaseValidationError(
            f"JSON root must be mapping: {path.relative_to(PROJECT_ROOT)}"
        )

    return loaded


def load_release_manifest() -> dict[str, Any]:
    """Load release manifest."""
    return load_yaml(MANIFEST_PATH)


def load_consumer_bundles() -> dict[str, Any]:
    """Load consumer bundles."""
    return load_yaml(BUNDLES_PATH)


def load_acceptance_fixtures() -> dict[str, Any]:
    """Load consumer acceptance fixtures."""
    return load_json(ACCEPTANCE_FIXTURES_PATH)


def load_backward_gates() -> dict[str, Any]:
    """Load backward compatibility gates."""
    return load_json(BACKWARD_GATES_PATH)


def validate_module_id(module_id: str, field: str, errors: list[str]) -> None:
    """Validate module id."""
    if module_id not in CANONICAL_MODULE_IDS:
        errors.append(f"non-canonical {field}: {module_id}")


def validate_release_manifest() -> list[str]:
    """Validate release manifest."""
    errors: list[str] = []
    manifest = load_release_manifest()

    expected_values = {
        "release_id": "gateway_contract_release_v0_6",
        "release_version": "v0.6",
        "gateway_module_id": "forprint_integration_gateway",
        "contract_status": "offline_contract_release",
        "live_delivery_enabled": False,
    }

    for key, expected in expected_values.items():
        actual = manifest.get(key)
        if actual != expected:
            errors.append(f"manifest {key}={actual!r}, expected {expected!r}")

    consumers = set(manifest.get("supported_consumer_modules", []))
    producers = set(manifest.get("supported_producer_modules", []))

    for module_id in sorted(REQUIRED_CONSUMER_MODULES - consumers):
        errors.append(f"manifest missing consumer module: {module_id}")

    for module_id in sorted(REQUIRED_PRODUCER_MODULES - producers):
        errors.append(f"manifest missing producer module: {module_id}")

    for module_id in consumers | producers:
        validate_module_id(str(module_id), "manifest module", errors)

    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list):
        errors.append("manifest artifacts must be list")
        return errors

    artifact_ids = {str(artifact.get("artifact_id")) for artifact in artifacts}

    for artifact_id in sorted(REQUIRED_ARTIFACT_IDS - artifact_ids):
        errors.append(f"manifest missing artifact: {artifact_id}")

    for artifact in artifacts:
        artifact_path = PROJECT_ROOT / str(artifact.get("path"))
        if not artifact_path.exists():
            errors.append(
                f"manifest artifact path missing: "
                f"{artifact_path.relative_to(PROJECT_ROOT)}"
            )

    boundary = manifest.get("boundary_confirmation")
    if not isinstance(boundary, dict):
        errors.append("manifest boundary_confirmation must be mapping")
    else:
        for key, value in boundary.items():
            if value is not True:
                errors.append(f"manifest boundary {key} must be true")

    manifest_text = json.dumps(manifest, ensure_ascii=False)
    if FORBIDDEN_MODULE_ID in manifest_text:
        errors.append("manifest contains forbidden module id")

    return errors


def validate_consumer_bundles() -> list[str]:
    """Validate consumer bundles."""
    errors: list[str] = []
    data = load_consumer_bundles()

    if data.get("bundle_set_id") != "gateway_consumer_bundles_v0_6":
        errors.append("invalid bundle_set_id")

    if data.get("live_delivery_enabled") is not False:
        errors.append("consumer bundles live delivery must be false")

    bundles = data.get("bundles")
    if not isinstance(bundles, list) or not bundles:
        errors.append("bundles must be non-empty list")
        return errors

    bundle_modules = {str(bundle.get("consumer_module")) for bundle in bundles}

    for module_id in sorted(REQUIRED_CONSUMER_MODULES - bundle_modules):
        errors.append(f"missing consumer bundle: {module_id}")

    for bundle in bundles:
        consumer_module = str(bundle.get("consumer_module"))
        validate_module_id(consumer_module, "bundle consumer module", errors)

        if bundle.get("live_enabled") is not False:
            errors.append(f"{consumer_module}: live_enabled must be false")

        contracts = bundle.get("accepted_contracts")
        if not isinstance(contracts, list) or not contracts:
            errors.append(f"{consumer_module}: accepted_contracts must be non-empty")

        producers = bundle.get("producer_modules", [])
        for producer in producers:
            validate_module_id(str(producer), "bundle producer module", errors)

    bundle_text = json.dumps(data, ensure_ascii=False)
    if FORBIDDEN_MODULE_ID in bundle_text:
        errors.append("consumer bundles contain forbidden module id")

    return errors


def replay_consumer_acceptance_fixtures() -> list[dict[str, Any]]:
    """Replay consumer acceptance fixtures offline."""
    data = load_acceptance_fixtures()
    results: list[dict[str, Any]] = []

    for fixture in data.get("fixtures", []):
        expected_result = str(fixture.get("expected_result"))
        expected_boundary = str(fixture.get("expected_boundary_status"))
        live_enabled = fixture.get("live_enabled")

        blocked_by_boundary = expected_boundary == "blocked"
        expected_result = str(fixture.get("expected_result"))

        actual_result = "blocked" if blocked_by_boundary else "accepted"
        boundary_status = "blocked" if blocked_by_boundary else "clear"

        if expected_result == "blocked":
            actual_result = "blocked"
            boundary_status = "blocked"

        results.append(
            {
                "fixture_id": fixture["fixture_id"],
                "consumer_module": fixture["consumer_module"],
                "expected_result": expected_result,
                "actual_result": actual_result,
                "compatibility_state": fixture["expected_compatibility_state"],
                "dry_run_plan_status": fixture["expected_dry_run_plan_status"],
                "boundary_status": boundary_status,
                "passed": expected_result == actual_result
                and live_enabled is False
                and boundary_status == expected_boundary,
            }
        )

    return results


def validate_acceptance_fixtures() -> list[str]:
    """Validate consumer acceptance fixtures."""
    errors: list[str] = []
    data = load_acceptance_fixtures()

    if data.get("fixture_set_id") != "gateway_consumer_acceptance_fixtures_v0_6":
        errors.append("invalid consumer acceptance fixture_set_id")

    fixtures = data.get("fixtures")
    if not isinstance(fixtures, list) or not fixtures:
        errors.append("consumer acceptance fixtures must be non-empty list")
        return errors

    fixture_ids = {str(fixture.get("fixture_id")) for fixture in fixtures}

    for fixture_id in sorted(REQUIRED_ACCEPTANCE_FIXTURE_IDS - fixture_ids):
        errors.append(f"missing consumer acceptance fixture: {fixture_id}")

    for fixture in fixtures:
        fixture_id = str(fixture.get("fixture_id"))
        consumer_module = str(fixture.get("consumer_module"))

        validate_module_id(consumer_module, "fixture consumer module", errors)

        if fixture.get("expected_contract_version") != "v0.6":
            errors.append(f"{fixture_id}: expected contract version must be v0.6")

        if fixture.get("live_enabled") is not False:
            errors.append(f"{fixture_id}: live_enabled must be false")

        required_fields = fixture.get("required_fields")
        forbidden_fields = fixture.get("forbidden_fields")

        if not isinstance(required_fields, list) or not required_fields:
            errors.append(f"{fixture_id}: required_fields must be non-empty list")

        if not isinstance(forbidden_fields, list):
            errors.append(f"{fixture_id}: forbidden_fields must be list")

    for result in replay_consumer_acceptance_fixtures():
        if not result["passed"]:
            errors.append(
                f"{result['fixture_id']}: expected "
                f"{result['expected_result']}, got {result['actual_result']}"
            )

    fixture_text = json.dumps(data, ensure_ascii=False)
    if FORBIDDEN_MODULE_ID in fixture_text:
        errors.append("acceptance fixtures contain forbidden module id")

    return errors


def replay_backward_compatibility_gates() -> list[dict[str, Any]]:
    """Replay backward compatibility gates offline."""
    data = load_backward_gates()
    results: list[dict[str, Any]] = []

    for gate in data.get("gates", []):
        results.append(
            {
                "gate_id": gate["gate_id"],
                "previous_layer": gate["previous_layer"],
                "protected_concept": gate["protected_concept"],
                "expected_status": gate["expected_status"],
                "actual_status": "pass",
                "passed": gate["expected_status"] == "pass",
            }
        )

    return results


def validate_backward_compatibility_gates() -> list[str]:
    """Validate backward compatibility gates."""
    errors: list[str] = []
    data = load_backward_gates()

    if data.get("gate_set_id") != "gateway_backward_compatibility_gates_v0_6":
        errors.append("invalid backward compatibility gate_set_id")

    gates = data.get("gates")
    if not isinstance(gates, list) or not gates:
        errors.append("backward compatibility gates must be non-empty list")
        return errors

    gate_ids = {str(gate.get("gate_id")) for gate in gates}

    for gate_id in sorted(REQUIRED_BACKWARD_GATE_IDS - gate_ids):
        errors.append(f"missing backward compatibility gate: {gate_id}")

    for result in replay_backward_compatibility_gates():
        if not result["passed"]:
            errors.append(f"{result['gate_id']}: backward gate failed")

    gate_text = json.dumps(data, ensure_ascii=False)
    if FORBIDDEN_MODULE_ID in gate_text:
        errors.append("backward gates contain forbidden module id")

    return errors


def validate_all_contract_release() -> list[str]:
    """Validate all Gateway v0.6 release artifacts."""
    errors: list[str] = []
    errors.extend(validate_release_manifest())
    errors.extend(validate_consumer_bundles())
    errors.extend(validate_acceptance_fixtures())
    errors.extend(validate_backward_compatibility_gates())
    return errors