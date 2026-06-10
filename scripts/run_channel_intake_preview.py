# python scripts/run_channel_intake_preview.py
"""Preview Gateway v0.3 channel intake processing.

Developer-only terminal preview.

No API.
No database.
No queues.
No external calls.
No live module integrations.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_PATH = PROJECT_ROOT / "app"

if str(APP_PATH) not in sys.path:
    sys.path.insert(0, str(APP_PATH))

from forprint_integration_gateway.services.channel_intake import (  # noqa: E402
    ChannelIntakeProcessor,
    load_channel_intake_example,
    serialize_channel_intake_result,
)

SAMPLES = [
    ("accepted Telegram sample", "telegram_new_order_request.json", True),
    ("accepted Website sample", "website_price_estimate_request.json", True),
    ("accepted CRM sample", "crm_client_lookup_request.json", True),
    ("future Mobile App sample", "mobile_app_file_prepress_request.json", True),
    ("invalid sample", "invalid_missing_contact_request.json", False),
]


def build_table(rows: list[dict[str, str]]) -> Table:
    """Build terminal preview table."""
    table = Table(title="ForPrint Gateway v0.3 — channel intake preview")
    table.add_column("Sample", style="bold")
    table.add_column("Channel")
    table.add_column("Status", justify="center")
    table.add_column("Route")
    table.add_column("Correlation")
    table.add_column("Idempotency")

    for row in rows:
        status = row["status"]
        status_style = "green" if status == "ACCEPTED" else "red"
        table.add_row(
            row["sample"],
            row["channel"],
            f"[{status_style}]{status}[/{status_style}]",
            row["route"],
            row["correlation"],
            row["idempotency"],
        )

    return table


def main() -> int:
    """Run channel intake preview."""
    console = Console()
    processor = ChannelIntakeProcessor()
    preview_rows: list[dict[str, str]] = []
    failures: list[str] = []

    console.print("🔎 Running ForPrint Gateway v0.3 channel intake preview...")

    for label, filename, should_be_accepted in SAMPLES:
        envelope = load_channel_intake_example(filename)
        issues, normalized_request, route_decision, handoff_candidate = processor.process(envelope)

        accepted = not issues
        if accepted != should_be_accepted:
            failures.append(
                f"{filename}: expected accepted={should_be_accepted}, got accepted={accepted}"
            )

        serialized = serialize_channel_intake_result(
            issues,
            normalized_request,
            route_decision,
            handoff_candidate,
        )

        channel_label = envelope.channel_source
        if envelope.channel_source == "mobile_app":
            channel_label = "mobile_app (planned/future)"

        preview_rows.append(
            {
                "sample": label,
                "channel": channel_label,
                "status": "ACCEPTED" if accepted else "REJECTED",
                "route": route_decision.route_id if route_decision else "-",
                "correlation": (
                    normalized_request.correlation_context.correlation_id
                    if normalized_request
                    else "-"
                ),
                "idempotency": (
                    normalized_request.idempotency_policy.idempotency_key
                    if normalized_request
                    else "-"
                ),
            }
        )

        console.print()
        console.print(f"## {label}: {filename}")
        console.print(json.dumps(serialized, ensure_ascii=False, indent=2))

    console.print()
    console.print(build_table(preview_rows))

    if failures:
        console.print()
        console.print("[red]❌ Channel intake preview failed[/red]")
        for failure in failures:
            console.print(f"[red]- {failure}[/red]")
        return 1

    console.print()
    console.print("✅ Channel intake preview completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())