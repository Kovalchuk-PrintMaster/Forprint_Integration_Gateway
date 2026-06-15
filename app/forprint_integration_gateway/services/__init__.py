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
from forprint_integration_gateway.services.contract_compatibility import (
    build_dry_run_delivery_plan,
    load_compatibility_matrix,
    load_replay_fixtures,
    replay_all_fixtures,
    replay_fixture,
    validate_all_contract_compatibility,
)
from forprint_integration_gateway.services.contract_release import (
    load_acceptance_fixtures,
    load_backward_gates,
    load_consumer_bundles,
    load_release_manifest,
    replay_backward_compatibility_gates,
    replay_consumer_acceptance_fixtures,
    validate_all_contract_release,
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
    "build_dry_run_delivery_plan",
    "load_compatibility_matrix",
    "load_replay_fixtures",
    "replay_all_fixtures",
    "replay_fixture",
    "validate_all_contract_compatibility",
    "load_acceptance_fixtures",
    "load_backward_gates",
    "load_consumer_bundles",
    "load_release_manifest",
    "replay_backward_compatibility_gates",
    "replay_consumer_acceptance_fixtures",
    "validate_all_contract_release",
]