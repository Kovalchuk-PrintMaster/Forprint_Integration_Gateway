"""Offline channel intake processor for Gateway v0.3.

The processor validates and normalizes local channel intake fixtures.

It does not:
- call Telegram;
- call Website;
- call CRM;
- call Operational Registry;
- write database rows;
- publish queues;
- make business decisions.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from forprint_integration_gateway.models.channel_intake import (
    BusinessRequestKind,
    BusinessRequestPayload,
    ChannelIntakeEnvelope,
    ChannelSource,
    ClientIdentityHint,
    ContactHint,
    GatewayCorrelationContext,
    GatewayIdempotencyPolicy,
    GatewayRouteDecision,
    GatewayValidationIssue,
    NormalizedGatewayRequest,
    OperationalRegistryHandoffCandidate,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CHANNEL_INTAKE_EXAMPLES_DIR = PROJECT_ROOT / "examples" / "channel_intake"

SUPPORTED_CHANNEL_SOURCES = {source.value for source in ChannelSource}
SUPPORTED_REQUEST_KINDS = {kind.value for kind in BusinessRequestKind}

FUTURE_RUNTIME_CHANNELS = {ChannelSource.MOBILE_APP.value}


def load_channel_intake_example(filename: str) -> ChannelIntakeEnvelope:
    """Load a local channel intake example from examples/channel_intake."""
    path = CHANNEL_INTAKE_EXAMPLES_DIR / filename
    payload = json.loads(path.read_text(encoding="utf-8"))

    contact_hint = ContactHint(**payload["client_identity_hint"].get("contact_hint", {}))
    client_identity_hint = ClientIdentityHint(
        external_channel_user_id=payload["client_identity_hint"].get("external_channel_user_id"),
        client_ref=payload["client_identity_hint"].get("client_ref"),
        contact_hint=contact_hint,
    )
    business_payload = BusinessRequestPayload(**payload["business_request_payload"])

    return ChannelIntakeEnvelope(
        intake_id=payload["intake_id"],
        channel_source=payload["channel_source"],
        source_channel_request_id=payload["source_channel_request_id"],
        client_identity_hint=client_identity_hint,
        business_request_payload=business_payload,
        raw_channel_values=payload.get("raw_channel_values", {}),
        metadata=payload.get("metadata", {}),
        received_at=payload.get("received_at"),
    )


class ChannelIntakeProcessor:
    """Local v0.3 channel intake processor."""

    def validate(self, envelope: ChannelIntakeEnvelope) -> list[GatewayValidationIssue]:
        """Validate envelope-level channel intake structure."""
        issues: list[GatewayValidationIssue] = []

        self._require_value(issues, envelope.intake_id, "intake_id")
        self._require_value(issues, envelope.channel_source, "channel_source")
        self._require_value(
            issues,
            envelope.source_channel_request_id,
            "source_channel_request_id",
        )
        self._require_value(
            issues,
            envelope.business_request_payload.request_kind,
            "business_request_payload.request_kind",
        )
        self._require_value(
            issues,
            envelope.business_request_payload.summary,
            "business_request_payload.summary",
        )

        if envelope.channel_source and envelope.channel_source not in SUPPORTED_CHANNEL_SOURCES:
            issues.append(
                GatewayValidationIssue(
                    code="unsupported_channel_source",
                    message=f"Unsupported channel_source: {envelope.channel_source}",
                    field_path="channel_source",
                    severity="error",
                    is_retryable=False,
                )
            )

        request_kind = envelope.business_request_payload.request_kind
        if request_kind and request_kind not in SUPPORTED_REQUEST_KINDS:
            issues.append(
                GatewayValidationIssue(
                    code="unsupported_business_request_kind",
                    message=f"Unsupported request kind: {request_kind}",
                    field_path="business_request_payload.request_kind",
                    severity="error",
                    is_retryable=False,
                )
            )

        contact_hint = envelope.client_identity_hint.contact_hint
        has_contact_hint = any(
            [
                contact_hint.phone,
                contact_hint.email,
                contact_hint.username,
                contact_hint.display_name,
                envelope.client_identity_hint.client_ref,
                envelope.client_identity_hint.external_channel_user_id,
            ]
        )
        if not has_contact_hint:
            issues.append(
                GatewayValidationIssue(
                    code="missing_client_identity_hint",
                    message="At least one client identity/contact hint is required",
                    field_path="client_identity_hint",
                    severity="error",
                    is_retryable=False,
                )
            )

        return issues

    def normalize(self, envelope: ChannelIntakeEnvelope) -> NormalizedGatewayRequest:
        """Create a normalized local Gateway request."""
        correlation_context = self.build_correlation_context(envelope)
        idempotency_policy = self.build_idempotency_policy(envelope)

        return NormalizedGatewayRequest(
            intake_id=envelope.intake_id,
            channel_source=envelope.channel_source,
            request_kind=envelope.business_request_payload.request_kind,
            summary=envelope.business_request_payload.summary.strip(),
            client_identity_hint=envelope.client_identity_hint,
            details=envelope.business_request_payload.details,
            attachments=envelope.business_request_payload.attachments,
            raw_channel_values=envelope.raw_channel_values,
            correlation_context=correlation_context,
            idempotency_policy=idempotency_policy,
            metadata={
                **envelope.metadata,
                "normalized_by": "forprint_integration_gateway",
                "live_runtime_enabled": False,
            },
        )

    def decide_route(self, request: NormalizedGatewayRequest) -> GatewayRouteDecision:
        """Create deterministic offline route decision for normalized request."""
        route_map = {
            BusinessRequestKind.NEW_ORDER_REQUEST.value: (
                "channel_intake_to_crm_new_order",
                "forprint_crm",
                "order.intake.submitted",
                "New order requests require CRM business workflow orchestration.",
            ),
            BusinessRequestKind.ORDER_CLARIFICATION.value: (
                "channel_intake_to_crm_order_clarification",
                "forprint_crm",
                "order.clarification.submitted",
                "Order clarification belongs to CRM workflow coordination.",
            ),
            BusinessRequestKind.PRICE_ESTIMATE_REQUEST.value: (
                "channel_intake_to_calculator_quote_preview",
                "forprint_calculator_engine",
                "quote.preview.requested",
                "Price estimate requests may be routed to Calculator Engine.",
            ),
            BusinessRequestKind.CLIENT_LOOKUP_REQUEST.value: (
                "channel_intake_to_operational_registry_client_lookup_candidate",
                "forprint_operational_registry",
                "client.lookup.requested",
                "Client lookup is an Operational Registry handoff candidate.",
            ),
            BusinessRequestKind.FILE_PREPRESS_REQUEST.value: (
                "channel_intake_to_prepress_job_candidate",
                "forprint_prepress_hub",
                "prepress.job.requested",
                "File/prepress requests may become Prepress Hub handoff candidates.",
            ),
            BusinessRequestKind.MANAGER_HANDOFF_REQUEST.value: (
                "channel_intake_to_crm_manager_handoff",
                "forprint_crm",
                "manager.handoff.requested",
                "Manager handoff requires CRM/human workflow coordination.",
            ),
        }

        route_id, target_module, operation, reason = route_map[request.request_kind]
        is_future_runtime = request.channel_source in FUTURE_RUNTIME_CHANNELS

        return GatewayRouteDecision(
            route_id=route_id,
            target_module=target_module,
            operation=operation,
            reason=reason,
            is_live_delivery_enabled=False,
            is_future_runtime=is_future_runtime,
            metadata={
                "channel_source": request.channel_source,
                "request_kind": request.request_kind,
                "mobile_app_planned_future": is_future_runtime,
            },
        )

    def build_handoff_candidate(
        self,
        request: NormalizedGatewayRequest,
        route_decision: GatewayRouteDecision,
    ) -> OperationalRegistryHandoffCandidate:
        """Create offline Operational Registry handoff candidate."""
        return OperationalRegistryHandoffCandidate(
            candidate_id=f"handoff_candidate:{request.intake_id}",
            source_intake_id=request.intake_id,
            target_owner_module="forprint_operational_registry",
            request_kind=request.request_kind,
            normalized_summary=request.summary,
            client_identity_hint=request.client_identity_hint,
            correlation_context=request.correlation_context,
            route_decision=route_decision,
            payload_snapshot={
                "details": request.details,
                "attachments": request.attachments,
                "route_target_module": route_decision.target_module,
            },
            is_live_write_enabled=False,
        )

    def process(
        self,
        envelope: ChannelIntakeEnvelope,
    ) -> tuple[
        list[GatewayValidationIssue],
        NormalizedGatewayRequest | None,
        GatewayRouteDecision | None,
        OperationalRegistryHandoffCandidate | None,
    ]:
        """Validate, normalize, decide route and prepare handoff candidate."""
        issues = self.validate(envelope)

        if issues:
            return issues, None, None, None

        normalized_request = self.normalize(envelope)
        route_decision = self.decide_route(normalized_request)
        handoff_candidate = self.build_handoff_candidate(
            normalized_request,
            route_decision,
        )

        return issues, normalized_request, route_decision, handoff_candidate

    @staticmethod
    def build_correlation_context(envelope: ChannelIntakeEnvelope) -> GatewayCorrelationContext:
        """Build deterministic correlation context for offline examples."""
        return GatewayCorrelationContext(
            correlation_id=f"corr:{envelope.channel_source}:{envelope.intake_id}",
            intake_id=envelope.intake_id,
            source_channel_request_id=envelope.source_channel_request_id,
            channel_source=envelope.channel_source,
        )

    @staticmethod
    def build_idempotency_policy(envelope: ChannelIntakeEnvelope) -> GatewayIdempotencyPolicy:
        """Build deterministic idempotency key for offline examples."""
        return GatewayIdempotencyPolicy(
            idempotency_key=(
                f"idem:{envelope.channel_source}:"
                f"{envelope.intake_id}:{envelope.source_channel_request_id}"
            )
        )

    @staticmethod
    def _require_value(
        issues: list[GatewayValidationIssue],
        value: Any,
        field_path: str,
    ) -> None:
        """Add missing field issue when value is empty."""
        if value is None or value == "":
            issues.append(
                GatewayValidationIssue(
                    code="missing_required_field",
                    message=f"Required field is missing or empty: {field_path}",
                    field_path=field_path,
                    severity="error",
                    is_retryable=False,
                )
            )


def serialize_channel_intake_result(
    issues: list[GatewayValidationIssue],
    normalized_request: NormalizedGatewayRequest | None,
    route_decision: GatewayRouteDecision | None,
    handoff_candidate: OperationalRegistryHandoffCandidate | None,
) -> dict[str, Any]:
    """Serialize channel intake processing result for scripts/tests."""
    return {
        "issues": [asdict(issue) for issue in issues],
        "normalized_request": asdict(normalized_request) if normalized_request else None,
        "route_decision": asdict(route_decision) if route_decision else None,
        "handoff_candidate": asdict(handoff_candidate) if handoff_candidate else None,
    }