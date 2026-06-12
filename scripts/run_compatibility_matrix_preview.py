"""Run Gateway v0.5 compatibility matrix preview."""

from __future__ import annotations

import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT / "app") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "app"))

from forprint_integration_gateway.services.contract_compatibility import (  # noqa: E402
    load_compatibility_matrix,
    validate_compatibility_matrix,
)


def main() -> int:
    """Run compatibility matrix preview."""
    console = Console()
    console.print("🔎 Running Gateway v0.5 compatibility matrix preview...")

    errors = validate_compatibility_matrix()
    if errors:
        console.print("❌ Compatibility matrix validation failed:")
        for error in errors:
            console.print(f"  - {error}")
        return 1

    matrix = load_compatibility_matrix()

    table = Table(title="ForPrint Gateway v0.5 — compatibility matrix preview")
    table.add_column("Source flow")
    table.add_column("Target contract")
    table.add_column("Operation")
    table.add_column("Version")
    table.add_column("State")
    table.add_column("Delivery")
    table.add_column("Live")
    table.add_column("Notes")

    for rule in matrix["rules"]:
        table.add_row(
            str(rule["source_flow"]),
            str(rule["target_contract"]),
            str(rule["operation"]),
            str(rule["contract_version"]),
            str(rule["compatibility_state"]),
            str(rule["delivery_mode"]),
            str(rule["live_enabled"]).lower(),
            "; ".join(str(note) for note in rule.get("notes", [])),
        )

    console.print(table)
    console.print("✅ Compatibility matrix preview completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())