"""Run Gateway v0.6 consumer acceptance preview."""

from __future__ import annotations

import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT / "app") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "app"))

from forprint_integration_gateway.services.contract_release import (  # noqa: E402
    replay_consumer_acceptance_fixtures,
    validate_acceptance_fixtures,
)


def main() -> int:
    """Run consumer acceptance preview."""
    console = Console()
    console.print("🔎 Running Gateway v0.6 consumer acceptance preview...")

    errors = validate_acceptance_fixtures()
    if errors:
        console.print("❌ Consumer acceptance validation failed:")
        for error in errors:
            console.print(f"  - {error}")
        return 1

    table = Table(title="ForPrint Gateway v0.6 — consumer acceptance preview")
    table.add_column("Consumer")
    table.add_column("Fixture")
    table.add_column("Expected")
    table.add_column("Actual")
    table.add_column("Compatibility")
    table.add_column("Boundary")

    for result in replay_consumer_acceptance_fixtures():
        table.add_row(
            result["consumer_module"],
            result["fixture_id"],
            result["expected_result"],
            result["actual_result"],
            result["compatibility_state"],
            result["boundary_status"],
        )

    console.print(table)
    console.print("✅ Consumer acceptance preview completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())