"""Gateway v0.4 adapter contract loading and validation helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ADAPTER_EXAMPLES_DIR = PROJECT_ROOT / "examples" / "adapter_contracts"

CANONICAL_MODULE_IDS = {
    "telegram_bot",
    "website",
    "forprint_crm",
    "mobile_app",
    "forprint_integration_gateway",
    "forprint_operational_registry",
    "calculator_engine",
    "forprint_prepress_hub",
    "forprint_accounting_registry_service",
    "forprint_library",
}

ALLOWED_DIRECTIONS = {
    "inbound_channel_to_gateway",
    "gateway_to_business_module",
    "business_module_to_gateway",
    "gateway_to_channel",
}

ALLOWED_DELIVERY_MODES = {
    "offline_fixture_only",
    "manual_preview_only",
    "dry_run_only",
    "future_live_adapter",
    "forbidden",
}

ALLOWED_RUNTIME_STATUSES = {
    "planned",
    "contract_ready",
    "dry_run_ready",
    "blocked",
    "forbidden",
}

ALLOWED_RETRY_POLICIES = {
    "no_retry",
    "manual_review",
    "retry_when_runtime_adapter_exists",
    "blocked_until_blueprint_approval",
}

FORBIDDEN_MODULE_ID = "forprint_" + "calculator_engine"


class AdapterContractValidationError(RuntimeError):
    """Raised when adapter contract descriptor is invalid."""


def load_adapter_contracts(directory: Path = ADAPTER_EXAMPLES_DIR) -> list[dict[str, Any]]:
    """Load adapter contract example descriptors."""
    if not directory.exists():
        raise AdapterContractValidationError(
            f"Adapter examples directory missing: {directory}"
        )

    contracts: list[dict[str, Any]] = []

    for path in sorted(directory.glob("*.json")):
        if path.name == "error_taxonomy_v0_4.json":
            continue

        text = path.read_text(encoding="utf-8")

        if not text.strip():
            raise AdapterContractValidationError(
                f"Empty adapter contract fixture: {path.relative_to(PROJECT_ROOT)}"
            )

        try:
            payload = json.loads(text)
        except json.JSONDecodeError as exc:
            raise AdapterContractValidationError(
                f"Invalid adapter contract JSON: {path.relative_to(PROJECT_ROOT)}: {exc}"
            ) from exc

        payload["_source_file"] = str(path.relative_to(PROJECT_ROOT))
        contracts.append(payload)

    return contracts


def validate_adapter_contract(contract: dict[str, Any]) -> list[str]:
    """Validate a single adapter contract descriptor."""
    errors: list[str] = []
    adapter_id = contract.get("adapter_id")

    required_fields = {
        "adapter_id",
        "adapter_name",
        "direction",
        "source_module",
        "target_module",
        "delivery_mode",
        "runtime_status",
        "live_enabled",
        "retry_policy",
        "contract_version",
    }

    for field_name in sorted(required_fields):
        if field_name not in contract:
            source_file = contract.get("_source_file", "<memory>")
            errors.append(f"{source_file}: missing {field_name}")

    source_module = contract.get("source_module")
    target_module = contract.get("target_module")

    if source_module not in CANONICAL_MODULE_IDS:
        errors.append(
            f"{adapter_id}: non-canonical source_module {source_module!r}"
        )

    if target_module not in CANONICAL_MODULE_IDS:
        errors.append(
            f"{adapter_id}: non-canonical target_module {target_module!r}"
        )

    if contract.get("direction") not in ALLOWED_DIRECTIONS:
        errors.append(f"{adapter_id}: invalid direction")

    if contract.get("delivery_mode") not in ALLOWED_DELIVERY_MODES:
        errors.append(f"{adapter_id}: invalid delivery_mode")

    if contract.get("runtime_status") not in ALLOWED_RUNTIME_STATUSES:
        errors.append(f"{adapter_id}: invalid runtime_status")

    if contract.get("retry_policy") not in ALLOWED_RETRY_POLICIES:
        errors.append(f"{adapter_id}: invalid retry_policy")

    if contract.get("live_enabled") is not False:
        errors.append(f"{adapter_id}: live_enabled must be false")

    text = json.dumps(contract, ensure_ascii=False)
    if FORBIDDEN_MODULE_ID in text:
        errors.append(f"{adapter_id}: forbidden module id remains")

    restrictions = contract.get("restrictions", {})
    if not isinstance(restrictions, dict):
        errors.append(f"{adapter_id}: restrictions must be mapping")
        restrictions = {}

    if restrictions.get("queue_worker_enabled") is True:
        errors.append(f"{adapter_id}: queue workers must not be enabled")

    if restrictions.get("external_runtime_calls_enabled") is True:
        errors.append(
            f"{adapter_id}: external runtime calls must not be enabled"
        )

    if contract.get("target_module") == "forprint_accounting_registry_service":
        if restrictions.get("automatic_posting_allowed") is not False:
            errors.append(
                f"{adapter_id}: accounting automatic posting must be false"
            )

        if restrictions.get("one_c_write_allowed") is not False:
            errors.append(f"{adapter_id}: accounting 1C writes must be false")

    if contract.get("source_module") == "mobile_app":
        if contract.get("runtime_status") != "planned":
            errors.append(f"{adapter_id}: mobile_app must remain planned")

        if contract.get("delivery_mode") not in {
            "offline_fixture_only",
            "future_live_adapter",
        }:
            errors.append(
                f"{adapter_id}: mobile_app delivery mode must remain safe"
            )

    return errors


def validate_all_adapter_contracts() -> list[str]:
    """Validate all adapter descriptors."""
    errors: list[str] = []

    contracts = load_adapter_contracts()

    required_adapter_ids = {
        "telegram_bot_to_gateway",
        "website_to_gateway",
        "forprint_crm_to_gateway",
        "mobile_app_to_gateway",
        "gateway_to_crm",
        "gateway_to_operational_registry",
        "gateway_to_calculator_engine",
        "gateway_to_prepress_hub",
        "gateway_to_accounting_registry",
    }

    actual_ids = {str(contract.get("adapter_id")) for contract in contracts}
    missing_ids = sorted(required_adapter_ids - actual_ids)

    for adapter_id in missing_ids:
        errors.append(f"missing adapter descriptor: {adapter_id}")

    for contract in contracts:
        errors.extend(validate_adapter_contract(contract))

    return errors