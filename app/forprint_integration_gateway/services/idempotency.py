"""In-memory idempotency service for ForPrint Integration Gateway.

This service is intentionally non-persistent for v0.1.

It proves the Gateway boundary logic without introducing a database.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class IdempotencyCheckResult:
    """Result of an idempotency check."""

    idempotency_key: str
    current_request_id: str
    is_duplicate: bool
    first_request_id: str


class InMemoryIdempotencyService:
    """Simple in-memory idempotency key registry."""

    def __init__(self) -> None:
        self._records: dict[str, str] = {}

    def check_and_store(self, idempotency_key: str, request_id: str) -> IdempotencyCheckResult:
        """Check whether the idempotency key was already seen.

        If the key is new, store it and return is_duplicate=False.
        If the key exists, return is_duplicate=True and keep the original request id.
        """
        if not idempotency_key:
            raise ValueError("idempotency_key must not be empty")

        if not request_id:
            raise ValueError("request_id must not be empty")

        if idempotency_key in self._records:
            return IdempotencyCheckResult(
                idempotency_key=idempotency_key,
                current_request_id=request_id,
                is_duplicate=True,
                first_request_id=self._records[idempotency_key],
            )

        self._records[idempotency_key] = request_id

        return IdempotencyCheckResult(
            idempotency_key=idempotency_key,
            current_request_id=request_id,
            is_duplicate=False,
            first_request_id=request_id,
        )