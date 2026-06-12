"""Validate Gateway v0.4 adapter contracts and error taxonomy."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT / "app") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "app"))

from forprint_integration_gateway.services.adapter_contracts import (  # noqa: E402
    validate_all_adapter_contracts,
)

ERROR_TAXONOMY_PATH = (
    PROJECT_ROOT / "examples" / "adapter_contracts" / "error_taxonomy_v0_4.json"
)

REQUIRED_ERROR_CATEGORIES = {
    "validation",
    "routing",
    "idempotency",
    "correlation",
    "adapter_availability",
    "forbidden_live_delivery",
    "unsupported_module",
    "boundary_violation",
    "external_runtime_disabled",
    "malformed_envelope",
    "incompatible_contract_version",
}

ALLOWED_RETRY_POLICIES = {
    "no_retry",
    "manual_review",
    "retry_when_runtime_adapter_exists",
    "blocked_until_blueprint_approval",
}


class AdapterReadinessCheckError(RuntimeError):
    """Raised when v0.4 adapter readiness check fails."""


def load_error_taxonomy() -> dict[str, Any]:
    """Load error taxonomy."""
    if not ERROR_TAXONOMY_PATH.exists():
        raise AdapterReadinessCheckError("error taxonomy fixture is missing")

    return json.loads(ERROR_TAXONOMY_PATH.read_text(encoding="utf-8"))


def check_error_taxonomy() -> None:
    """Validate error taxonomy fixture."""
    taxonomy = load_error_taxonomy()

    errors = taxonomy.get("errors")
    if not isinstance(errors, list):
        raise AdapterReadinessCheckError("error taxonomy must contain errors list")

    categories = set()

    for error in errors:
        for field_name in ["code", "category", "severity", "retryable", "message", "metadata"]:
            if field_name not in error:
                raise AdapterReadinessCheckError(
                    f"error taxonomy entry missing {field_name}: {error}"
                )

        categories.add(error["category"])

        if not isinstance(error["retryable"], bool):
            raise AdapterReadinessCheckError(f"retryable must be bool: {error['code']}")

        if not isinstance(error["metadata"], dict):
            raise AdapterReadinessCheckError(f"metadata must be mapping: {error['code']}")

    missing = sorted(REQUIRED_ERROR_CATEGORIES - categories)
    if missing:
        raise AdapterReadinessCheckError(
            "error taxonomy missing categories: " + ", ".join(missing)
        )


def check_retry_policies_are_offline() -> None:
    """Ensure retry policies do not imply runtime queues."""
    errors = validate_all_adapter_contracts()
    if errors:
        raise AdapterReadinessCheckError("; ".join(errors))

    examples_dir = PROJECT_ROOT / "examples" / "adapter_contracts"

    for path in sorted(examples_dir.glob("*.json")):
        if path.name == "error_taxonomy_v0_4.json":
            continue

        payload = json.loads(path.read_text(encoding="utf-8"))
        retry_policy = payload.get("retry_policy")

        if retry_policy not in ALLOWED_RETRY_POLICIES:
            raise AdapterReadinessCheckError(
                f"{path.relative_to(PROJECT_ROOT)} has invalid retry policy"
            )

        if payload.get("restrictions", {}).get("queue_worker_enabled") is True:
            raise AdapterReadinessCheckError(
                f"{path.relative_to(PROJECT_ROOT)} enables queue worker"
            )


def main() -> int:
    """Run adapter contracts check."""
    print("== Gateway v0.4 adapter contracts check ==")
    adapter_errors = validate_all_adapter_contracts()
    if adapter_errors:
        for error in adapter_errors:
            print(f"❌ {error}")
        return 1

    print("✅ Adapter descriptors")
    check_error_taxonomy()
    print("✅ Error taxonomy")
    check_retry_policies_are_offline()
    print("✅ Retry policies are offline descriptors")
    print("✅ Gateway v0.4 adapter contracts are valid.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AdapterReadinessCheckError as exc:
        print(f"❌ Gateway adapter contracts check failed: {exc}")
        raise SystemExit(1) from exc