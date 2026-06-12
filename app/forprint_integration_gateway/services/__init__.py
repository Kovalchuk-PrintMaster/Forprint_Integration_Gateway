"""Services for ForPrint Integration Gateway."""

from forprint_integration_gateway.services.adapter_contracts import (
    AdapterContractValidationError,
    load_adapter_contracts,
    validate_adapter_contract,
    validate_all_adapter_contracts,
)
from forprint_integration_gateway.services.channel_intake import (
    ChannelIntakeProcessor,
    load_channel_intake_example,
    serialize_channel_intake_result,
)
from forprint_integration_gateway.services.example_loader import (
    load_contract_fixture,
    load_example_request,
    load_example_response,
)
from forprint_integration_gateway.services.gateway_processor import GatewayProcessor
from forprint_integration_gateway.services.idempotency import InMemoryIdempotencyService
from forprint_integration_gateway.services.router import RouteNotFoundError, SimpleRouter
from forprint_integration_gateway.services.validator import SimpleValidator

__all__ = [
    "ChannelIntakeProcessor",
    "GatewayProcessor",
    "InMemoryIdempotencyService",
    "RouteNotFoundError",
    "SimpleRouter",
    "SimpleValidator",
    "load_channel_intake_example",
    "load_contract_fixture",
    "load_example_request",
    "load_example_response",
    "serialize_channel_intake_result",
    "AdapterContractValidationError",
    "load_adapter_contracts",
    "validate_adapter_contract",
    "validate_all_adapter_contracts",
]