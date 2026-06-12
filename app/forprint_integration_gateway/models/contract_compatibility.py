"""Gateway v0.5 contract compatibility and replay models.

These models are offline/dry-run descriptors only.

They do not:
- execute delivery;
- call external systems;
- create queues;
- write to databases;
- enable live runtime adapters.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class GatewayCompatibilityState(StrEnum):
    """Compatibility result states."""

    COMPATIBLE = "compatible"
    COMPATIBLE_DRY_RUN_ONLY = "compatible_dry_run_only"
    PLANNED_FUTURE = "planned_future"
    BLOCKED_BY_POLICY = "blocked_by_policy"
    BLOCKED_BY_BOUNDARY = "blocked_by_boundary"
    INCOMPATIBLE_CONTRACT_VERSION = "incompatible_contract_version"
    MISSING_REQUIRED_FIELD = "missing_required_field"
    UNSUPPORTED_TARGET_MODULE = "unsupported_target_module"
    FORBIDDEN_LIVE_DELIVERY = "forbidden_live_delivery"


class GatewayReplayFixtureType(StrEnum):
    """Replay fixture type."""

    GOLDEN = "golden"
    NEGATIVE = "negative"


class GatewayReplayExpectedResult(StrEnum):
    """Expected replay result."""

    PASS = "pass"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class GatewayContractVersion:
    """Gateway contract version descriptor."""

    version: str
    min_supported_version: str = "v0.5"
    max_supported_version: str = "v0.5"

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return asdict(self)


@dataclass(frozen=True)
class GatewayContractCompatibilityRule:
    """Compatibility rule between source flow and target contract."""

    source_flow: str
    target_contract: str
    operation: str
    contract_version: str
    compatibility_state: GatewayCompatibilityState
    delivery_mode: str
    runtime_status: str
    live_enabled: bool
    expected_owner_module: str
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        payload = asdict(self)
        payload["compatibility_state"] = self.compatibility_state.value
        return payload


@dataclass(frozen=True)
class GatewayContractCompatibilityResult:
    """Compatibility result."""

    source_flow: str
    target_contract: str
    operation: str
    contract_version: str
    state: GatewayCompatibilityState
    compatible: bool
    live_enabled: bool
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        payload = asdict(self)
        payload["state"] = self.state.value
        return payload


@dataclass(frozen=True)
class GatewayCompatibilityMatrix:
    """Compatibility matrix descriptor."""

    matrix_id: str
    contract_version: str
    rules: list[GatewayContractCompatibilityRule]

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "matrix_id": self.matrix_id,
            "contract_version": self.contract_version,
            "rules": [rule.to_dict() for rule in self.rules],
        }


@dataclass(frozen=True)
class GatewayDryRunDeliveryStep:
    """Dry-run delivery step."""

    step_id: str
    title: str
    status: str
    owner_module: str
    live_enabled: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return asdict(self)


@dataclass(frozen=True)
class GatewayBoundaryViolation:
    """Boundary violation descriptor."""

    code: str
    message: str
    severity: str
    blocked: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return asdict(self)


@dataclass(frozen=True)
class GatewayDryRunDeliveryPlan:
    """Dry-run delivery plan."""

    plan_id: str
    source_module: str
    target_module: str
    operation: str
    contract_version: str
    delivery_mode: str
    runtime_status: str
    live_delivery_enabled: bool
    idempotency_key: str
    correlation_id: str
    compatibility_result: GatewayContractCompatibilityResult
    boundary_flags: list[GatewayBoundaryViolation]
    planned_steps: list[GatewayDryRunDeliveryStep]
    expected_owner_module: str
    error_result: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "plan_id": self.plan_id,
            "source_module": self.source_module,
            "target_module": self.target_module,
            "operation": self.operation,
            "contract_version": self.contract_version,
            "delivery_mode": self.delivery_mode,
            "runtime_status": self.runtime_status,
            "live_delivery_enabled": self.live_delivery_enabled,
            "idempotency_key": self.idempotency_key,
            "correlation_id": self.correlation_id,
            "compatibility_result": self.compatibility_result.to_dict(),
            "boundary_flags": [flag.to_dict() for flag in self.boundary_flags],
            "planned_steps": [step.to_dict() for step in self.planned_steps],
            "expected_owner_module": self.expected_owner_module,
            "error_result": self.error_result,
        }


@dataclass(frozen=True)
class GatewayReplayFixture:
    """Replay fixture descriptor."""

    fixture_id: str
    fixture_type: GatewayReplayFixtureType
    source_flow: str
    target_contract: str
    contract_version: str
    expected_result: GatewayReplayExpectedResult
    expected_state: GatewayCompatibilityState
    payload: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        payload = asdict(self)
        payload["fixture_type"] = self.fixture_type.value
        payload["expected_result"] = self.expected_result.value
        payload["expected_state"] = self.expected_state.value
        return payload


@dataclass(frozen=True)
class GatewayGoldenPathFixture:
    """Golden path fixture descriptor."""

    fixture_id: str
    source_flow: str
    target_contract: str
    expected_state: GatewayCompatibilityState

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        payload = asdict(self)
        payload["expected_state"] = self.expected_state.value
        return payload


@dataclass(frozen=True)
class GatewayReplayResult:
    """Replay result descriptor."""

    fixture_id: str
    fixture_type: GatewayReplayFixtureType
    expected_result: GatewayReplayExpectedResult
    actual_result: GatewayReplayExpectedResult
    compatibility_state: GatewayCompatibilityState
    delivery_plan_status: str
    boundary_status: str
    passed: bool
    delivery_plan: GatewayDryRunDeliveryPlan

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "fixture_id": self.fixture_id,
            "fixture_type": self.fixture_type.value,
            "expected_result": self.expected_result.value,
            "actual_result": self.actual_result.value,
            "compatibility_state": self.compatibility_state.value,
            "delivery_plan_status": self.delivery_plan_status,
            "boundary_status": self.boundary_status,
            "passed": self.passed,
            "delivery_plan": self.delivery_plan.to_dict(),
        }


@dataclass(frozen=True)
class GatewayAdapterReadinessScore:
    """Adapter readiness score descriptor."""

    adapter_id: str
    score: int
    max_score: int
    status: str
    blocking_reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return asdict(self)