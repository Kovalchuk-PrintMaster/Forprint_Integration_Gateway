"""Run Gateway v0.5 replay fixtures preview."""

from __future__ import annotations

import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT / "app") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "app"))

from forprint_integration_gateway.services.contract_compatibility import (  # noqa: E402
    replay_all_fixtures,
    validate_all_contract_compatibility,
)


def main() -> int:
    """Run replay fixtures preview."""
    console = Console()
    console.print("🔎 Running Gateway v0.5 replay fixtures preview...")

    errors = validate_all_contract_compatibility()
    if errors:
        console.print("❌ Replay validation failed:")
        for error in errors:
            console.print(f"  - {error}")
        return 1

    results = replay_all_fixtures()

    table = Table(title="ForPrint Gateway v0.5 — replay fixtures preview")
    table.add_column("Fixture")
    table.add_column("Type")
    table.add_column("Expected")
    table.add_column("Actual")
    table.add_column("State")
    table.add_column("Plan")
    table.add_column("Boundary")

    for result in results:
        table.add_row(
            result.fixture_id,
            result.fixture_type.value,
            result.expected_result.value,
            result.actual_result.value,
            result.compatibility_state.value,
            result.delivery_plan_status,
            result.boundary_status,
        )

    console.print(table)
    console.print("✅ Replay fixtures preview completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())