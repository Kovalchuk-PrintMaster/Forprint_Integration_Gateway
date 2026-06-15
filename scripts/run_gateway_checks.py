# python scripts/run_gateway_checks.py
"""Run local ForPrint Integration Gateway checks and generate reports.

This script is intentionally local/dev-only.

It does not start API servers.
It does not connect to databases.
It does not call real CRM, Calculator, Accounting or Prepress services.

Checks included:
- Ruff lint;
- Pytest;
- module manifest validation;
- local routes.yaml validation;
- architecture boundary document validation.

Outputs:
- terminal table;
- reports/gateway_check_report.json;
- reports/gateway_check_report.md.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from rich.console import Console
from rich.table import Table

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_PATH = PROJECT_ROOT / "app"
REPORTS_DIR = PROJECT_ROOT / "reports"
JSON_REPORT_PATH = REPORTS_DIR / "gateway_check_report.json"
MARKDOWN_REPORT_PATH = REPORTS_DIR / "gateway_check_report.md"

# Make local app package importable even before editable install is refreshed.
if str(APP_PATH) not in sys.path:
    sys.path.insert(0, str(APP_PATH))

from forprint_integration_gateway.services.router import load_routes_from_yaml  # noqa: E402


@dataclass(slots=True)
class CheckResult:
    """Single check result for terminal and file reports."""

    name: str
    expected_result: str
    status: str
    duration_seconds: float
    command: str | None = None
    details: str = ""


def utc_now_iso() -> str:
    """Return current UTC timestamp for generated report metadata."""
    return datetime.now(UTC).isoformat()


def run_command_check(name: str, expected_result: str, command: list[str]) -> CheckResult:
    """Run subprocess command and convert it to a CheckResult."""
    started_at = time.perf_counter()

    completed = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    duration = time.perf_counter() - started_at
    status = "OK" if completed.returncode == 0 else "FAIL"

    details_parts = []
    if completed.stdout.strip():
        details_parts.append(completed.stdout.strip())
    if completed.stderr.strip():
        details_parts.append(completed.stderr.strip())

    return CheckResult(
        name=name,
        expected_result=expected_result,
        status=status,
        duration_seconds=duration,
        command=" ".join(command),
        details="\n".join(details_parts),
    )

def validate_examples_and_contract_fixtures() -> CheckResult:
    """Validate local v0.2 example files and documentation-only contract fixtures."""
    started_at = time.perf_counter()

    try:
        required_example_files = [
            PROJECT_ROOT / "examples" / "requests" / "customer_channel_quote_preview_request.json",
            PROJECT_ROOT
            / "examples"
            / "requests"
            / "crm_to_calculator_quote_recalculation_request.json",
            PROJECT_ROOT / "examples" / "requests" / "crm_to_accounting_invoice_request.json",
            PROJECT_ROOT
            / "examples"
            / "responses"
            / "calculator_to_crm_quote_result_response.json",
            PROJECT_ROOT / "examples" / "responses" / "validation_error_response.json",
            PROJECT_ROOT / "examples" / "contracts" / "calculator.quote_request.v1.yaml",
            PROJECT_ROOT / "examples" / "contracts" / "calculator.quote_response.v1.yaml",
            PROJECT_ROOT / "examples" / "contracts" / "accounting.invoice_request.v1.yaml",
        ]

        missing_files = [
            str(path.relative_to(PROJECT_ROOT)) 
            for path in required_example_files 
            if not path.exists()
        ]
        if missing_files:
            raise FileNotFoundError("Missing v0.2 example file(s): " + ", ".join(missing_files))

        for path in required_example_files:
            if path.suffix == ".json":
                json.loads(path.read_text(encoding="utf-8"))
            elif path.suffix in {".yaml", ".yml"}:
                fixture = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

                required_contract_fields = {
                    "contract_id",
                    "version",
                    "producer",
                    "consumer",
                    "operation",
                    "description",
                    "required_payload_fields",
                    "example_request_file",
                    "example_response_file",
                    "fixture_status",
                    "canonical_contract_truth",
                }

                missing_contract_fields = sorted(required_contract_fields - set(fixture))
                if missing_contract_fields:
                    raise ValueError(
                        f"{path.name} misses field(s): " + ", ".join(missing_contract_fields)
                    )

                if fixture["fixture_status"] != "documentation_only":
                    raise ValueError(f"{path.name} must be documentation_only")

                if fixture["canonical_contract_truth"] != "forprint_library_future":
                    raise ValueError(f"{path.name} must point canonical truth to Library future")

        status = "OK"
        details = "Examples and documentation-only contract fixtures validation passed"

    except Exception as exc:
        status = "FAIL"
        details = str(exc)

    return CheckResult(
        name="Examples/contracts validation",
        expected_result="v0.2 examples і documentation-only contract fixtures валідні",
        status=status,
        duration_seconds=time.perf_counter() - started_at,
        command=None,
        details=details,
    )

def validate_manifest() -> CheckResult:
    """Validate minimal Blueprint-compatible module manifest fields."""
    started_at = time.perf_counter()
    manifest_path = PROJECT_ROOT / "forprint_module_manifest.yaml"

    try:
        if not manifest_path.exists():
            raise FileNotFoundError("forprint_module_manifest.yaml not found")

        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}

        required_top_level_fields = {
            "module_id",
            "module_name",
            "role",
            "status",
            "description",
            "owns",
            "consumes",
            "must_not_own",
        }

        missing_fields = sorted(required_top_level_fields - set(manifest))
        if missing_fields:
            raise ValueError(f"Missing manifest fields: {', '.join(missing_fields)}")

        if manifest["module_id"] != "forprint_integration_gateway":
            raise ValueError("module_id must be forprint_integration_gateway")

        if manifest["status"] != "bootstrap_development":
            raise ValueError("status must be bootstrap_development")

        required_boundaries = {
            "client_registry",
            "order_registry",
            "material_catalog",
            "product_catalog",
            "price_calculation",
            "invoice",
            "payment_status",
            "warehouse_stock",
            "business_workflow_decisions",
        }

        manifest_boundaries = set(manifest.get("must_not_own", []))
        missing_boundaries = sorted(required_boundaries - manifest_boundaries)
        if missing_boundaries:
            raise ValueError(
                "Missing must_not_own boundaries: " + ", ".join(missing_boundaries)
            )

        status = "OK"
        details = "Module manifest validation passed"

    except Exception as exc:
        status = "FAIL"
        details = str(exc)

    return CheckResult(
        name="Module manifest validation",
        expected_result="Manifest відповідає bootstrap-межам Gateway",
        status=status,
        duration_seconds=time.perf_counter() - started_at,
        command=None,
        details=details,
    )


def validate_routes() -> CheckResult:
    """Validate local placeholder routes configuration."""
    started_at = time.perf_counter()
    routes_path = PROJECT_ROOT / "app" / "forprint_integration_gateway" / "config" / "routes.yaml"

    try:
        if not routes_path.exists():
            raise FileNotFoundError("routes.yaml not found")

        routes = load_routes_from_yaml(routes_path)

        if not routes:
            raise ValueError("routes.yaml must contain at least one route")

        route_ids = [route.route_id for route in routes]
        duplicated_route_ids = sorted(
            route_id for route_id in set(route_ids) if route_ids.count(route_id) > 1
        )
        if duplicated_route_ids:
            raise ValueError("Duplicated route_id values: " + ", ".join(duplicated_route_ids))

        enabled_routes = [route for route in routes if route.enabled]
        if not enabled_routes:
            raise ValueError("routes.yaml must contain at least one enabled route")

        required_route_ids = {
            "crm_to_calculator_quote_recalculation",
            "crm_to_accounting_invoice_request",
            "crm_to_prepress_job_request",
            "customer_channel_to_crm_order_intake",
            "customer_channel_to_calculator_quote_preview",
            "calculator_to_crm_quote_result",
            "accounting_to_crm_invoice_status",
            "prepress_to_crm_prepress_status",
        }

        missing_route_ids = sorted(required_route_ids - set(route_ids))
        if missing_route_ids:
            raise ValueError("Missing placeholder routes: " + ", ".join(missing_route_ids))

        status = "OK"
        details = f"Routes validation passed: {len(routes)} route(s), {len(enabled_routes)} enabled"

    except Exception as exc:
        status = "FAIL"
        details = str(exc)

    return CheckResult(
        name="Routes validation",
        expected_result="Локальні placeholder routes валідні",
        status=status,
        duration_seconds=time.perf_counter() - started_at,
        command=None,
        details=details,
    )


def validate_gateway_boundaries_doc() -> CheckResult:
    """Validate that the local Gateway boundary document exists."""
    started_at = time.perf_counter()
    doc_path = PROJECT_ROOT / "docs" / "architecture" / "gateway_boundaries.md"

    try:
        if not doc_path.exists():
            raise FileNotFoundError("docs/architecture/gateway_boundaries.md not found")

        content = doc_path.read_text(encoding="utf-8")

        required_phrases = [
            "not a business brain",
            "Gateway must not answer",
            "Business workflow decisions belong to ForPrint CRM",
            "Gateway must stay channel-agnostic",
        ]

        missing_phrases = [phrase for phrase in required_phrases if phrase not in content]
        if missing_phrases:
            raise ValueError(
                "Boundary document misses required phrase(s): " + ", ".join(missing_phrases)
            )

        status = "OK"
        details = "Gateway boundary document validation passed"

    except Exception as exc:
        status = "FAIL"
        details = str(exc)

    return CheckResult(
        name="Gateway boundaries doc",
        expected_result="Документ меж Gateway існує і фіксує ключові заборони",
        status=status,
        duration_seconds=time.perf_counter() - started_at,
        command=None,
        details=details,
    )

def validate_v0_3_architecture_docs() -> CheckResult:
    """Validate v0.3 architecture documentation files."""
    started_at = time.perf_counter()

    try:
        required_docs = {
            PROJECT_ROOT
            / "docs"
            / "architecture"
            / "channel_intake_contracts_v0_3.md": [
                "Supported channel sources",
                "Supported request kinds",
                "No live runtime",
                "Gateway must not become a business brain",
            ],
            PROJECT_ROOT
            / "docs"
            / "architecture"
            / "operational_handoff_contracts_v0_3.md": [
                "Operational Registry handoff candidates",
                "is_live_write_enabled",
                "Gateway does not create",
                "It must not become the owner of operational truth",
            ],
        }

        for path, required_phrases in required_docs.items():
            if not path.exists():
                raise FileNotFoundError(
                    "Missing v0.3 architecture doc: "
                    + str(path.relative_to(PROJECT_ROOT))
                )

            content = path.read_text(encoding="utf-8")
            missing_phrases = [phrase for phrase in required_phrases if phrase not in content]

            if missing_phrases:
                raise ValueError(
                    f"{path.name} misses required phrase(s): "
                    + ", ".join(missing_phrases)
                )

        status = "OK"
        details = "v0.3 architecture documentation validation passed"

    except Exception as exc:
        status = "FAIL"
        details = str(exc)

    return CheckResult(
        name="v0.3 architecture docs",
        expected_result="Channel intake і operational handoff docs валідні",
        status=status,
        duration_seconds=time.perf_counter() - started_at,
        command=None,
        details=details,
    )

def build_terminal_table(results: list[CheckResult]) -> Table:
    """Build Rich terminal table."""
    table = Table(title="ForPrint Integration Gateway — check report")

    table.add_column("Перевірка", style="bold")
    table.add_column("Очікуваний результат")
    table.add_column("Статус", justify="center")
    table.add_column("Час", justify="right")

    for result in results:
        status_style = "green" if result.status == "OK" else "red"
        table.add_row(
            result.name,
            result.expected_result,
            f"[{status_style}]{result.status}[/{status_style}]",
            f"{result.duration_seconds:.2f}s",
        )

    return table


def write_json_report(results: list[CheckResult]) -> None:
    """Write machine-readable JSON report."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    payload: dict[str, Any] = {
        "project": "forprint_integration_gateway",
        "generated_at": utc_now_iso(),
        "overall_status": "OK" if all(result.status == "OK" for result in results) else "FAIL",
        "results": [asdict(result) for result in results],
    }

    JSON_REPORT_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def write_markdown_report(results: list[CheckResult]) -> None:
    """Write human-readable Markdown report."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    overall_status = "OK" if all(result.status == "OK" for result in results) else "FAIL"

    lines = [
        "# ForPrint Integration Gateway — check report",
        "",
        f"- Generated at: `{utc_now_iso()}`",
        f"- Overall status: `{overall_status}`",
        "",
        "| Перевірка | Очікуваний результат | Статус | Час |",
        "|---|---|---:|---:|",
    ]

    for result in results:
        lines.append(
            "| "
            f"{result.name} | "
            f"{result.expected_result} | "
            f"{result.status} | "
            f"{result.duration_seconds:.2f}s |"
        )

    lines.extend(
        [
            "",
            "## Details",
            "",
        ]
    )

    for result in results:
        lines.extend(
            [
                f"### {result.name}",
                "",
                f"- Status: `{result.status}`",
                f"- Expected: {result.expected_result}",
                f"- Duration: `{result.duration_seconds:.2f}s`",
            ]
        )

        if result.command:
            lines.append(f"- Command: `{result.command}`")

        if result.details:
            lines.extend(
                [
                    "",
                    "```text",
                    result.details,
                    "```",
                ]
            )

        lines.append("")

    MARKDOWN_REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    """Run all Gateway checks."""
    console = Console()

    console.print("🔎 Running ForPrint Integration Gateway checks...")

    results = [
		run_command_check(
			name="Ruff lint",
			expected_result="Немає lint-помилок у app/tests/scripts",
			command=[sys.executable, "-m", "ruff", "check", "app", "tests", "scripts"],
		),
		run_command_check(
			name="Pytest",
			expected_result="Усі тести проходять",
			command=[sys.executable, "-m", "pytest", "-q"],
		),
		run_command_check(
			name="Gateway smoke runner",
			expected_result="Локальний GatewayProcessor проходить smoke-сценарій",
			command=[sys.executable, "scripts/run_gateway_smoke.py"],
		),
        run_command_check(
            name="Channel intake preview",
            expected_result="v0.3 channel intake preview проходить offline-сценарії",
            command=[sys.executable, "scripts/run_channel_intake_preview.py"],
        ),
        run_command_check(
            name="Coordination records check",
            expected_result="v0.3 coordination records machine-clean і tracked",
            command=[sys.executable, "scripts/check_gateway_coordination_records.py"],
        ),
        run_command_check(
            name="Adapter contracts check",
            expected_result=
                "v0.4 adapter descriptors, error taxonomy " 
                "і offline retry policies валідні",
            command=[sys.executable, "scripts/check_gateway_adapter_contracts.py"],
        ),
        run_command_check(
            name="Adapter readiness preview",
            expected_result="v0.4 adapter readiness preview проходить offline-сценарії",
            command=[sys.executable, "scripts/run_adapter_readiness_preview.py"],
        ),
        run_command_check(
        name="Contract compatibility check",
        expected_result=(
            "v0.5 compatibility matrix, replay fixtures "
            "і dry-run planner валідні"
        ),
        command=[sys.executable, "scripts/check_gateway_contract_compatibility.py"],
        ),
        run_command_check(
            name="Compatibility matrix preview",
            expected_result="v0.5 compatibility matrix preview проходить",
            command=[sys.executable, "scripts/run_compatibility_matrix_preview.py"],
        ),
        run_command_check(
            name="Replay fixtures preview",
            expected_result="v0.5 replay fixtures preview проходить",
            command=[sys.executable, "scripts/run_replay_fixtures_preview.py"],
        ),
        run_command_check(
            name="Contract release check",
            expected_result="v0.6 release manifest і consumer bundles валідні",
            command=[sys.executable, "scripts/check_gateway_contract_release.py"],
        ),
        run_command_check(
            name="Contract release preview",
            expected_result="v0.6 contract release preview проходить",
            command=[sys.executable, "scripts/run_contract_release_preview.py"],
        ),
        run_command_check(
            name="Consumer acceptance preview",
            expected_result="v0.6 consumer acceptance fixtures проходять",
            command=[sys.executable, "scripts/run_consumer_acceptance_preview.py"],
        ),
        run_command_check(
            name="Backward compatibility preview",
            expected_result="v0.6 backward compatibility gates проходять",
            command=[sys.executable, "scripts/run_backward_compatibility_preview.py"],
        ),
		validate_examples_and_contract_fixtures(),
		validate_manifest(),
		validate_routes(),
		validate_gateway_boundaries_doc(),
        validate_v0_3_architecture_docs(),
	]

    for result in results:
        status_label = "OK" if result.status == "OK" else "FAIL"
        console.print(f"  - {result.name}: {status_label} ({result.duration_seconds:.2f}s)")

    console.print()
    console.print(build_terminal_table(results))

    write_json_report(results)
    write_markdown_report(results)

    console.print()
    console.print(f"📄 JSON report: {JSON_REPORT_PATH}")
    console.print(f"📄 Markdown report: {MARKDOWN_REPORT_PATH}")

    if all(result.status == "OK" for result in results):
        console.print("✅ Gateway check report completed successfully.")
        return 0

    console.print("❌ Gateway check report failed.")

    for result in results:
        if result.status != "OK":
            console.print()
            console.print(f"[red]Failure details for {result.name}:[/red]")
            console.print(result.details or "No details")

    return 1


if __name__ == "__main__":
    raise SystemExit(main())