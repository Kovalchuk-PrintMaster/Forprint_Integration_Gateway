"""Gateway v0.5 contract compatibility and replay helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from forprint_integration_gateway.models.contract_compatibility import (
    GatewayBoundaryViolation,
    GatewayCompatibilityState,
    GatewayContractCompatibilityResult,
    GatewayDryRunDeliveryPlan,
    GatewayDryRunDeliveryStep,
    GatewayReplayExpectedResult,
    GatewayReplayFixtureType,
    GatewayReplayResult,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
FIXTURES_DIR = PROJECT_ROOT / "examples" / "contract_compatibility"
MATRIX_PATH = FIXTURES_DIR / "compatibility_matrix_v0_5.json"
REPLAY_FIXTURES_PATH = FIXTURES_DIR / "replay_fixtures_v0_5.json"

CONTRACT_VERSION = "v0.5"
FORBIDDEN_MODULE_ID = "forprint_" + "calculator_engine"

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

REQUIRED_SOURCE_FLOWS = {
    "telegram_bot.new_order_request",
    "website.price_estimate_request",
    "forprint_crm.client_lookup_request",
    "mobile_app.file_prepress_request",
}

REQUIRED_TARGET_CONTRACTS = {
    "forprint_crm.order_intake",
    "forprint_operational_registry.client_lookup_candidate",
    "forprint_operational_registry.order_handoff_candidate",
    "calculator_engine.quote_preview",
    "forprint_prepress_hub.prepress_job_candidate",
    "forprint_accounting_registry_service.accounting_reference_candidate",
}

BLOCKED_STATES = {
    GatewayCompatibilityState.BLOCKED_BY_POLICY.value,
    GatewayCompatibilityState.BLOCKED_BY_BOUNDARY.value,
    GatewayCompatibilityState.INCOMPATIBLE_CONTRACT_VERSION.value,
    GatewayCompatibilityState.MISSING_REQUIRED_FIELD.value,
    GatewayCompatibilityState.UNSUPPORTED_TARGET_MODULE.value,
    GatewayCompatibilityState.FORBIDDEN_LIVE_DELIVERY.value,
}


class ContractCompatibilityValidationError(RuntimeError):
    """Raised when v0.5 compatibility fixtures are invalid."""


def load_json(path: Path) -> dict[str, Any]:
    """Load JSON object."""
    if not path.exists():
        raise ContractCompatibilityValidationError(
            f"Missing fixture: {path.relative_to(PROJECT_ROOT)}"
        )

    text = path.read_text(encoding="utf-8")

    if not text.strip():
        raise ContractCompatibilityValidationError(
            f"Empty fixture: {path.relative_to(PROJECT_ROOT)}"
        )

    return json.loads(text)


def load_compatibility_matrix() -> dict[str, Any]:
    """Load compatibility matrix fixture."""
    return load_json(MATRIX_PATH)


def load_replay_fixtures() -> dict[str, Any]:
    """Load replay fixtures."""
    return load_json(REPLAY_FIXTURES_PATH)


def module_from_contract(contract_id: str) -> str:
    """Return module id from target contract id."""
    return contract_id.split(".", maxsplit=1)[0]


def validate_module_id(module_id: str, field_name: str, errors: list[str]) -> None:
    """Validate canonical module id."""
    if module_id not in CANONICAL_MODULE_IDS:
        errors.append(f"non-canonical {field_name}: {module_id}")


def validate_compatibility_matrix() -> list[str]:
    """Validate compatibility matrix fixture."""
    errors: list[str] = []
    matrix = load_compatibility_matrix()
    rules = matrix.get("rules", [])

    if matrix.get("matrix_id") != "gateway_compatibility_matrix_v0_5":
        errors.append("invalid matrix_id")

    if matrix.get("contract_version") != CONTRACT_VERSION:
        errors.append("invalid matrix contract_version")

    if not isinstance(rules, list) or not rules:
        errors.append("matrix rules must be a non-empty list")
        return errors

    source_flows = set()
    target_contracts = set()

    for rule in rules:
        source_flow = str(rule.get("source_flow"))
        target_contract = str(rule.get("target_contract"))
        source_module = source_flow.split(".", maxsplit=1)[0]
        target_module = module_from_contract(target_contract)

        source_flows.add(source_flow)
        target_contracts.add(target_contract)

        validate_module_id(source_module, "source module", errors)
        validate_module_id(target_module, "target module", errors)

        if rule.get("contract_version") != CONTRACT_VERSION:
            errors.append(f"{source_flow}->{target_contract}: invalid contract version")

        if rule.get("live_enabled") is not False:
            errors.append(f"{source_flow}->{target_contract}: live delivery enabled")

        if rule.get("queue_required") is True:
            errors.append(f"{source_flow}->{target_contract}: queue required")

        if rule.get("db_write_required") is True:
            errors.append(f"{source_flow}->{target_contract}: DB write required")

        if rule.get("external_runtime_required") is True:
            errors.append(f"{source_flow}->{target_contract}: external runtime required")

        text = json.dumps(rule, ensure_ascii=False)
        if FORBIDDEN_MODULE_ID in text:
            errors.append(f"{source_flow}->{target_contract}: forbidden module id remains")

    for source_flow in sorted(REQUIRED_SOURCE_FLOWS - source_flows):
        errors.append(f"missing required source flow: {source_flow}")

    for target_contract in sorted(REQUIRED_TARGET_CONTRACTS - target_contracts):
        errors.append(f"missing required target contract: {target_contract}")

    return errors


def validate_replay_fixtures() -> list[str]:
    """Validate replay fixtures."""
    errors: list[str] = []
    data = load_replay_fixtures()
    fixtures = data.get("fixtures", [])

    if data.get("fixture_set_id") != "gateway_replay_fixtures_v0_5":
        errors.append("invalid fixture_set_id")

    if not isinstance(fixtures, list) or not fixtures:
        errors.append("replay fixtures must be a non-empty list")
        return errors

    fixture_ids = set()

    for fixture in fixtures:
        fixture_id = str(fixture.get("fixture_id"))
        fixture_ids.add(fixture_id)

        source_flow = str(fixture.get("source_flow"))
        target_contract = str(fixture.get("target_contract"))
        source_module = source_flow.split(".", maxsplit=1)[0]
        target_module = module_from_contract(target_contract)

        validate_module_id(source_module, "fixture source module", errors)

        if target_contract != "unknown_module.unsupported_operation":
            validate_module_id(target_module, "fixture target module", errors)

        if fixture.get("contract_version") is None:
            errors.append(f"{fixture_id}: missing contract_version")

        if fixture.get("fixture_type") not in {"golden", "negative"}:
            errors.append(f"{fixture_id}: invalid fixture_type")

        if fixture.get("expected_result") not in {"pass", "blocked"}:
            errors.append(f"{fixture_id}: invalid expected_result")

        if fixture.get("requested_live_delivery") is True:
            expected_state = fixture.get("expected_state")
            if expected_state != GatewayCompatibilityState.FORBIDDEN_LIVE_DELIVERY.value:
                errors.append(f"{fixture_id}: live request must expect forbidden state")

        text = json.dumps(fixture, ensure_ascii=False)
        if FORBIDDEN_MODULE_ID in text:
            errors.append(f"{fixture_id}: forbidden module id remains")

    required_fixture_ids = {
        "golden_telegram_new_order_to_crm",
        "golden_telegram_new_order_to_operational_registry",
        "golden_website_price_estimate_to_calculator",
        "golden_crm_client_lookup_to_operational_registry",
        "golden_mobile_prepress_to_prepress_planned_future",
        "negative_missing_client_identity",
        "negative_unsupported_target_module",
        "negative_live_delivery_requested",
        "negative_wrong_contract_version",
        "negative_accounting_posting_attempt",
        "negative_one_c_write_attempt",
    }

    for fixture_id in sorted(required_fixture_ids - fixture_ids):
        errors.append(f"missing replay fixture: {fixture_id}")

    return errors


def find_matrix_rule(source_flow: str, target_contract: str) -> dict[str, Any] | None:
    """Find compatibility rule."""
    matrix = load_compatibility_matrix()

    for rule in matrix["rules"]:
        if (
            rule.get("source_flow") == source_flow
            and rule.get("target_contract") == target_contract
        ):
            return rule

    return None


def build_error_result(
    state: GatewayCompatibilityState,
    message: str,
) -> dict[str, Any]:
    """Build safe error result."""
    return {
        "state": state.value,
        "message": message,
        "retryable": False,
        "metadata": {
            "offline_only": True,
            "requires_blueprint_review": state
            in {
                GatewayCompatibilityState.BLOCKED_BY_POLICY,
                GatewayCompatibilityState.BLOCKED_BY_BOUNDARY,
                GatewayCompatibilityState.FORBIDDEN_LIVE_DELIVERY,
            },
        },
    }


def derive_compatibility_state(
    fixture: dict[str, Any],
    rule: dict[str, Any] | None,
) -> GatewayCompatibilityState:
    """Derive compatibility state for fixture."""
    if fixture.get("requested_live_delivery") is True:
        return GatewayCompatibilityState.FORBIDDEN_LIVE_DELIVERY

    if fixture.get("contract_version") != CONTRACT_VERSION:
        return GatewayCompatibilityState.INCOMPATIBLE_CONTRACT_VERSION

    if fixture.get("missing_required_field") is True:
        return GatewayCompatibilityState.MISSING_REQUIRED_FIELD

    if fixture.get("target_contract") == "unknown_module.unsupported_operation":
        return GatewayCompatibilityState.UNSUPPORTED_TARGET_MODULE

    if fixture.get("attempts_automatic_posting") is True:
        return GatewayCompatibilityState.BLOCKED_BY_POLICY

    if fixture.get("attempts_one_c_write") is True:
        return GatewayCompatibilityState.BLOCKED_BY_POLICY

    if rule is None:
        return GatewayCompatibilityState.UNSUPPORTED_TARGET_MODULE

    return GatewayCompatibilityState(str(rule["compatibility_state"]))


def build_dry_run_delivery_plan(fixture: dict[str, Any]) -> GatewayDryRunDeliveryPlan:
    """Build dry-run delivery plan without sending anything."""
    source_flow = str(fixture["source_flow"])
    target_contract = str(fixture["target_contract"])
    rule = find_matrix_rule(source_flow, target_contract)
    state = derive_compatibility_state(fixture=fixture, rule=rule)

    source_module = source_flow.split(".", maxsplit=1)[0]
    target_module = module_from_contract(target_contract)
    operation = str(fixture.get("operation") or target_contract.split(".", maxsplit=1)[-1])
    blocked = state.value in BLOCKED_STATES

    delivery_mode = str(
        fixture.get("delivery_mode")
        or (rule or {}).get("delivery_mode")
        or "offline_fixture_only"
    )
    runtime_status = str(
        fixture.get("runtime_status")
        or (rule or {}).get("runtime_status")
        or "planned"
    )
    expected_owner_module = str(
        fixture.get("expected_owner_module")
        or (rule or {}).get("expected_owner_module")
        or target_module
    )

    boundary_flags: list[GatewayBoundaryViolation] = []
    if blocked:
        boundary_flags.append(
            GatewayBoundaryViolation(
                code=f"gateway.compatibility.{state.value}",
                message=f"Dry-run delivery blocked: {state.value}",
                severity="error",
                blocked=True,
                metadata={"fixture_id": fixture["fixture_id"]},
            )
        )

    compatibility_result = GatewayContractCompatibilityResult(
        source_flow=source_flow,
        target_contract=target_contract,
        operation=operation,
        contract_version=str(fixture["contract_version"]),
        state=state,
        compatible=not blocked,
        live_enabled=False,
        notes=[str(note) for note in fixture.get("notes", [])],
    )

    planned_steps = [
        GatewayDryRunDeliveryStep(
            step_id="validate_contract",
            title="Validate source flow and target contract",
            status="ok" if not blocked else "blocked",
            owner_module="forprint_integration_gateway",
        ),
        GatewayDryRunDeliveryStep(
            step_id="prepare_offline_delivery_plan",
            title="Prepare dry-run delivery plan",
            status="ok" if not blocked else "not_executed",
            owner_module="forprint_integration_gateway",
        ),
    ]

    error_result = None
    if blocked:
        error_result = build_error_result(
            state=state,
            message=f"Fixture {fixture['fixture_id']} is blocked as expected.",
        )

    return GatewayDryRunDeliveryPlan(
        plan_id=f"dry_run_plan:{fixture['fixture_id']}",
        source_module=source_module,
        target_module=target_module,
        operation=operation,
        contract_version=str(fixture["contract_version"]),
        delivery_mode=delivery_mode,
        runtime_status=runtime_status,
        live_delivery_enabled=False,
        idempotency_key=f"dryrun:{fixture['fixture_id']}",
        correlation_id=f"corr:dryrun:{fixture['fixture_id']}",
        compatibility_result=compatibility_result,
        boundary_flags=boundary_flags,
        planned_steps=planned_steps,
        expected_owner_module=expected_owner_module,
        error_result=error_result,
    )


def replay_fixture(fixture: dict[str, Any]) -> GatewayReplayResult:
    """Replay a fixture offline."""
    plan = build_dry_run_delivery_plan(fixture)
    expected_result = GatewayReplayExpectedResult(str(fixture["expected_result"]))
    actual_result = (
        GatewayReplayExpectedResult.BLOCKED
        if plan.error_result is not None
        else GatewayReplayExpectedResult.PASS
    )
    fixture_type = GatewayReplayFixtureType(str(fixture["fixture_type"]))
    state = plan.compatibility_result.state
    boundary_status = "blocked" if plan.boundary_flags else "clear"

    return GatewayReplayResult(
        fixture_id=str(fixture["fixture_id"]),
        fixture_type=fixture_type,
        expected_result=expected_result,
        actual_result=actual_result,
        compatibility_state=state,
        delivery_plan_status="blocked" if plan.error_result else "ready",
        boundary_status=boundary_status,
        passed=expected_result == actual_result
        and state.value == fixture["expected_state"],
        delivery_plan=plan,
    )


def replay_all_fixtures() -> list[GatewayReplayResult]:
    """Replay all fixtures offline."""
    data = load_replay_fixtures()
    return [replay_fixture(fixture) for fixture in data["fixtures"]]


def validate_all_contract_compatibility() -> list[str]:
    """Validate matrix and replay fixtures."""
    errors: list[str] = []
    errors.extend(validate_compatibility_matrix())
    errors.extend(validate_replay_fixtures())

    if errors:
        return errors

    replay_results = replay_all_fixtures()
    for result in replay_results:
        if not result.passed:
            errors.append(
                f"{result.fixture_id}: expected {result.expected_result.value}/"
                f"{result.delivery_plan.compatibility_result.state.value}, got "
                f"{result.actual_result.value}/{result.compatibility_state.value}"
            )

        if result.delivery_plan.live_delivery_enabled is not False:
            errors.append(f"{result.fixture_id}: live delivery enabled")

    return errors