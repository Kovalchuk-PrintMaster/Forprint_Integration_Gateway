
from pathlib import Path

from forprint_integration_gateway.services.example_loader import (
    load_contract_fixture,
    load_example_request,
    load_example_response,
)
from forprint_integration_gateway.services.gateway_processor import GatewayProcessor
from forprint_integration_gateway.services.idempotency import InMemoryIdempotencyService
from forprint_integration_gateway.services.router import SimpleRouter, load_routes_from_yaml
from forprint_integration_gateway.services.validator import SimpleValidator

PROJECT_ROOT = Path(__file__).resolve().parents[1]

EXAMPLE_REQUEST_FILES = [
    "customer_channel_quote_preview_request.json",
    "crm_to_calculator_quote_recalculation_request.json",
    "crm_to_accounting_invoice_request.json",
]

EXAMPLE_RESPONSE_FILES = [
    "calculator_to_crm_quote_result_response.json",
    "validation_error_response.json",
]

CONTRACT_FIXTURE_FILES = [
    "calculator.quote_request.v1.yaml",
    "calculator.quote_response.v1.yaml",
    "accounting.invoice_request.v1.yaml",
]


def make_processor_from_local_routes() -> GatewayProcessor:
    routes_path = PROJECT_ROOT / "app" / "forprint_integration_gateway" / "config" / "routes.yaml"

    return GatewayProcessor(
        validator=SimpleValidator(),
        idempotency_service=InMemoryIdempotencyService(),
        router=SimpleRouter(routes=load_routes_from_yaml(routes_path)),
    )


def test_example_requests_are_valid_envelopes() -> None:
    validator = SimpleValidator()

    for filename in EXAMPLE_REQUEST_FILES:
        request = load_example_request(filename)

        errors = validator.validate_request(request)

        assert errors == []


def test_example_requests_can_pass_gateway_processor() -> None:
    processor = make_processor_from_local_routes()

    for filename in EXAMPLE_REQUEST_FILES:
        request = load_example_request(filename)

        response = processor.process(request)

        assert response.status == "routed"
        assert response.result_payload["route_id"]
        assert response.metadata["gateway_stage"] == "routing"


def test_example_responses_can_be_loaded() -> None:
    for filename in EXAMPLE_RESPONSE_FILES:
        response = load_example_response(filename)

        assert response.request_id
        assert response.correlation_id
        assert response.status
        assert isinstance(response.result_payload, dict)
        assert isinstance(response.errors, list)
        assert isinstance(response.warnings, list)


def test_contract_fixtures_are_documentation_only() -> None:
    for filename in CONTRACT_FIXTURE_FILES:
        contract = load_contract_fixture(filename)

        assert contract["contract_id"]
        assert contract["version"] == "v1"
        assert contract["fixture_status"] == "documentation_only"
        assert contract["canonical_contract_truth"] == "forprint_library_future"