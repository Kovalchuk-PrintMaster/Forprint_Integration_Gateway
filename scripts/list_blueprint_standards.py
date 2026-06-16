"""List Blueprint standards visible to Gateway."""

from __future__ import annotations

import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT / "app") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "app"))

from forprint_integration_gateway.services.blueprint_standards import (  # noqa: E402
    STANDARDS_INDEX_RELATIVE_PATH,
    get_blueprint_root,
    list_blueprint_standards,
)


def main() -> int:
    """List Blueprint standards."""
    console = Console()
    blueprint_root = get_blueprint_root()
    standards = list_blueprint_standards()

    console.print("== Gateway Blueprint standards list ==")
    console.print(f"Standards index: {blueprint_root / STANDARDS_INDEX_RELATIVE_PATH}")
    console.print(f"Standards count: {len(standards)}")

    table = Table(title="Blueprint standards visible to Gateway")
    table.add_column("Standard ID")
    table.add_column("File path")
    table.add_column("Status")
    table.add_column("Adoption mode")

    for standard in standards:
        table.add_row(
            standard.standard_id,
            standard.path,
            standard.status,
            standard.adoption_mode,
        )

    console.print(table)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())