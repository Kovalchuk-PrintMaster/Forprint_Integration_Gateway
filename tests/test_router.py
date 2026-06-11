from pathlib import Path

import pytest

from forprint_integration_gateway.models.envelope import IntegrationRequest
from forprint_integration_gateway.models.routing import RoutingRule
from forprint_integration_gateway.services.router import (
    RouteNotFoundError,
    SimpleRouter,
    load_routes_from_yaml,
)


def make_quote_preview_request() -> IntegrationRequest:
    return IntegrationRequest(
        request_id="req_001",
        correlation_id="corr_001",
        idempotency_key="idem_001",
        source_module="customer_channel",
        source_channel="website",
        target_module="calculator_engine",
        contract_id="calculator.quote_request.v1",
        contract_version="v1",
        operation="quote.preview.requested",
        payload={"product": "business_card"},
        metadata={},
    )


def test_router_can_match_simple_placeholder_route() -> None:
    route = RoutingRule(
        route_id="customer_channel_to_calculator_quote_preview",
        source_module="customer_channel",
        target_module="calculator_engine",
        contract_id="calculator.quote_request.v1",
        operation="quote.preview.requested",
        enabled=True,
        priority=100,
    )

    router = SimpleRouter(routes=[route])

    matched_route = router.match(make_quote_preview_request())

    assert matched_route.route_id == "customer_channel_to_calculator_quote_preview"


def test_router_rejects_missing_route() -> None:
    router = SimpleRouter(routes=[])

    with pytest.raises(RouteNotFoundError):
        router.match(make_quote_preview_request())


def test_router_ignores_disabled_route() -> None:
    route = RoutingRule(
        route_id="disabled_route",
        source_module="customer_channel",
        target_module="calculator_engine",
        contract_id="calculator.quote_request.v1",
        operation="quote.preview.requested",
        enabled=False,
        priority=100,
    )

    router = SimpleRouter(routes=[route])

    with pytest.raises(RouteNotFoundError):
        router.match(make_quote_preview_request())


def test_router_prefers_higher_priority_matching_route() -> None:
    low_priority_route = RoutingRule(
        route_id="low_priority_route",
        source_module="customer_channel",
        target_module="calculator_engine",
        contract_id="calculator.quote_request.v1",
        operation="quote.preview.requested",
        enabled=True,
        priority=10,
    )

    high_priority_route = RoutingRule(
        route_id="high_priority_route",
        source_module="customer_channel",
        target_module="calculator_engine",
        contract_id="calculator.quote_request.v1",
        operation="quote.preview.requested",
        enabled=True,
        priority=100,
    )

    router = SimpleRouter(routes=[low_priority_route, high_priority_route])

    matched_route = router.match(make_quote_preview_request())

    assert matched_route.route_id == "high_priority_route"


def test_routes_can_be_loaded_from_local_yaml_config() -> None:
    project_root = Path(__file__).resolve().parents[1]
    routes_path = project_root / "app" / "forprint_integration_gateway" / "config" / "routes.yaml"

    routes = load_routes_from_yaml(routes_path)

    assert routes
    assert any(route.route_id == "customer_channel_to_crm_order_intake" for route in routes)
    assert any(route.route_id == "customer_channel_to_calculator_quote_preview" for route in routes)