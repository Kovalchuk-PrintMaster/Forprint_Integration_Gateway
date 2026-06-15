"""Run Gateway v0.6 contract release preview."""

from __future__ import annotations

import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT / "app") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "app"))

from forprint_integration_gateway.services.contract_release import (  # noqa: E402
    load_consumer_bundles,
    load_release_manifest,
    validate_release_manifest,
)


def main() -> int:
    """Run contract release preview."""
    console = Console()
    console.print("🔎 Running Gateway v0.6 contract release preview...")

    errors = validate_release_manifest()
    if errors:
        console.print("❌ Contract release manifest validation failed:")
        for error in errors:
            console.print(f"  - {error}")
        return 1

    manifest = load_release_manifest()
    bundles = load_consumer_bundles()

    table = Table(title="ForPrint Gateway v0.6 — contract release preview")
    table.add_column("Release")
    table.add_column("Artifacts")
    table.add_column("Consumer bundles")
    table.add_column("Producer modules")
    table.add_column("Live")
    table.add_column("Boundary")

    table.add_row(
        str(manifest["release_id"]),
        str(len(manifest["artifacts"])),
        str(len(bundles["bundles"])),
        str(len(manifest["supported_producer_modules"])),
        str(manifest["live_delivery_enabled"]).lower(),
        "offline/dry-run/contract-only",
    )

    console.print(table)
    console.print("✅ Contract release preview completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())