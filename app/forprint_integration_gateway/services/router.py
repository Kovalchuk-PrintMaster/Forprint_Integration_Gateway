"""Simple local router for ForPrint Integration Gateway.

The router uses local placeholder RoutingRule objects in v0.1.

It does not call real modules.
It does not execute business logic.
It only decides which placeholder route matches the request envelope.
"""

from collections.abc import Sequence
from pathlib import Path
from typing import Any

import yaml

from forprint_integration_gateway.models.envelope import IntegrationRequest
from forprint_integration_gateway.models.routing import RoutingRule


class RouteNotFoundError(Exception):
    """Raised when the Gateway cannot find a matching local route."""


class SimpleRouter:
    """Minimal route matcher for local placeholder routes."""

    def __init__(self, routes: Sequence[RoutingRule]) -> None:
        self.routes = list(routes)

    def match(self, request: IntegrationRequest) -> RoutingRule:
        """Return the highest-priority matching route for the request.

        Higher numeric priority wins.
        Disabled routes are ignored.
        """
        candidates = [
            route
            for route in self.routes
            if route.enabled
            and route.source_module == request.source_module
            and route.target_module == request.target_module
            and route.contract_id == request.contract_id
            and route.operation == request.operation
        ]

        if not candidates:
            raise RouteNotFoundError(
                "No route found for "
                f"source_module={request.source_module}, "
                f"target_module={request.target_module}, "
                f"contract_id={request.contract_id}, "
                f"operation={request.operation}"
            )

        return sorted(candidates, key=lambda route: route.priority, reverse=True)[0]


def load_routes_from_yaml(path: str | Path) -> list[RoutingRule]:
    """Load local placeholder routes from YAML."""
    routes_path = Path(path)

    with routes_path.open("r", encoding="utf-8") as file:
        raw_config: dict[str, Any] = yaml.safe_load(file) or {}

    raw_routes = raw_config.get("routes", [])

    return [RoutingRule(**raw_route) for raw_route in raw_routes]