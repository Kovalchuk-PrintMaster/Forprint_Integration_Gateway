"""Local Gateway processing pipeline for ForPrint Integration Gateway.

This processor is deliberately small for v0.1.

It connects existing local services:

1. validate IntegrationRequest envelope;
2. check idempotency_key;
3. match local placeholder route;
4. return IntegrationResponse envelope.

It does not:
- start a production API;
- connect to a database;
- call CRM, Calculator, Accounting or Prepress;
- execute business logic;
- publish messages to queues.
"""

from collections.abc import Mapping
from dataclasses import asdict, fields
from typing import Any

from forprint_integration_gateway.models.envelope import IntegrationRequest, IntegrationResponse
from forprint_integration_gateway.models.errors import ValidationError
from forprint_integration_gateway.services.idempotency import InMemoryIdempotencyService
from forprint_integration_gateway.services.router import RouteNotFoundError, SimpleRouter
from forprint_integration_gateway.services.validator import SimpleValidator


class GatewayProcessor:
    """Small local Gateway pipeline.

    The processor is a composition layer around validator, idempotency service
    and router. It is intentionally not an integration client.
    """

    def __init__(
        self,
        validator: SimpleValidator,
        idempotency_service: InMemoryIdempotencyService,
        router: SimpleRouter,
    ) -> None:
        self.validator = validator
        self.idempotency_service = idempotency_service
        self.router = router

    def process(self, request: IntegrationRequest | Mapping[str, Any]) -> IntegrationResponse:
        """Process local Gateway request and return standardized response."""
        validation_errors = self.validator.validate_request(request)

        if validation_errors:
            return self._validation_failed_response(
                request=request,
                validation_errors=validation_errors,
            )

        integration_request = self._to_integration_request(request)

        idempotency_result = self.idempotency_service.check_and_store(
            idempotency_key=integration_request.idempotency_key,
            request_id=integration_request.request_id,
        )

        if idempotency_result.is_duplicate:
            return IntegrationResponse(
                request_id=integration_request.request_id,
                correlation_id=integration_request.correlation_id,
                target_module=integration_request.target_module,
                status="duplicate_ignored",
                result_payload={
                    "accepted": False,
                    "reason": "duplicate_idempotency_key",
                },
                warnings=[
                    {
                        "code": "duplicate_idempotency_key",
                        "message": "Request has already been processed by idempotency_key",
                        "field_path": "idempotency_key",
                        "severity": "warning",
                        "is_retryable": False,
                    }
                ],
                metadata={
                    "gateway_stage": "idempotency",
                    "idempotency": asdict(idempotency_result),
                },
            )

        try:
            matched_route = self.router.match(integration_request)
        except RouteNotFoundError as exc:
            return IntegrationResponse(
                request_id=integration_request.request_id,
                correlation_id=integration_request.correlation_id,
                target_module=integration_request.target_module,
                status="route_not_found",
                errors=[
                    {
                        "code": "route_not_found",
                        "message": str(exc),
                        "field_path": "routing",
                        "severity": "error",
                        "is_retryable": False,
                    }
                ],
                metadata={
                    "gateway_stage": "routing",
                    "idempotency": asdict(idempotency_result),
                },
            )

        return IntegrationResponse(
            request_id=integration_request.request_id,
            correlation_id=integration_request.correlation_id,
            target_module=integration_request.target_module,
            status="routed",
            result_payload={
                "route_id": matched_route.route_id,
                "target_module": matched_route.target_module,
                "operation": matched_route.operation,
                "contract_id": matched_route.contract_id,
            },
            metadata={
                "gateway_stage": "routing",
                "idempotency": asdict(idempotency_result),
                "route": asdict(matched_route),
            },
        )

    @staticmethod
    def _to_integration_request(
        request: IntegrationRequest | Mapping[str, Any],
    ) -> IntegrationRequest:
        """Convert validated mapping to IntegrationRequest if needed."""
        if isinstance(request, IntegrationRequest):
            return request

        integration_request_fields = {field.name for field in fields(IntegrationRequest)}
        request_kwargs = {
            field_name: request[field_name]
            for field_name in integration_request_fields
            if field_name in request
        }

        return IntegrationRequest(**request_kwargs)

    @staticmethod
    def _validation_failed_response(
        request: IntegrationRequest | Mapping[str, Any],
        validation_errors: list[ValidationError],
    ) -> IntegrationResponse:
        """Build response for validation failure without routing anything."""
        return IntegrationResponse(
            request_id=GatewayProcessor._get_request_value(request, "request_id", "unknown"),
            correlation_id=GatewayProcessor._get_request_value(
                request,
                "correlation_id",
                "unknown",
            ),
            target_module=GatewayProcessor._get_request_value(request, "target_module", "unknown"),
            status="validation_failed",
            errors=[asdict(error) for error in validation_errors],
            metadata={
                "gateway_stage": "validation",
                "routed": False,
            },
        )

    @staticmethod
    def _get_request_value(
        request: IntegrationRequest | Mapping[str, Any],
        field_name: str,
        default: str,
    ) -> str:
        """Read field value from dataclass request or raw mapping."""
        if isinstance(request, Mapping):
            value = request.get(field_name, default)
        else:
            value = getattr(request, field_name, default)

        if value is None or value == "":
            return default

        return str(value)