"""Error models for ForPrint Integration Gateway."""

from dataclasses import dataclass


@dataclass(slots=True)
class ValidationError:
    """Standard validation error returned by Gateway validation services."""

    code: str
    message: str
    field_path: str
    severity: str = "error"
    is_retryable: bool = False