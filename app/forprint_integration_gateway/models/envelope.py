"""Envelope models for ForPrint Integration Gateway.

These models are intentionally simple for v0.1.

They describe the shape of requests and responses moving through the Gateway,
but they do not connect to any real module, API, database or queue yet.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


def utc_now_iso() -> str:
    """Return current UTC time as an ISO-8601 string.

    The Gateway uses this helper for deterministic envelope creation.
    """
    return datetime.now(UTC).isoformat()


@dataclass(slots=True)
class IntegrationRequest:
    """Input envelope accepted by the Gateway.

    The Gateway receives this request from CRM, customer channels or internal
    modules and then validates, normalizes and routes it.

    This class must stay channel-agnostic. Do not add Telegram-only or
    Website-only fields here.
    """

    request_id: str
    correlation_id: str
    idempotency_key: str
    source_module: str
    source_channel: str
    target_module: str
    contract_id: str
    contract_version: str
    operation: str
    payload: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now_iso)


@dataclass(slots=True)
class IntegrationResponse:
    """Output envelope returned by the Gateway.

    This model represents a standardized response shape. In v0.1 it is only a
    local data model and is not exposed through a production API.
    """

    request_id: str
    correlation_id: str
    target_module: str
    status: str
    result_payload: dict[str, Any] = field(default_factory=dict)
    errors: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now_iso)