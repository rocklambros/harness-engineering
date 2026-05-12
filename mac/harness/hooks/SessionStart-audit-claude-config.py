#!/usr/bin/env python3
"""
Hook: SessionStart-audit-claude-config
Event: SessionStart
Purpose: Block sessions that load an unaudited .claude/settings.json,
         .claude/settings.local.json, or .mcp.json from the working directory.

Threat: foundation/01-threat-model.md Threat actors #3 (pre-trust initialization,
        CVE-2025-59536 / CVE-2026-21852 class). Code in .claude/settings.json
        and .mcp.json executes during project initialization before the trust
        dialog appears.

Decision: Phase 2 Q2b elected T3 hook. Phase 2 Q5 elected every-clone hash-gated
          cadence: every change to a candidate file requires re-audit. The
          audited-hash registry lives at ~/.claude/audited-hashes.json. The
          hook does not auto-acknowledge; an unaudited file blocks the session
          with stderr + additionalContext until Rock adds the hash manually.

Registry format:
    {
      "<sha256-hex>": {
        "path": "<absolute-path-at-audit-time>",
        "audited_at": "YYYY-MM-DD",
        "auditor": "<username>",
        "note": "<optional context>"
      },
      ...
    }

The 44 in-repo .claude/ directories Phase 1 surveyed need bulk acknowledgment.
scripts/audit-claude-config.sh (post-launch revision 2026-05-12) is the CLI
for that workflow. It walks cwd, computes hashes, prompts for audit notes,
and appends to the registry. Run with --auto-note for scripted bulk
additions. Manual registry edits remain available for inspection-heavy
cases.

Verify (no candidates, exit 0):
    echo '{"cwd":"/tmp/empty-test-dir","session_id":"test"}' | \
        python3 SessionStart-audit-claude-config.py
    # exit 0, empty stdout

Verify (unaudited candidate, exit 2):
    mkdir -p /tmp/unaudited/.claude && echo '{"a":1}' > /tmp/unaudited/.claude/settings.json
    echo '{"cwd":"/tmp/unaudited","session_id":"test"}' | \
        python3 SessionStart-audit-claude-config.py
    # exit 2, stderr with audit instructions, stdout with additionalContext

Owner: harness-engineering (Phase 3, 2026-05-11)
"""
import hashlib
import json
import os
import sys
from pathlib import Path

REGISTRY_PATH = Path(os.path.expanduser("~")) / ".claude" / "audited-hashes.json"
CANDIDATE_RELPATHS = [
    Path(".claude") / "settings.json",
    Path(".claude") / "settings.local.json",
    Path(".mcp.json"),
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_registry() -> dict:
    if not REGISTRY_PATH.exists():
        return {}
    try:
        with REGISTRY_PATH.open("r") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    cwd = Path(data.get("cwd") or os.getcwd())
    candidates = []
    for relpath in CANDIDATE_RELPATHS:
        p = cwd / relpath
        if p.is_file():
            candidates.append(p)
    if not candidates:
        return 0
    registry = load_registry()
    unaudited = []
    for p in candidates:
        try:
            digest = sha256_file(p)
        except OSError:
            continue
        if digest not in registry:
            unaudited.append((str(p), digest))
    if not unaudited:
        return 0
    lines = [
        "AUDIT REQUIRED. The following .claude/ config files in the working "
        "directory have not been audited (pre-trust initialization defense; "
        "foundation/01 Threat actors #3, Phase 2 Q5 every-clone cadence):",
        "",
    ]
    for path, digest in unaudited:
        lines.append(f"  {path}")
        lines.append(f"    sha256 {digest}")
    lines.append("")
    lines.append(
        f"Review each file's contents before continuing. To audit, add the "
        f"hash to {REGISTRY_PATH} with the registry entry format documented "
        f"in the hook header."
    )
    msg = "\n".join(lines)
    out = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": msg,
        }
    }
    print(json.dumps(out))
    # SessionStart blocking semantics depend on Claude Code version. Exit code 2
    # is the conventional non-zero block-with-stderr signal. The additionalContext
    # is the durable defense: visible to the model on session start regardless
    # of how the exit code is handled by the runtime.
    print(msg, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
