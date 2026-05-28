import pytest

from forprint_integration_gateway.services.idempotency import InMemoryIdempotencyService


def test_idempotency_service_recognizes_first_key_as_new() -> None:
    service = InMemoryIdempotencyService()

    result = service.check_and_store(
        idempotency_key="idem_001",
        request_id="req_001",
    )

    assert result.idempotency_key == "idem_001"
    assert result.current_request_id == "req_001"
    assert result.first_request_id == "req_001"
    assert result.is_duplicate is False


def test_idempotency_service_recognizes_repeated_key() -> None:
    service = InMemoryIdempotencyService()

    first_result = service.check_and_store(
        idempotency_key="idem_001",
        request_id="req_001",
    )
    second_result = service.check_and_store(
        idempotency_key="idem_001",
        request_id="req_002",
    )

    assert first_result.is_duplicate is False
    assert second_result.is_duplicate is True
    assert second_result.current_request_id == "req_002"
    assert second_result.first_request_id == "req_001"


def test_idempotency_service_rejects_empty_idempotency_key() -> None:
    service = InMemoryIdempotencyService()

    with pytest.raises(ValueError):
        service.check_and_store(
            idempotency_key="",
            request_id="req_001",
        )


def test_idempotency_service_rejects_empty_request_id() -> None:
    service = InMemoryIdempotencyService()

    with pytest.raises(ValueError):
        service.check_and_store(
            idempotency_key="idem_001",
            request_id="",
        )