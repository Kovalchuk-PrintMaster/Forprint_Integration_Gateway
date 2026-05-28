"""Simple request validator for ForPrint Integration Gateway.

This validator is deliberately minimal for v0.1.

It checks the local IntegrationRequest envelope shape and required fields.
It does not validate real business rules and does not replace Library-owned
contract/schema validation.
"""

from collections.abc import Mapping
from dataclasses import asdict, is_dataclass
from typing import Any

from forprint_integration_gateway.models.envelope import IntegrationRequest
from forprint_integration_gateway.models.errors import ValidationError


class SimpleValidator:
    """Minimal Gateway envelope validator."""

    required_fields: tuple[str, ...] = (
        "request_id",
        "correlation_id",
        "idempotency_key",
        "source_module",
        "source_channel",
        "target_module",
        "contract_id",
        "contract_version",
        "operation",
        "payload",
        "metadata",
        "created_at",
    )

    def validate_request(
        self,
        request: IntegrationRequest | Mapping[str, Any],
    ) -> list[ValidationError]:
        """Validate an integration request envelope.

        Returns a list of ValidationError objects.
        Empty list means the local envelope is valid.
        """
        raw_request = self._to_mapping(request)
        errors: list[ValidationError] = []

        for field_name in self.required_fields:
            if field_name not in raw_request:
                errors.append(
                    ValidationError(
                        code="missing_required_field",
                        message=f"Required field is missing: {field_name}",
                        field_path=field_name,
                        severity="error",
                        is_retryable=False,
                    )
                )
                continue

            value = raw_request[field_name]
            if value is None or value == "":
                errors.append(
                    ValidationError(
                        code="empty_required_field",
                        message=f"Required field is empty: {field_name}",
                        field_path=field_name,
                        severity="error",
                        is_retryable=False,
                    )
                )

        payload = raw_request.get("payload")
        if payload is not None and not isinstance(payload, dict):
            errors.append(
                ValidationError(
                    code="invalid_payload_type",
                    message="payload must be a dictionary",
                    field_path="payload",
                    severity="error",
                    is_retryable=False,
                )
            )

        metadata = raw_request.get("metadata")
        if metadata is not None and not isinstance(metadata, dict):
            errors.append(
                ValidationError(
                    code="invalid_metadata_type",
                    message="metadata must be a dictionary",
                    field_path="metadata",
                    severity="error",
                    is_retryable=False,
                )
            )

        return errors

    @staticmethod
    def _to_mapping(request: IntegrationRequest | Mapping[str, Any]) -> Mapping[str, Any]:
        """Convert supported request input to a mapping."""
        if is_dataclass(request):
            return asdict(request)

        return request