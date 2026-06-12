"""Validate Gateway v0.5 contract compatibility and replay fixtures."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT / "app") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "app"))

from forprint_integration_gateway.services.contract_compatibility import (  # noqa: E402
    validate_all_contract_compatibility,
)


def main() -> int:
    """Run v0.5 contract compatibility check."""
    print("== Gateway v0.5 contract compatibility check ==")
    errors = validate_all_contract_compatibility()

    if errors:
        for error in errors:
            print(f"❌ {error}")
        return 1

    print("✅ Compatibility matrix")
    print("✅ Replay fixtures")
    print("✅ Golden paths")
    print("✅ Negative paths blocked as expected")
    print("✅ Dry-run delivery planner")
    print("✅ Gateway v0.5 contract compatibility is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())