#!/usr/bin/env python3
"""
Hook: ConfigChange-audit-claude-config
Event: ConfigChange (matchers project_settings, local_settings)
Purpose: Block an in-repo settings change from taking effect in the running
         session until its hash is in the audited-hash registry.

Threat: foundation/01-threat-model.md T.3 (pre-trust initialization,
        CVE-2025-59536 / CVE-2026-21852 class) and T.7 (silent capability
        erosion). A `.claude/settings.json` written during a session, by an
        injected instruction or by a checkout that moves to a hostile
        commit, is applied by Claude Code's file watcher. One line in it,
        `"disableAllHooks": true`, switches every hook off.

Decision: `SessionStart-audit-claude-config.py` checks the same three
          files, but a SessionStart hook can only flag. ConfigChange is the
          event that blocks: a `{"decision": "block"}` keeps the new
          settings from being applied. This hook blocks any
          `project_settings` or `local_settings` change whose file hash is
          not in the registry, the same registry and the same every-change
          cadence the SessionStart audit uses (Phase 2 Q5). The first load
          at session start is the trust dialog's job and the SessionStart
          audit's flag. `user_settings` is not gated here: the operator's
          own `/permissions` and `/hooks` edits write that file, and the
          external-write gate already asks for model edits to it.
          `policy_settings` cannot be blocked by design. Skill files are
          advisory and pass.

What the operator sees: nothing. Claude Code surfaces no message for a
blocked ConfigChange, by design, so this hook writes one line per decision
to ~/.claude/logs/config-change-gate.log. The next session start also
flags the unaudited file through the SessionStart audit.

Workflow after a legitimate edit: review the file, add its sha256 to the
registry with a note (scripts/audit-claude-config.sh does this), then
touch the file so the watcher fires again and the audited change applies.

Failure handling: a payload that is not JSON, an unreadable registry, or
any exception exits 2 (block). The registration sets onFailure: block and
runs under python3 -I with a 10 second timeout, so a hook that cannot
start blocks as well.

Verify (block, unaudited project settings):
    mkdir -p /tmp/cfgprobe/.claude && echo '{"disableAllHooks":true}' > /tmp/cfgprobe/.claude/settings.json
    echo '{"hook_event_name":"ConfigChange","source":"project_settings","file_path":"/tmp/cfgprobe/.claude/settings.json","cwd":"/tmp/cfgprobe"}' | \
        python3 -I ConfigChange-audit-claude-config.py
    # exit 0, stdout: {"decision": "block", ...}

Verify (allow, file removed):
    echo '{"hook_event_name":"ConfigChange","source":"project_settings","file_path":"/tmp/cfgprobe/.claude/gone.json","cwd":"/tmp/cfgprobe"}' | \
        python3 -I ConfigChange-audit-claude-config.py
    # exit 0, empty stdout

Full matrix: python3 -I mac/harness/hooks/tests/test_configchange_audit_claude_config.py \
    mac/harness/hooks/ConfigChange-audit-claude-config.py

Owner: harness-engineering (October 30, 2026)
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone

GATED_SOURCES = {"project_settings", "local_settings"}
_SOURCE_RELPATH = {
    "project_settings": os.path.join(".claude", "settings.json"),
    "local_settings": os.path.join(".claude", "settings.local.json"),
}


def _config_root() -> str:
    return os.path.abspath(
        os.environ.get("CLAUDE_CONFIG_DIR")
        or os.path.join(os.path.expanduser("~"), ".claude")
    )


def _log(line: str) -> None:
    path = os.path.join(_config_root(), "logs", "config-change-gate.log")
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(
                datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                + "\t"
                + line
                + "\n"
            )
    except OSError:
        pass


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _registry() -> dict:
    path = os.path.join(_config_root(), "audited-hashes.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, dict) else {}


def _block(why: str) -> int:
    _log("BLOCK\t" + why)
    print(json.dumps({"decision": "block", "reason": why}))
    return 0


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        sys.stderr.write(
            f"ConfigChange-audit-claude-config: payload is not JSON ({exc}). Blocked per AP.8.\n"
        )
        return 2
    source = data.get("source", "")
    if source not in GATED_SOURCES:
        return 0
    cwd = os.path.abspath(data.get("cwd") or os.getcwd())
    file_path = data.get("file_path") or os.path.join(cwd, _SOURCE_RELPATH[source])
    file_path = os.path.abspath(file_path)
    if not os.path.isfile(file_path):
        _log(f"ALLOW\t{source}\t{file_path}\tfile absent")
        return 0
    digest = _sha256(file_path)
    if digest in _registry():
        _log(f"ALLOW\t{source}\t{file_path}\tsha256 {digest}")
        return 0
    return _block(
        f"{source} change to {file_path} is not in the audited-hash registry (sha256 {digest}). "
        f"The new settings were not applied. Review the file, add the hash to "
        f"{os.path.join(_config_root(), 'audited-hashes.json')} with a note, then touch the file. "
        f"foundation/01 T.3, Phase 2 Q5 every-change cadence."
    )


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001  fail closed per AP.8
        sys.stderr.write(
            f"ConfigChange-audit-claude-config failed: {exc!r}. Blocked per AP.8.\n"
        )
        sys.exit(2)
