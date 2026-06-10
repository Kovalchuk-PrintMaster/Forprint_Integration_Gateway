from __future__ import annotations

from pathlib import Path


BLUEPRINT_ROOT = Path("/srv/software_development/forprint-project/forprint_system_blueprint")
MODULE_ID = "forprint_integration_gateway"

INDEX_PATH = BLUEPRINT_ROOT / "coordination/outgoing_prompts" / MODULE_ID / "index.yaml"


def _parse_simple_prompt_index(content: str) -> list[dict[str, str]]:
    prompts: list[dict[str, str]] = []
    current: dict[str, str] | None = None

    for raw_line in content.splitlines():
        line = raw_line.strip()

        if line.startswith("- prompt_id:"):
            if current:
                prompts.append(current)
            current = {"prompt_id": line.split(":", 1)[1].strip().strip('"')}

        elif current is not None and ":" in line:
            key, value = line.split(":", 1)
            current[key.strip()] = value.strip().strip('"')

    if current:
        prompts.append(current)

    return prompts


def main() -> int:
    if not INDEX_PATH.exists():
        print(f"NO OUTGOING PROMPT INDEX: {INDEX_PATH}")
        return 1

    index_content = INDEX_PATH.read_text(encoding="utf-8")
    prompts = _parse_simple_prompt_index(index_content)

    ready_prompts = [
        prompt for prompt in prompts
        if prompt.get("status") == "ready_for_module_pull"
    ]

    if not ready_prompts:
        print("NO READY OUTGOING PROMPTS")
        print(f"Index: {INDEX_PATH}")
        return 0

    prompt = ready_prompts[0]
    prompt_file = prompt.get("file")

    if not prompt_file:
        print("READY PROMPT HAS NO FILE FIELD")
        print(f"Prompt: {prompt}")
        return 1

    prompt_path = INDEX_PATH.parent / prompt_file

    if not prompt_path.exists():
        print(f"PROMPT FILE NOT FOUND: {prompt_path}")
        return 1

    print("=" * 80)
    print("FORPRINT BLUEPRINT OUTGOING PROMPT")
    print("=" * 80)
    print(f"module: {MODULE_ID}")
    print(f"prompt_id: {prompt.get('prompt_id', '-')}")
    print(f"status: {prompt.get('status', '-')}")
    print(f"file: {prompt_path}")
    print("=" * 80)
    print()
    print(prompt_path.read_text(encoding="utf-8"))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
