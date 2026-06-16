"""Check Blueprint standards visibility for Gateway."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT / "app") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "app"))

from forprint_integration_gateway.services.blueprint_standards import (  # noqa: E402
    validate_blueprint_standards_ready,
)


def main() -> int:
    """Check standards visibility."""
    print("== Gateway Blueprint standards visibility check ==")
    errors = validate_blueprint_standards_ready()

    if errors:
        for error in errors:
            print(f"❌ {error}")
        return 1

    print("✅ Blueprint repository reachable")
    print("✅ Standards index readable")
    print("✅ Standards files referenced by index exist")
    print("✅ Advisory semantics explicit")
    print("✅ Local standards snapshot valid")
    print("✅ Gateway standards visibility is ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())