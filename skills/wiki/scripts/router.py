#!/usr/bin/env python3
"""
Second Brain deterministic routing script.
Parses subcommands, selects knowledge base, outputs path variables so the LLM can skip routing and enter workflows directly.

Usage:
    python router.py ingest
    python router.py ingest paper.pdf
    python router.py query "What is Memex?"
    python router.py lint
    python router.py wipe all
    python router.py init
    python router.py help

Output JSON:
    {
        "status": "ok",
        "subcommand": "ingest",
        "args": "paper.pdf",
        "workflow": "workflows/ingest.md",
        "schema": "SCHEMA.md",
        "kb": {
            "id": "ai-research",
            "name": "AI Research",
            "root": "/path/to/kb",
            "wiki": "/path/to/kb/wiki",
            "raw": "/path/to/kb/raw",
            "lang": "en"
        }
    }

When multiple knowledge bases exist, outputs status=select with a candidate list for the LLM to ask the user.
"""

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REGISTRIES_FILE = SKILL_DIR / "registries.json"

VALID_SUBCOMMANDS = {"init", "ingest", "query", "lint", "wipe", "test", "help"}

# Subcommands that do not require KB selection
NO_KB_REQUIRED = {"init", "help"}

# Subcommands that need SCHEMA.md (create/modify wiki pages)
NEEDS_SCHEMA = {"ingest", "query", "lint", "wipe"}


def load_registries() -> dict:
    if not REGISTRIES_FILE.exists():
        return {"default": None, "registries": {}}
    with open(REGISTRIES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("registries.json must be a JSON object")
    if "registries" in data and not isinstance(data["registries"], dict):
        raise ValueError("registries.json 'registries' field must be an object")
    return data


def validate_registry_entry(kb_id: str, kb_data: object) -> str | None:
    """Return error message if entry is invalid, else None."""
    if not isinstance(kb_data, dict):
        return f"Registry entry '{kb_id}' must be an object"
    name = kb_data.get("name")
    path = kb_data.get("path")
    if not isinstance(name, str) or not name.strip():
        return f"Registry entry '{kb_id}': 'name' must be a non-empty string"
    if not isinstance(path, str) or not path.strip():
        return f"Registry entry '{kb_id}': 'path' must be a non-empty string"
    return None


def validate_kb_path(path_str: str) -> tuple[Path | None, str | None]:
    """Resolve KB path to absolute and reject traversal. Returns (path, error)."""
    if ".." in Path(path_str).parts:
        return None, f"Knowledge base path must not contain '..': {path_str}"
    try:
        resolved = Path(path_str).expanduser().resolve()
    except (OSError, RuntimeError) as exc:
        return None, f"Invalid knowledge base path: {path_str} ({exc})"
    if not resolved.is_absolute():
        return None, f"Knowledge base path must resolve to an absolute path: {path_str}"
    if ".." in resolved.parts:
        return None, f"Knowledge base path contains path traversal: {path_str}"
    return resolved, None


def validate_registries(registries: dict) -> dict | None:
    """Validate registries structure and paths. Return error dict or None."""
    kbs = registries.get("registries", {})
    if not isinstance(kbs, dict):
        return {
            "status": "error",
            "message": "registries.json 'registries' field must be an object",
            "skill_dir": str(SKILL_DIR),
        }
    for kb_id, kb_data in kbs.items():
        if err := validate_registry_entry(kb_id, kb_data):
            return {"status": "error", "message": err, "skill_dir": str(SKILL_DIR)}
        _, path_err = validate_kb_path(kb_data["path"])
        if path_err:
            return {"status": "error", "message": path_err, "skill_dir": str(SKILL_DIR)}
    return None


def make_kb_info(kb_id: str, kb_data: dict) -> dict:
    root_path, _ = validate_kb_path(kb_data["path"])
    root = str(root_path)
    return {
        "id": kb_id,
        "name": kb_data["name"],
        "root": root,
        "wiki": f"{root}/wiki",
        "raw": f"{root}/raw",
        "lang": kb_data.get("language", "en"),
    }


def route(args: list[str]) -> dict:
    # Parse subcommand
    if not args:
        return {
            "status": "ok",
            "subcommand": "help",
            "args": "",
            "workflow": None,
            "schema": None,
            "kb": None,
            "skill_dir": str(SKILL_DIR),
        }

    subcommand = args[0].lower()
    remaining = " ".join(args[1:]) if len(args) > 1 else ""

    if subcommand not in VALID_SUBCOMMANDS:
        return {
            "status": "error",
            "message": f"Unknown subcommand: {subcommand}",
            "valid_subcommands": sorted(VALID_SUBCOMMANDS),
            "skill_dir": str(SKILL_DIR),
        }

    result = {
        "status": "ok",
        "subcommand": subcommand,
        "args": remaining,
        "workflow": f"workflows/{subcommand}.md" if subcommand not in ("help",) else None,
        "schema": "SCHEMA.md" if subcommand in NEEDS_SCHEMA else None,
        "kb": None,
        "skill_dir": str(SKILL_DIR),
    }

    # help and init do not need KB selection
    if subcommand in NO_KB_REQUIRED:
        return result

    # Commands that need KB selection
    try:
        registries = load_registries()
    except (json.JSONDecodeError, ValueError) as exc:
        return {
            "status": "error",
            "message": f"Invalid registries.json: {exc}",
            "skill_dir": str(SKILL_DIR),
        }

    if err := validate_registries(registries):
        return err

    kbs = registries.get("registries", {})

    if not kbs:
        return {
            "status": "no_kb",
            "message": "No knowledge base registered yet. Run /wiki init to create one first.",
            "skill_dir": str(SKILL_DIR),
        }

    if len(kbs) == 1:
        # Single KB — auto-select
        kb_id = next(iter(kbs))
        kb_data = kbs[kb_id]

        # Verify path exists
        root, path_err = validate_kb_path(kb_data["path"])
        if path_err:
            return {
                "status": "error",
                "message": path_err,
                "skill_dir": str(SKILL_DIR),
            }
        if not root.exists():
            return {
                "status": "error",
                "message": f"Knowledge base path does not exist: {root}",
                "skill_dir": str(SKILL_DIR),
            }

        result["kb"] = make_kb_info(kb_id, kb_data)
        return result

    # Multiple KBs — check for default
    default_id = registries.get("default")
    if default_id and default_id in kbs:
        # Use default KB but inform the LLM
        result["kb"] = make_kb_info(default_id, kbs[default_id])
        result["multiple_kbs"] = True
        result["kb_list"] = [
            {"id": kid, "name": kd["name"], "path": kd["path"], "is_default": kid == default_id}
            for kid, kd in kbs.items()
        ]
        return result

    # Multiple KBs with no default — LLM must ask user
    result["status"] = "select"
    result["message"] = "Multiple knowledge bases found. Ask the user to choose."
    result["kb_list"] = [
        {"id": kid, "name": kd["name"], "path": kd["path"]}
        for kid, kd in kbs.items()
    ]
    return result


def main():
    result = route(sys.argv[1:])
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
