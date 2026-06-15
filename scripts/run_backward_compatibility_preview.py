"""Run Gateway v0.6 backward compatibility preview."""

from __future__ import annotations

import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT / "app") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "app"))

from forprint_integration_gateway.services.contract_release import (  # noqa: E402
    replay_backward_compatibility_gates,
    validate_backward_compatibility_gates,
)


def main() -> int:
    """Run backward compatibility preview."""
    console = Console()
    console.print("🔎 Running Gateway v0.6 backward compatibility preview...")

    errors = validate_backward_compatibility_gates()
    if errors:
        console.print("❌ Backward compatibility validation failed:")
        for error in errors:
            console.print(f"  - {error}")
        return 1

    table = Table(title="ForPrint Gateway v0.6 — backward compatibility preview")
    table.add_column("Previous layer")
    table.add_column("Protected concept")
    table.add_column("Expected")
    table.add_column("Actual")
    table.add_column("Result")

    for result in replay_backward_compatibility_gates():
        table.add_row(
            result["previous_layer"],
            result["protected_concept"],
            result["expected_status"],
            result["actual_status"],
            "OK" if result["passed"] else "FAIL",
        )

    console.print(table)
    console.print("✅ Backward compatibility preview completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())