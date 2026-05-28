from pathlib import Path

import yaml


def test_manifest_file_exists() -> None:
    project_root = Path(__file__).resolve().parents[1]
    manifest_path = project_root / "forprint_module_manifest.yaml"

    assert manifest_path.exists()


def test_manifest_has_correct_module_id() -> None:
    project_root = Path(__file__).resolve().parents[1]
    manifest_path = project_root / "forprint_module_manifest.yaml"

    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))

    assert manifest["module_id"] == "forprint_integration_gateway"


def test_manifest_has_bootstrap_status() -> None:
    project_root = Path(__file__).resolve().parents[1]
    manifest_path = project_root / "forprint_module_manifest.yaml"

    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))

    assert manifest["status"] == "bootstrap_development"


def test_manifest_contains_required_must_not_own_boundaries() -> None:
    project_root = Path(__file__).resolve().parents[1]
    manifest_path = project_root / "forprint_module_manifest.yaml"

    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))

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

    assert required_boundaries.issubset(set(manifest["must_not_own"]))