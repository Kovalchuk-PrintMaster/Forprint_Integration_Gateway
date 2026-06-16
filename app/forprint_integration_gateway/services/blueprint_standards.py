"""Blueprint standards visibility helpers for Gateway v0.7."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_BLUEPRINT_ROOT = PROJECT_ROOT.parent / "forprint_system_blueprint"

STANDARDS_INDEX_RELATIVE_PATH = Path("coordination/standards/index.yaml")
SNAPSHOT_PATH = PROJECT_ROOT / "coordination" / "standards" / "blueprint_standards_snapshot.yaml"

REQUIRED_REVIEWED_STANDARDS = [
    "coordination/standards/index.yaml",
    "coordination/standards/module_standards_awareness_protocol.md",
    "coordination/standards/module_governance_protocol.md",
    "coordination/standards/module_make_target_contract.md",
]

ADVISORY_ALIGNMENT_NOTES = [
    "Gateway added standards visibility without forcing full compliance.",
    "Standards remain advisory unless activated by prompt/directive.",
    "No destructive refactor was performed.",
]

ADVISORY_KEYWORDS = {
    "advisory",
    "gradual",
    "visibility",
    "awareness",
    "prompt",
    "directive",
    "non-destructive",
    "not automatic",
    "unless activated",
}


class BlueprintStandardsError(RuntimeError):
    """Raised when Blueprint standards visibility validation fails."""


@dataclass(frozen=True)
class BlueprintStandardRecord:
    """Normalized Blueprint standard index record."""

    standard_id: str
    path: str
    status: str
    adoption_mode: str


def get_blueprint_root() -> Path:
    """Return configured Blueprint repository root."""
    return DEFAULT_BLUEPRINT_ROOT


def load_yaml(path: Path) -> dict[str, Any]:
    """Load YAML mapping."""
    if not path.exists():
        raise BlueprintStandardsError(f"Missing file: {path}")

    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))

    if not isinstance(loaded, dict):
        raise BlueprintStandardsError(f"YAML root must be mapping: {path}")

    return loaded


def _pick_string(data: dict[str, Any], keys: tuple[str, ...], default: str = "") -> str:
    """Pick first non-empty string value."""
    for key in keys:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return default


def normalize_standard_record(raw: dict[str, Any]) -> BlueprintStandardRecord:
    """Normalize one standard index entry."""
    standard_id = _pick_string(
        raw,
        ("standard_id", "id", "name", "standard"),
        default="unknown_standard",
    )
    path = _pick_string(
        raw,
        ("file", "path", "document", "standard_file"),
        default="",
    )
    status = _pick_string(raw, ("status",), default="unknown")
    adoption_mode = _pick_string(
        raw,
        ("adoption_mode", "mode", "enforcement", "semantics"),
        default="advisory",
    )

    return BlueprintStandardRecord(
        standard_id=standard_id,
        path=path,
        status=status,
        adoption_mode=adoption_mode,
    )


def load_standards_index() -> dict[str, Any]:
    """Load Blueprint standards index."""
    blueprint_root = get_blueprint_root()
    return load_yaml(blueprint_root / STANDARDS_INDEX_RELATIVE_PATH)

def resolve_standard_path(standard_path: str) -> Path:
    """Resolve standard path from Blueprint standards index.

    Blueprint standards index stores paths relative to coordination/standards.
    Some legacy entries may still be relative to Blueprint root, so we support both.
    """
    blueprint_root = get_blueprint_root()
    raw_path = Path(standard_path)

    if raw_path.is_absolute():
        return raw_path

    standards_dir_path = blueprint_root / STANDARDS_INDEX_RELATIVE_PATH.parent / raw_path
    if standards_dir_path.exists():
        return standards_dir_path

    blueprint_root_path = blueprint_root / raw_path
    if blueprint_root_path.exists():
        return blueprint_root_path

    return standards_dir_path

def list_blueprint_standards() -> list[BlueprintStandardRecord]:
    """List normalized standards from Blueprint standards index."""
    index = load_standards_index()

    raw_standards = index.get("standards")
    if raw_standards is None:
        raw_standards = index.get("items", [])

    if not isinstance(raw_standards, list):
        raise BlueprintStandardsError("Blueprint standards index must contain standards list")

    standards: list[BlueprintStandardRecord] = []
    for raw in raw_standards:
        if not isinstance(raw, dict):
            raise BlueprintStandardsError("Each standards index entry must be mapping")
        standards.append(normalize_standard_record(raw))

    return standards


def _read_optional_text(path: Path) -> str:
    """Read optional text file."""
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def validate_blueprint_standards_visibility() -> list[str]:
    """Validate advisory standards visibility without enforcing full compliance."""
    errors: list[str] = []
    blueprint_root = get_blueprint_root()

    if not blueprint_root.exists():
        errors.append(f"Blueprint root does not exist: {blueprint_root}")
        return errors

    index_path = blueprint_root / STANDARDS_INDEX_RELATIVE_PATH
    if not index_path.exists():
        errors.append(f"Blueprint standards index missing: {index_path}")
        return errors

    try:
        standards = list_blueprint_standards()
    except BlueprintStandardsError as exc:
        errors.append(str(exc))
        return errors

    if not standards:
        errors.append("Blueprint standards index has no standards")

    for standard in standards:
        if not standard.path:
            errors.append(f"{standard.standard_id}: missing file path")
            continue

        standard_path = resolve_standard_path(standard.path)
        if not standard_path.exists():
            errors.append(f"{standard.standard_id}: referenced file missing: {standard.path}")

    awareness_text = _read_optional_text(
        resolve_standard_path("module_standards_awareness_protocol.md")
    ).lower()
    index_text = index_path.read_text(encoding="utf-8").lower()
    combined_text = awareness_text + "\n" + index_text

    if not any(keyword in combined_text for keyword in ADVISORY_KEYWORDS):
        errors.append("Advisory standards semantics are not explicit enough")

    hard_enforcement_markers = [
        "standards_alone_are_mandatory: true",
        "hard_enforcement_by_default: true",
        "destructive_refactor_by_default: true",
    ]

    for marker in hard_enforcement_markers:
        if marker in combined_text:
            errors.append(f"Hard enforcement marker is not allowed: {marker}")

    return errors


def build_standards_snapshot() -> dict[str, Any]:
    """Build lightweight Gateway standards visibility snapshot."""
    index = load_standards_index()
    standards = list_blueprint_standards()
    blueprint_root = get_blueprint_root()

    index_version = (
        index.get("version")
        or index.get("standards_index_version")
        or index.get("updated_at")
        or "unknown"
    )

    return {
        "snapshot_id": "gateway_blueprint_standards_snapshot_v0_7",
        "module_id": "forprint_integration_gateway",
        "source_blueprint_path": str(blueprint_root),
        "snapshot_timestamp": datetime.now(UTC).isoformat(),
        "standards_index_path": str(STANDARDS_INDEX_RELATIVE_PATH),
        "standards_index_version": str(index_version),
        "standards_count": len(standards),
        "reviewed_standards": [
            {
                "standard_id": standard.standard_id,
                "file": standard.path,
                "status": standard.status,
                "adoption_mode": standard.adoption_mode,
            }
            for standard in standards
        ],
        "required_reviewed_standards": REQUIRED_REVIEWED_STANDARDS,
        "advisory_semantics_confirmation": {
            "standards_are_advisory_by_default": True,
            "prompts_define_concrete_work_now": True,
            "directives_are_mandatory_when_explicitly_active": True,
            "global_policy_defines_ecosystem_constraints": True,
            "no_hard_enforcement_implied_by_standards_alone": True,
            "no_destructive_refactor_from_standards_alone": True,
        },
        "gateway_specific_alignment_notes": ADVISORY_ALIGNMENT_NOTES,
    }


def write_standards_snapshot() -> Path:
    """Write local standards visibility snapshot."""
    SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = build_standards_snapshot()
    SNAPSHOT_PATH.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return SNAPSHOT_PATH


def validate_standards_snapshot() -> list[str]:
    """Validate local standards snapshot."""
    errors: list[str] = []

    if not SNAPSHOT_PATH.exists():
        errors.append(f"Missing standards snapshot: {SNAPSHOT_PATH.relative_to(PROJECT_ROOT)}")
        return errors

    try:
        snapshot = load_yaml(SNAPSHOT_PATH)
    except BlueprintStandardsError as exc:
        return [str(exc)]

    expected_values = {
        "snapshot_id": "gateway_blueprint_standards_snapshot_v0_7",
        "module_id": "forprint_integration_gateway",
    }

    for key, expected in expected_values.items():
        actual = snapshot.get(key)
        if actual != expected:
            errors.append(f"snapshot {key}={actual!r}, expected {expected!r}")

    confirmation = snapshot.get("advisory_semantics_confirmation")
    if not isinstance(confirmation, dict):
        errors.append("snapshot advisory_semantics_confirmation must be mapping")
    else:
        for key, value in confirmation.items():
            if value is not True:
                errors.append(f"snapshot advisory confirmation {key} must be true")

    notes = snapshot.get("gateway_specific_alignment_notes")
    if not isinstance(notes, list):
        errors.append("snapshot gateway_specific_alignment_notes must be list")
    else:
        for note in ADVISORY_ALIGNMENT_NOTES:
            if note not in notes:
                errors.append(f"snapshot missing alignment note: {note}")

    reviewed = snapshot.get("reviewed_standards")
    if not isinstance(reviewed, list) or not reviewed:
        errors.append("snapshot reviewed_standards must be non-empty list")

    return errors


def validate_blueprint_standards_ready() -> list[str]:
    """Validate standards visibility and snapshot readiness."""
    errors: list[str] = []
    errors.extend(validate_blueprint_standards_visibility())
    errors.extend(validate_standards_snapshot())
    return errors