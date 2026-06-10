"""Offline channel intake contract models for Gateway v0.3.

These models are intentionally local and dataclass-based.

They prepare a contract foundation for Telegram Bot, Website, CRM and future
Mobile App intake without enabling live runtime integrations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


def utc_now_iso() -> str:
    """Return current UTC time as an ISO-8601 string."""
    return datetime.now(UTC).isoformat()


class ChannelSource(StrEnum):
    """Supported channel sources for offline intake fixtures."""

    TELEGRAM_BOT = "telegram_bot"
    WEBSITE = "website"
    FORPRINT_CRM = "forprint_crm"
    MOBILE_APP = "mobile_app"


class BusinessRequestKind(StrEnum):
    """Supported offline business request kinds for v0.3."""

    NEW_ORDER_REQUEST = "new_order_request"
    ORDER_CLARIFICATION = "order_clarification"
    PRICE_ESTIMATE_REQUEST = "price_estimate_request"
    CLIENT_LOOKUP_REQUEST = "client_lookup_request"
    FILE_PREPRESS_REQUEST = "file_prepress_request"
    MANAGER_HANDOFF_REQUEST = "manager_handoff_request"


@dataclass(slots=True)
class ContactHint:
    """Non-authoritative contact hints from a channel request."""

    phone: str | None = None
    email: str | None = None
    username: str | None = None
    display_name: str | None = None


@dataclass(slots=True)
class ClientIdentityHint:
    """Non-authoritative client identity hints from a channel request.

    Gateway does not own client accounts. These values are only hints for
    future CRM / Operational Registry flows.
    """

    external_channel_user_id: str | None = None
    client_ref: str | None = None
    contact_hint: ContactHint = field(default_factory=ContactHint)


@dataclass(slots=True)
class BusinessRequestPayload:
    """Normalized local payload wrapper for the business request."""

    request_kind: str
    summary: str
    details: dict[str, Any] = field(default_factory=dict)
    attachments: list[dict[str, Any]] = field(default_factory=list)


@dataclass(slots=True)
class ChannelIntakeEnvelope:
    """Offline channel intake envelope accepted by Gateway v0.3."""

    intake_id: str
    channel_source: str
    source_channel_request_id: str
    client_identity_hint: ClientIdentityHint
    business_request_payload: BusinessRequestPayload
    raw_channel_values: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    received_at: str = field(default_factory=utc_now_iso)


@dataclass(slots=True)
class GatewayCorrelationContext:
    """Generated correlation context for Gateway processing."""

    correlation_id: str
    intake_id: str
    source_channel_request_id: str
    channel_source: str
    generated_at: str = field(default_factory=utc_now_iso)


@dataclass(slots=True)
class GatewayIdempotencyPolicy:
    """Generated idempotency metadata for offline channel intake."""

    idempotency_key: str
    policy: str = "channel_source:intake_id:source_channel_request_id"
    is_persistent: bool = False
    generated_at: str = field(default_factory=utc_now_iso)


@dataclass(slots=True)
class GatewayValidationIssue:
    """Validation issue for channel intake contracts."""

    code: str
    message: str
    field_path: str
    severity: str = "error"
    is_retryable: bool = False


@dataclass(slots=True)
class NormalizedGatewayRequest:
    """Normalized Gateway request produced from ChannelIntakeEnvelope."""

    intake_id: str
    channel_source: str
    request_kind: str
    summary: str
    client_identity_hint: ClientIdentityHint
    details: dict[str, Any]
    attachments: list[dict[str, Any]]
    raw_channel_values: dict[str, Any]
    correlation_context: GatewayCorrelationContext
    idempotency_policy: GatewayIdempotencyPolicy
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class GatewayRouteDecision:
    """Offline deterministic route decision.

    This is not live delivery. It only tells future adapters where this request
    would be handed off after Gateway validation.
    """

    route_id: str
    target_module: str
    operation: str
    reason: str
    is_live_delivery_enabled: bool = False
    is_future_runtime: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class OperationalRegistryHandoffCandidate:
    """Offline candidate for future Operational Registry handoff.

    Gateway does not write to Operational Registry in v0.3.
    """

    candidate_id: str
    source_intake_id: str
    target_owner_module: str
    request_kind: str
    normalized_summary: str
    client_identity_hint: ClientIdentityHint
    correlation_context: GatewayCorrelationContext
    route_decision: GatewayRouteDecision
    payload_snapshot: dict[str, Any] = field(default_factory=dict)
    is_live_write_enabled: bool = False
    created_at: str = field(default_factory=utc_now_iso)