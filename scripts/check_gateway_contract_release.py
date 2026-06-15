"""Validate Gateway v0.6 contract release package."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT / "app") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "app"))

from forprint_integration_gateway.services.contract_release import (  # noqa: E402
    validate_all_contract_release,
)


def main() -> int:
    """Run v0.6 contract release check."""
    print("== Gateway v0.6 contract release check ==")
    errors = validate_all_contract_release()

    if errors:
        for error in errors:
            print(f"❌ {error}")
        return 1

    print("✅ Release manifest")
    print("✅ Consumer bundles")
    print("✅ Consumer acceptance fixtures")
    print("✅ Backward compatibility gates")
    print("✅ Gateway v0.6 contract release package is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())