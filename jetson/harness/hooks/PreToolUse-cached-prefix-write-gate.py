#!/usr/bin/env python3
"""
Hook: PreToolUse-cached-prefix-write-gate
Event: PreToolUse (Phase 2 Q2a wrote PostToolUse; see PHASE-3-NOTES.md §Deviations)
Purpose: Ask for confirmation on writes to cached-prefix files (CLAUDE.md
         hierarchy, the foundation/ documents cited from it, and user-level
         @import targets in ~/.claude/).

Threat: foundation/01-threat-model.md Threat actors #5 (cache poisoning of the
        prefix). Text landed in the cached prefix becomes persistent influence
        over every future session.

Decision: Phase 2 Q2a elected T5 hook. Phase 3 implements as PreToolUse rather
          than PostToolUse: PostToolUse fires after the write has landed,
          providing audit but not gating. The Phase 2 intent ('requires
          explicit confirmation') is gating, which only PreToolUse delivers.

Verify (allow):
    echo "{\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"./README.md\"},\"cwd\":\"$PWD\"}" | \
        python3 PreToolUse-cached-prefix-write-gate.py
    # exit 0, empty stdout

Verify (ask, project CLAUDE.md):
    echo "{\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"./CLAUDE.md\"},\"cwd\":\"$PWD\"}" | \
        python3 PreToolUse-cached-prefix-write-gate.py
    # exit 0, stdout: permissionDecision=ask

Verify (ask, ~/.claude/CLAUDE.md):
    echo "{\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"$HOME/.claude/CLAUDE.md\"},\"cwd\":\"$PWD\"}" | \
        python3 PreToolUse-cached-prefix-write-gate.py
    # exit 0, stdout: permissionDecision=ask

Owner: harness-engineering (Phase 3, 2026-05-11)
"""
import json
import os
import re
import sys

WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}

# User-level @import targets currently loaded by ~/.claude/CLAUDE.md
# (per Phase 1 inventory, Section 1). Any file matching one of these patterns
# inside ~/.claude/ is cached-prefix material.
USER_LEVEL_PATTERNS = [
    re.compile(r"^[A-Z]+\.md$"),       # FLAGS.md, RULES.md, PRINCIPLES.md
    re.compile(r"^MODE_[A-Za-z_]+\.md$"),
    re.compile(r"^MCP_[A-Za-z0-9]+\.md$"),
    re.compile(r"^CLAUDE\.md$"),
]


def is_cached_prefix_file(abs_path: str, abs_cwd: str, home: str) -> bool:
    basename = os.path.basename(abs_path)
    # Any CLAUDE.md anywhere in the project tree under cwd.
    if basename == "CLAUDE.md" and abs_path.startswith(abs_cwd + os.sep):
        return True
    # foundation/ documents (cited extensively from project root CLAUDE.md
    # and from skill bodies; participate in the cache prefix when loaded).
    foundation_dir = os.path.join(abs_cwd, "foundation") + os.sep
    if abs_path.startswith(foundation_dir):
        return True
    # User-level @import targets in $HOME/.claude
    user_claude = os.path.join(home, ".claude")
    if os.path.dirname(abs_path) == user_claude:
        for pat in USER_LEVEL_PATTERNS:
            if pat.match(basename):
                return True
    return False


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
    home = os.path.expanduser("~")
    abs_cwd = os.path.abspath(cwd)
    if os.path.isabs(raw_path):
        abs_path = os.path.abspath(raw_path)
    else:
        abs_path = os.path.abspath(os.path.join(abs_cwd, raw_path))
    if not is_cached_prefix_file(abs_path, abs_cwd, home):
        return 0
    out = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": (
                f"Write target '{abs_path}' is in the Claude Code cached "
                f"prefix. Cache-poisoning concerns (foundation/01 #5, "
                f"Phase 2 Q2a) require explicit confirmation."
            ),
        }
    }
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
