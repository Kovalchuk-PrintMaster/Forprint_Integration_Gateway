"""Read the active outgoing Blueprint prompt for this module."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

BLUEPRINT_ROOT = Path("/srv/software_development/forprint-project/forprint_system_blueprint")
MODULE_ID = "forprint_integration_gateway"
OUTGOING_PROMPTS_DIR = (
    BLUEPRINT_ROOT / "coordination" / "outgoing_prompts" / MODULE_ID
)
INDEX_PATH = OUTGOING_PROMPTS_DIR / "index.yaml"
READY_STATUS = "ready_for_module_pull"

SECTION_HEADERS = {
    "active_prompts:",
    "completed_prompts:",
    "review_notes:",
}


def load_index(path: Path) -> dict[str, Any]:
    """Load Blueprint outgoing prompt index.

    The preferred format is valid YAML.

    A fallback parser is intentionally kept here because Blueprint index files
    may temporarily contain flat prompt records or non-indented block text while
    coordination records are being fixed.
    """
    text = path.read_text(encoding="utf-8")

    try:
        loaded = yaml.safe_load(text) or {}
        if isinstance(loaded, dict):
            return loaded
    except yaml.YAMLError:
        return parse_flat_index_fallback(text)

    return {}


def parse_flat_index_fallback(text: str) -> dict[str, Any]:
    """Parse a temporarily malformed flat Blueprint prompt index.

    This supports the observed shape:

    active_prompts:

    prompt_id: ...
    status: ready_for_module_pull
    file: ...
    target_module: ...
    phase: ...
    priority: ...

    completed_prompts:

    note: >
    Non-indented note text...
    """
    index_data: dict[str, Any] = {"active_prompts": []}
    current_section: str | None = None
    active_prompt: dict[str, Any] = {}

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        if line in SECTION_HEADERS:
            current_section = line.removesuffix(":")
            continue

        if current_section != "active_prompts":
            continue

        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"')

        if key in {
            "prompt_id",
            "status",
            "file",
            "target_module",
            "phase",
            "priority",
        }:
            active_prompt[key] = value

    if active_prompt:
        index_data["active_prompts"].append(active_prompt)

    return index_data


def normalize_prompt_records(index_data: dict[str, Any]) -> list[dict[str, Any]]:
    """Normalize supported Blueprint outgoing prompt index shapes."""
    active_prompts = index_data.get("active_prompts")

    if isinstance(active_prompts, list):
        return [prompt for prompt in active_prompts if isinstance(prompt, dict)]

    if isinstance(active_prompts, dict):
        return [active_prompts]

    flat_prompt_keys = {
        "prompt_id",
        "status",
        "file",
        "target_module",
        "phase",
        "priority",
    }

    if flat_prompt_keys.intersection(index_data):
        return [index_data]

    return []


def find_ready_prompt(index_data: dict[str, Any]) -> dict[str, Any] | None:
    """Find the first ready outgoing prompt for the module."""
    for prompt in normalize_prompt_records(index_data):
        if prompt.get("status") != READY_STATUS:
            continue

        if prompt.get("target_module") not in {None, MODULE_ID}:
            continue

        return prompt

    return None


def resolve_prompt_path(prompt: dict[str, Any]) -> Path:
    """Resolve prompt file path from index record."""
    prompt_file = prompt.get("file")
    if not prompt_file:
        raise ValueError("Ready prompt record does not contain 'file'")

    path = Path(str(prompt_file))

    if path.is_absolute():
        return path

    return OUTGOING_PROMPTS_DIR / path


def print_prompt(prompt: dict[str, Any], prompt_path: Path) -> None:
    """Print outgoing prompt header and content."""
    print("=" * 80)
    print("FORPRINT BLUEPRINT OUTGOING PROMPT")
    print("=" * 80)
    print(f"module: {MODULE_ID}")
    print(f"prompt_id: {prompt.get('prompt_id')}")
    print(f"status: {prompt.get('status')}")
    print(f"file: {prompt_path}")
    print("=" * 80)
    print()
    print(prompt_path.read_text(encoding="utf-8"))


def main() -> int:
    """Read and print the active ready outgoing prompt."""
    if not INDEX_PATH.exists():
        print("NO OUTGOING PROMPT INDEX")
        print(f"Index: {INDEX_PATH}")
        return 1

    raw_index_text = INDEX_PATH.read_text(encoding="utf-8")

    try:
        loaded = yaml.safe_load(raw_index_text) or {}
        index_data = loaded if isinstance(loaded, dict) else {}
    except yaml.YAMLError:
        index_data = parse_flat_index_fallback(raw_index_text)

    prompt = find_ready_prompt(index_data)

    if prompt is None:
        # Some Blueprint prompt indexes are syntactically valid YAML but use
        # duplicate flat top-level keys. In that case PyYAML keeps the last
        # duplicate key and loses the active prompt. The raw-text fallback keeps
        # the active_prompts section boundaries and finds the intended prompt.
        fallback_index_data = parse_flat_index_fallback(raw_index_text)
        prompt = find_ready_prompt(fallback_index_data)

    if prompt is None:
        print("NO READY OUTGOING PROMPTS")
        print(f"Index: {INDEX_PATH}")
        return 1

    prompt_path = resolve_prompt_path(prompt)

    if not prompt_path.exists():
        print("READY PROMPT FILE NOT FOUND")
        print(f"Prompt file: {prompt_path}")
        return 1

    print_prompt(prompt, prompt_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())