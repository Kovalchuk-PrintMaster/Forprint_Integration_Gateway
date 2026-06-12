"""Gateway v0.4 adapter contract and error taxonomy models.

These models describe future adapter readiness only.

They do not:
- enable live delivery;
- call external services;
- create queues;
- create databases;
- perform retries.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class AdapterDirection(StrEnum):
    """Allowed adapter contract directions."""

    INBOUND_CHANNEL_TO_GATEWAY = "inbound_channel_to_gateway"
    GATEWAY_TO_BUSINESS_MODULE = "gateway_to_business_module"
    BUSINESS_MODULE_TO_GATEWAY = "business_module_to_gateway"
    GATEWAY_TO_CHANNEL = "gateway_to_channel"


class AdapterDeliveryMode(StrEnum):
    """Offline-safe delivery modes."""

    OFFLINE_FIXTURE_ONLY = "offline_fixture_only"
    MANUAL_PREVIEW_ONLY = "manual_preview_only"
    DRY_RUN_ONLY = "dry_run_only"
    FUTURE_LIVE_ADAPTER = "future_live_adapter"
    FORBIDDEN = "forbidden"


class AdapterRuntimeStatus(StrEnum):
    """Adapter runtime readiness status."""

    PLANNED = "planned"
    CONTRACT_READY = "contract_ready"
    DRY_RUN_READY = "dry_run_ready"
    BLOCKED = "blocked"
    FORBIDDEN = "forbidden"


class GatewayErrorCategory(StrEnum):
    """Gateway error categories."""

    VALIDATION = "validation"
    ROUTING = "routing"
    IDEMPOTENCY = "idempotency"
    CORRELATION = "correlation"
    ADAPTER_AVAILABILITY = "adapter_availability"
    FORBIDDEN_LIVE_DELIVERY = "forbidden_live_delivery"
    UNSUPPORTED_MODULE = "unsupported_module"
    BOUNDARY_VIOLATION = "boundary_violation"
    EXTERNAL_RUNTIME_DISABLED = "external_runtime_disabled"
    MALFORMED_ENVELOPE = "malformed_envelope"
    INCOMPATIBLE_CONTRACT_VERSION = "incompatible_contract_version"


class GatewayErrorSeverity(StrEnum):
    """Gateway error severity."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class GatewayRetryPolicy(StrEnum):
    """Offline retry policy descriptors."""

    NO_RETRY = "no_retry"
    MANUAL_REVIEW = "manual_review"
    RETRY_WHEN_RUNTIME_ADAPTER_EXISTS = "retry_when_runtime_adapter_exists"
    BLOCKED_UNTIL_BLUEPRINT_APPROVAL = "blocked_until_blueprint_approval"


@dataclass(frozen=True)
class GatewayErrorCode:
    """Structured Gateway error taxonomy entry."""

    code: str
    category: GatewayErrorCategory
    severity: GatewayErrorSeverity
    retryable: bool
    message: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        payload = asdict(self)
        payload["category"] = self.category.value
        payload["severity"] = self.severity.value
        return payload


@dataclass(frozen=True)
class GatewayRetryDecision:
    """Offline retry decision descriptor."""

    policy: GatewayRetryPolicy
    retryable: bool
    reason: str
    requires_queue: bool = False
    requires_runtime_worker: bool = False
    requires_blueprint_approval: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        payload = asdict(self)
        payload["policy"] = self.policy.value
        return payload


@dataclass(frozen=True)
class GatewayDeliveryAttempt:
    """Offline delivery attempt descriptor."""

    attempt_id: str
    adapter_id: str
    delivery_mode: AdapterDeliveryMode
    runtime_status: AdapterRuntimeStatus
    live_enabled: bool = False
    was_executed: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        payload = asdict(self)
        payload["delivery_mode"] = self.delivery_mode.value
        payload["runtime_status"] = self.runtime_status.value
        return payload


@dataclass(frozen=True)
class GatewayDeliveryPlan:
    """Offline delivery plan descriptor."""

    plan_id: str
    adapter_id: str
    delivery_mode: AdapterDeliveryMode
    runtime_status: AdapterRuntimeStatus
    retry_policy: GatewayRetryPolicy
    live_enabled: bool = False
    queue_required: bool = False
    external_runtime_required: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        payload = asdict(self)
        payload["delivery_mode"] = self.delivery_mode.value
        payload["runtime_status"] = self.runtime_status.value
        payload["retry_policy"] = self.retry_policy.value
        return payload


@dataclass(frozen=True)
class GatewayContractCompatibility:
    """Contract compatibility descriptor."""

    contract_version: str
    min_supported_version: str
    max_supported_version: str
    compatible: bool
    compatibility_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return asdict(self)


@dataclass(frozen=True)
class GatewayAdapterReadiness:
    """Adapter readiness descriptor."""

    status: AdapterRuntimeStatus
    live_enabled: bool
    delivery_mode: AdapterDeliveryMode
    blocking_reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        payload = asdict(self)
        payload["status"] = self.status.value
        payload["delivery_mode"] = self.delivery_mode.value
        return payload


@dataclass(frozen=True)
class GatewayAdapterContract:
    """Gateway adapter contract descriptor."""

    adapter_id: str
    adapter_name: str
    direction: AdapterDirection
    source_module: str
    target_module: str
    delivery_mode: AdapterDeliveryMode = AdapterDeliveryMode.OFFLINE_FIXTURE_ONLY
    runtime_status: AdapterRuntimeStatus = AdapterRuntimeStatus.PLANNED
    live_enabled: bool = False
    retry_policy: GatewayRetryPolicy = GatewayRetryPolicy.NO_RETRY
    compatibility: GatewayContractCompatibility | None = None
    restrictions: dict[str, bool] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        payload = asdict(self)
        payload["direction"] = self.direction.value
        payload["delivery_mode"] = self.delivery_mode.value
        payload["runtime_status"] = self.runtime_status.value
        payload["retry_policy"] = self.retry_policy.value

        if self.compatibility is not None:
            payload["compatibility"] = self.compatibility.to_dict()

        return payload