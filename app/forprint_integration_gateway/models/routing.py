"""Routing models for ForPrint Integration Gateway."""

from dataclasses import dataclass


@dataclass(slots=True)
class RoutingRule:
    """Local placeholder routing rule.

    In v0.1 routes are loaded from local YAML config.

    Final route and contract ownership should later move toward Blueprint /
    Library contract registry standards.
    """

    route_id: str
    source_module: str
    target_module: str
    contract_id: str
    operation: str
    enabled: bool = True
    priority: int = 0