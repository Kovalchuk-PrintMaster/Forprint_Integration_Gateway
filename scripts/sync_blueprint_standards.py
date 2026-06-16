"""Create or refresh Gateway local Blueprint standards snapshot."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT / "app") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "app"))


def main() -> int:
    """Sync standards snapshot."""
    from forprint_integration_gateway.services.blueprint_standards import (
        PROJECT_ROOT as SERVICE_PROJECT_ROOT,
    )
    from forprint_integration_gateway.services.blueprint_standards import (
        write_standards_snapshot,
    )

    path = write_standards_snapshot()
    print("✅ Gateway Blueprint standards snapshot refreshed.")
    print(f"  - {path.relative_to(SERVICE_PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())