from forprint_integration_gateway.models.envelope import IntegrationRequest, IntegrationResponse


def test_integration_request_model_can_be_created() -> None:
    request = IntegrationRequest(
        request_id="req_001",
        correlation_id="corr_001",
        idempotency_key="idem_001",
        source_module="customer_channel",
        source_channel="telegram",
        target_module="forprint_crm",
        contract_id="crm.order_intake.v1",
        contract_version="v1",
        operation="order.intake.submitted",
        payload={"message": "Need business cards"},
        metadata={"customer_channel": "telegram"},
    )

    assert request.request_id == "req_001"
    assert request.source_channel == "telegram"
    assert request.payload["message"] == "Need business cards"
    assert request.created_at


def test_integration_response_model_can_be_created() -> None:
    response = IntegrationResponse(
        request_id="req_001",
        correlation_id="corr_001",
        target_module="forprint_crm",
        status="accepted",
        result_payload={"accepted": True},
        metadata={"route_id": "customer_channel_to_crm_order_intake"},
    )

    assert response.request_id == "req_001"
    assert response.status == "accepted"
    assert response.result_payload["accepted"] is True
    assert response.created_at