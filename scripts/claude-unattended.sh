#!/usr/bin/env bash
# claude-unattended.sh - Launch a non-interactive Claude Code run with the
# harness gates proven present.
#
# Why this exists: Claude Code states that --bare, which skips hook
# discovery, will become the default for -p. A scheduled or scripted run
# that relied on auto-discovery would then start with no write gate, no rm
# deny, no force-push gate, and no config audit. This launcher passes the
# settings file explicitly (bare mode honors --settings), checks the
# running version against the harness floor, and proves each
# destructive-class hook can start before the run begins. A gate that
# cannot start would otherwise block every tool call (onFailure: block) and
# burn the run's budget on refusals.
#
# Usage:
#   scripts/claude-unattended.sh "<prompt>" [any other claude -p flags]
#   HARNESS_SETTINGS=/path/settings.json scripts/claude-unattended.sh ...
#
# Exit codes: 0 pass-through of claude; 2 a precondition failed (nothing ran).
#
# Threat: foundation/01-threat-model.md T.7 (silent capability erosion).
# Owner: harness-engineering (October 30, 2026)

set -euo pipefail

FLOOR="2.1.295"
PIN_MAJOR_MINOR="2.1"
SETTINGS="${HARNESS_SETTINGS:-$HOME/.claude/settings.json}"
HOOKS_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/hooks"
GATES=(
  PreToolUse-bash-deny-rm-protected-paths.py
  PreToolUse-external-write-gate.py
  PreToolUse-cached-prefix-write-gate.py
  PreToolUse-git-push-force-ask.py
  ConfigChange-audit-claude-config.py
)

fail() { echo "claude-unattended: $*" >&2; exit 2; }

command -v claude >/dev/null 2>&1 || fail "claude is not on PATH"
command -v python3 >/dev/null 2>&1 || fail "python3 is not on PATH; every gate needs it"
[[ -f "$SETTINGS" ]] || fail "settings file not found: $SETTINGS"

# Version: at or above the floor where onFailure: block exists, and within
# the pinned minor range (AP.9). sort -V orders dotted versions.
version="$(claude --version 2>/dev/null | awk '{print $1}')"
[[ -n "$version" ]] || fail "could not read claude --version"
lowest="$(printf '%s\n%s\n' "$FLOOR" "$version" | sort -V | head -1)"
[[ "$lowest" == "$FLOOR" ]] || fail "claude $version is below the harness floor $FLOOR (fail-closed hooks need it)"
if [[ "${version%.*}" != "$PIN_MAJOR_MINOR" && -z "${HARNESS_ALLOW_UNPINNED:-}" ]]; then
  fail "claude $version is outside the pinned $PIN_MAJOR_MINOR.x range; re-evaluate per QC.5 or set HARNESS_ALLOW_UNPINNED=1"
fi

# Registrations: each gate must be in the settings file with onFailure: block.
python3 -I - "$SETTINGS" "${GATES[@]}" <<'PY' || fail "settings file does not register every gate fail-closed"
import json, os, sys
settings, gates = sys.argv[1], set(sys.argv[2:])
d = json.load(open(settings, encoding="utf-8"))
seen = {}
for event, groups in (d.get("hooks") or {}).items():
    if event.startswith("_") or not isinstance(groups, list):
        continue
    for g in groups:
        for e in g.get("hooks", []) if isinstance(g, dict) else []:
            if not isinstance(e, dict):
                continue
            path = (e.get("args") or [e.get("command", "")])[-1]
            seen[os.path.basename(str(path))] = e.get("onFailure")
missing = [g for g in gates if seen.get(g) != "block"]
if missing:
    print("not registered fail-closed: " + ", ".join(missing), file=sys.stderr)
    sys.exit(1)
PY

# Start probe: each gate run on empty stdin must exit 0 or 2. 127 means no
# interpreter, 1 means a crash, either of which would block the whole run.
for gate in "${GATES[@]}"; do
  path="$HOOKS_DIR/$gate"
  [[ -f "$path" ]] || fail "gate missing on disk: $path"
  set +e
  python3 -I "$path" </dev/null >/dev/null 2>&1
  rc=$?
  set -e
  if [[ $rc -ne 0 && $rc -ne 2 ]]; then
    fail "gate cannot start cleanly (exit $rc): $path"
  fi
done

exec claude -p --settings "$SETTINGS" "$@"
