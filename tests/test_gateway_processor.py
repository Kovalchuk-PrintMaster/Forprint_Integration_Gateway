from forprint_integration_gateway.models.envelope import IntegrationRequest
from forprint_integration_gateway.models.routing import RoutingRule
from forprint_integration_gateway.services.gateway_processor import GatewayProcessor
from forprint_integration_gateway.services.idempotency import InMemoryIdempotencyService
from forprint_integration_gateway.services.router import SimpleRouter
from forprint_integration_gateway.services.validator import SimpleValidator


def make_request(
    *,
    request_id: str = "req_001",
    idempotency_key: str = "idem_001",
    target_module: str = "forprint_calculator_engine",
    contract_id: str = "calculator.quote_request.v1",
    operation: str = "quote.preview.requested",
) -> IntegrationRequest:
    return IntegrationRequest(
        request_id=request_id,
        correlation_id="corr_001",
        idempotency_key=idempotency_key,
        source_module="customer_channel",
        source_channel="website",
        target_module=target_module,
        contract_id=contract_id,
        contract_version="v1",
        operation=operation,
        payload={"product": "business_card"},
        metadata={"customer_channel": "website"},
    )


def make_processor_with_quote_route() -> GatewayProcessor:
    route = RoutingRule(
        route_id="customer_channel_to_calculator_quote_preview",
        source_module="customer_channel",
        target_module="forprint_calculator_engine",
        contract_id="calculator.quote_request.v1",
        operation="quote.preview.requested",
        enabled=True,
        priority=100,
    )

    return GatewayProcessor(
        validator=SimpleValidator(),
        idempotency_service=InMemoryIdempotencyService(),
        router=SimpleRouter(routes=[route]),
    )


def test_gateway_processor_routes_valid_request() -> None:
    processor = make_processor_with_quote_route()

    response = processor.process(make_request())

    assert response.status == "routed"
    assert response.request_id == "req_001"
    assert response.correlation_id == "corr_001"
    assert response.target_module == "forprint_calculator_engine"
    assert response.result_payload["route_id"] == "customer_channel_to_calculator_quote_preview"
    assert response.metadata["gateway_stage"] == "routing"
    assert response.metadata["idempotency"]["is_duplicate"] is False


def test_gateway_processor_returns_validation_failed_response() -> None:
    processor = make_processor_with_quote_route()

    raw_request = {
        "request_id": "req_001",
        "correlation_id": "corr_001",
        # idempotency_key is intentionally missing.
        "source_module": "customer_channel",
        "source_channel": "website",
        "target_module": "forprint_calculator_engine",
        "contract_id": "calculator.quote_request.v1",
        "contract_version": "v1",
        "operation": "quote.preview.requested",
        "payload": {},
        "metadata": {},
        "created_at": "2026-05-26T00:00:00+00:00",
    }

    response = processor.process(raw_request)

    assert response.status == "validation_failed"
    assert response.result_payload == {}
    assert response.errors
    assert response.errors[0]["code"] == "missing_required_field"
    assert response.errors[0]["field_path"] == "idempotency_key"
    assert response.metadata["gateway_stage"] == "validation"
    assert response.metadata["routed"] is False


def test_gateway_processor_ignores_duplicate_idempotency_key() -> None:
    processor = make_processor_with_quote_route()

    first_response = processor.process(
        make_request(
            request_id="req_001",
            idempotency_key="idem_001",
        )
    )
    second_response = processor.process(
        make_request(
            request_id="req_002",
            idempotency_key="idem_001",
        )
    )

    assert first_response.status == "routed"
    assert second_response.status == "duplicate_ignored"
    assert second_response.result_payload["accepted"] is False
    assert second_response.metadata["gateway_stage"] == "idempotency"
    assert second_response.metadata["idempotency"]["is_duplicate"] is True
    assert second_response.metadata["idempotency"]["first_request_id"] == "req_001"


def test_gateway_processor_returns_route_not_found_response() -> None:
    processor = GatewayProcessor(
        validator=SimpleValidator(),
        idempotency_service=InMemoryIdempotencyService(),
        router=SimpleRouter(routes=[]),
    )

    response = processor.process(make_request())

    assert response.status == "route_not_found"
    assert response.errors
    assert response.errors[0]["code"] == "route_not_found"
    assert response.errors[0]["field_path"] == "routing"
    assert response.metadata["gateway_stage"] == "routing"
    assert response.metadata["idempotency"]["is_duplicate"] is False