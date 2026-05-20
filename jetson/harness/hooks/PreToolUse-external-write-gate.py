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

Exemption: Claude Code's own managed, regenerable write stores are exempt as a
           class. These are written on most sessions as part of normal operation,
           are not project source, and are not irreversible in the Principle 3
           sense. Gating them produces high-frequency prompts that train
           reflexive approval and erode the gate's signal for writes that
           matter. The class today:
             1. Auto-memory: ~/.claude/projects/<encoded-cwd>/memory/...
             2. Plan files: ~/.claude/plans/...
           Everything else under ~/.claude/ stays gated (settings.json, mcp.json,
           hooks/, skills/, agents/, CLAUDE.md, audited-hashes.json, etc.).
           Custom plansDirectory or autoMemoryDirectory overrides outside these
           default paths are not auto-detected; if you set them, extend
           is_claude_code_managed_store accordingly.

Verify (allow, inside cwd):
    echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"./local.txt\"},\"cwd\":\"$PWD\"}" | \
        python3 PreToolUse-external-write-gate.py
    # exit 0, empty stdout

Verify (ask, outside cwd):
    echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"/tmp/external.txt\"},\"cwd\":\"$PWD\"}" | \
        python3 PreToolUse-external-write-gate.py
    # exit 0, stdout: hookSpecificOutput with permissionDecision=ask

Verify (allow, auto-memory store):
    echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$HOME/.claude/projects/x/memory/MEMORY.md\"},\"cwd\":\"$PWD\"}" | \
        python3 PreToolUse-external-write-gate.py
    # exit 0, empty stdout

Verify (allow, plan file):
    echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$HOME/.claude/plans/foo.md\"},\"cwd\":\"$PWD\"}" | \
        python3 PreToolUse-external-write-gate.py
    # exit 0, empty stdout

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


def is_claude_code_managed_store(abs_path: str, home: str) -> bool:
    # Class: Claude Code's own managed, regenerable write stores. See the
    # Exemption note in the module header. Today: auto-memory under
    # ~/.claude/projects/<encoded-cwd>/memory/ and plan files under
    # ~/.claude/plans/. Everything else under ~/.claude/ stays gated.
    claude_root = os.path.join(home, ".claude")
    # Plan files: ~/.claude/plans/... (Claude Code default plansDirectory).
    plans_root = os.path.join(claude_root, "plans")
    if abs_path == plans_root or abs_path.startswith(plans_root + os.sep):
        return True
    # Auto-memory: ~/.claude/projects/<one-segment>/memory/...
    projects_root = os.path.join(claude_root, "projects")
    if abs_path.startswith(projects_root + os.sep):
        rel = os.path.relpath(abs_path, projects_root)
        parts = rel.split(os.sep)
        if len(parts) >= 2 and parts[1] == "memory":
            return True
    return False


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
    home = os.path.expanduser("~")
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
    if is_claude_code_managed_store(abs_path, home):
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
