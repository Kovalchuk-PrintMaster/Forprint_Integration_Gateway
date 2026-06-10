from forprint_integration_gateway.models.channel_intake import (
    BusinessRequestKind,
    ChannelSource,
)
from forprint_integration_gateway.services.channel_intake import (
    ChannelIntakeProcessor,
    load_channel_intake_example,
)

ACCEPTED_EXAMPLES = [
    "telegram_new_order_request.json",
    "telegram_order_clarification_request.json",
    "website_price_estimate_request.json",
    "crm_client_lookup_request.json",
    "mobile_app_file_prepress_request.json",
    "website_manager_handoff_request.json",
]


def test_supported_channel_sources_are_expected() -> None:
    assert {source.value for source in ChannelSource} == {
        "telegram_bot",
        "website",
        "forprint_crm",
        "mobile_app",
    }


def test_supported_business_request_kinds_are_expected() -> None:
    assert {kind.value for kind in BusinessRequestKind} == {
        "new_order_request",
        "order_clarification",
        "price_estimate_request",
        "client_lookup_request",
        "file_prepress_request",
        "manager_handoff_request",
    }


def test_accepted_channel_intake_examples_process_successfully() -> None:
    processor = ChannelIntakeProcessor()

    for filename in ACCEPTED_EXAMPLES:
        envelope = load_channel_intake_example(filename)

        issues, normalized_request, route_decision, handoff_candidate = processor.process(envelope)

        assert issues == []
        assert normalized_request is not None
        assert route_decision is not None
        assert handoff_candidate is not None
        assert route_decision.is_live_delivery_enabled is False
        assert handoff_candidate.is_live_write_enabled is False
        assert normalized_request.correlation_context.correlation_id.startswith("corr:")
        assert normalized_request.idempotency_policy.idempotency_key.startswith("idem:")


def test_mobile_app_example_is_marked_planned_future() -> None:
    processor = ChannelIntakeProcessor()
    envelope = load_channel_intake_example("mobile_app_file_prepress_request.json")

    issues, normalized_request, route_decision, handoff_candidate = processor.process(envelope)

    assert issues == []
    assert normalized_request is not None
    assert route_decision is not None
    assert handoff_candidate is not None
    assert envelope.channel_source == "mobile_app"
    assert route_decision.is_future_runtime is True
    assert route_decision.metadata["mobile_app_planned_future"] is True
    assert normalized_request.metadata["planned_future_channel"] is True


def test_invalid_channel_intake_example_returns_validation_issue() -> None:
    processor = ChannelIntakeProcessor()
    envelope = load_channel_intake_example("invalid_missing_contact_request.json")

    issues, normalized_request, route_decision, handoff_candidate = processor.process(envelope)

    assert normalized_request is None
    assert route_decision is None
    assert handoff_candidate is None
    assert issues
    assert issues[0].code == "missing_client_identity_hint"
    assert issues[0].field_path == "client_identity_hint"