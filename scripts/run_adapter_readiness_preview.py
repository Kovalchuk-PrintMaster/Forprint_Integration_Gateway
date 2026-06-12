"""Run Gateway v0.4 adapter readiness preview."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT / "app") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "app"))

from forprint_integration_gateway.services.adapter_contracts import (  # noqa: E402
    load_adapter_contracts,
    validate_all_adapter_contracts,
)

ERROR_TAXONOMY_PATH = (
    PROJECT_ROOT / "examples" / "adapter_contracts" / "error_taxonomy_v0_4.json"
)


def load_error_taxonomy() -> dict[str, Any]:
    """Load error taxonomy fixture."""
    return json.loads(ERROR_TAXONOMY_PATH.read_text(encoding="utf-8"))


def main() -> int:
    """Run adapter readiness preview."""
    console = Console()
    console.print("🔎 Running ForPrint Gateway v0.4 adapter readiness preview...")

    errors = validate_all_adapter_contracts()
    if errors:
        console.print("❌ Adapter contract validation failed:")
        for error in errors:
            console.print(f"  - {error}")
        return 1

    contracts = load_adapter_contracts()
    taxonomy = load_error_taxonomy()

    table = Table(title="ForPrint Gateway v0.4 — adapter readiness preview")
    table.add_column("Adapter")
    table.add_column("Direction")
    table.add_column("Source")
    table.add_column("Target")
    table.add_column("Delivery")
    table.add_column("Runtime")
    table.add_column("Live")
    table.add_column("Retry")

    for contract in contracts:
        if contract.get("taxonomy_id"):
            continue

        table.add_row(
            str(contract["adapter_id"]),
            str(contract["direction"]),
            str(contract["source_module"]),
            str(contract["target_module"]),
            str(contract["delivery_mode"]),
            str(contract["runtime_status"]),
            str(contract["live_enabled"]).lower(),
            str(contract["retry_policy"]),
        )

    console.print(table)

    error_table = Table(title="Representative Gateway v0.4 error taxonomy entries")
    error_table.add_column("Code")
    error_table.add_column("Category")
    error_table.add_column("Severity")
    error_table.add_column("Retryable")

    for error in taxonomy["errors"][:6]:
        error_table.add_row(
            str(error["code"]),
            str(error["category"]),
            str(error["severity"]),
            str(error["retryable"]).lower(),
        )

    console.print(error_table)
    console.print("✅ Adapter readiness preview completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())