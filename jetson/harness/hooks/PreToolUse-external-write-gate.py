#!/usr/bin/env python3
"""
Hook: PreToolUse-external-write-gate
Event: PreToolUse
Purpose: Ask for explicit confirmation on writes outside the working directory.

Threat: foundation/02-architectural-principles.md Principle 3 (reversibility-
        weighted risk). Writes outside the working directory are not reversible
        from version control. Friction must match the reversibility class.

Decision: Mandatory deterministic enforcement of Principle 3. Not threat-elected
          in Phase 2; the principle is foundation-level (applies to every phase),
          not threat-elected (per-phase). Matches the Phase 3 prompt's explicit
          mandatory-hook list.

Verify (allow, inside cwd):
    echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"./local.txt\"},\"cwd\":\"$PWD\"}" | \
        python3 PreToolUse-external-write-gate.py
    # exit 0, empty stdout

Verify (ask, outside cwd):
    echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"/tmp/external.txt\"},\"cwd\":\"$PWD\"}" | \
        python3 PreToolUse-external-write-gate.py
    # exit 0, stdout: hookSpecificOutput with permissionDecision=ask

Owner: harness-engineering (Phase 3, 2026-05-11)
"""
import json
import os
import sys

WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}


def extract_path(tool_input: dict) -> str:
    for key in ("file_path", "notebook_path", "path"):
        v = tool_input.get(key)
        if v:
            return v
    return ""


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    if data.get("tool_name") not in WRITE_TOOLS:
        return 0
    tool_input = data.get("tool_input", {}) or {}
    raw_path = extract_path(tool_input)
    if not raw_path:
        return 0
    cwd = data.get("cwd") or os.getcwd()
    abs_cwd = os.path.abspath(cwd)
    if os.path.isabs(raw_path):
        abs_path = os.path.abspath(raw_path)
    else:
        abs_path = os.path.abspath(os.path.join(abs_cwd, raw_path))
    # Inside cwd if the common path with cwd equals cwd.
    try:
        common = os.path.commonpath([abs_path, abs_cwd])
    except ValueError:
        # Cross-drive on Windows or unrelated paths.
        common = ""
    if common == abs_cwd:
        return 0
    out = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": (
                f"Write target '{abs_path}' is outside the working directory "
                f"'{abs_cwd}'. Principle 3 (reversibility) requires explicit "
                f"confirmation."
            ),
        }
    }
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
