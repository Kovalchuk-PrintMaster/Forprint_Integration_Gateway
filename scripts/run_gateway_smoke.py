# python scripts/run_gateway_smoke.py
"""Run a local developer-only smoke check for ForPrint Integration Gateway.

This script demonstrates the local GatewayProcessor pipeline:

1. Load local placeholder routes.
2. Load one example request.
3. Run GatewayProcessor.
4. Print normalized IntegrationResponse.
5. Exit with non-zero code if the request was not routed.

This script does not:
- start API;
- connect to database;
- call CRM;
- call Calculator;
- call Accounting;
- call Prepress;
- publish queues.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

from rich.console import Console

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_PATH = PROJECT_ROOT / "app"

if str(APP_PATH) not in sys.path:
    sys.path.insert(0, str(APP_PATH))

from forprint_integration_gateway.services.example_loader import load_example_request  # noqa: E402
from forprint_integration_gateway.services.gateway_processor import GatewayProcessor  # noqa: E402
from forprint_integration_gateway.services.idempotency import (  # noqa: E402
    InMemoryIdempotencyService,
)
from forprint_integration_gateway.services.router import (  # noqa: E402
    SimpleRouter,
    load_routes_from_yaml,
)
from forprint_integration_gateway.services.validator import SimpleValidator  # noqa: E402

DEFAULT_EXAMPLE_REQUEST = "customer_channel_quote_preview_request.json"


def main(argv: list[str] | None = None) -> int:
    """Run local smoke scenario."""
    console = Console()
    args = argv if argv is not None else sys.argv[1:]
    example_request_filename = args[0] if args else DEFAULT_EXAMPLE_REQUEST

    console.print("🔎 Running ForPrint Integration Gateway smoke scenario...")
    console.print(f"📄 Example request: {example_request_filename}")

    try:
        routes_path = (
            PROJECT_ROOT
            / "app"
            / "forprint_integration_gateway"
            / "config"
            / "routes.yaml"
        )
        routes = load_routes_from_yaml(routes_path)

        request = load_example_request(example_request_filename)

        processor = GatewayProcessor(
            validator=SimpleValidator(),
            idempotency_service=InMemoryIdempotencyService(),
            router=SimpleRouter(routes=routes),
        )

        response = processor.process(request)
        response_payload = asdict(response)

        console.print()
        console.print("Normalized IntegrationResponse:")
        console.print(json.dumps(response_payload, ensure_ascii=False, indent=2))

        if response.status != "routed":
            console.print()
            console.print(f"[red]❌ Gateway smoke failed with status: {response.status}[/red]")
            return 1

    except Exception as exc:
        console.print()
        console.print(f"[red]❌ Gateway smoke failed: {exc}[/red]")
        return 1

    console.print()
    console.print("✅ Gateway smoke completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())