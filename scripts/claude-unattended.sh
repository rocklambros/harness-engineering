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
  PreToolUse-bash-cap-subcommands.py
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

# Registrations: each gate must be registered with onFailure: block, in the
# settings file or in root-owned managed settings, where
# scripts/install-managed-gates.sh puts it and where it is removed from the
# user file (operator decision, October 31, 2026). Gates found only in
# managed settings are merged into a private copy of the settings file and
# passed with --settings, because --bare skips settings hooks and its help
# text does not say whether managed hooks survive. The merge keeps the gates
# in the run either way. The managed path is fixed and its files must be
# root-owned and not group or world writable, so a user-writable file there
# cannot pose as policy.
case "$(uname -s)" in
  Darwin) MANAGED_DIR="/Library/Application Support/ClaudeCode" ;;
  *) MANAGED_DIR="/etc/claude-code" ;;
esac
RUN_DIR="$(mktemp -d)"
chmod 0700 "$RUN_DIR"
trap 'rm -rf "$RUN_DIR"' EXIT
MERGED="$RUN_DIR/settings.json"

probes="$(python3 -I - "$SETTINGS" "$MANAGED_DIR" "$HOOKS_DIR" "$MERGED" "${GATES[@]}" <<'PY'
import glob, json, os, stat, sys
settings, managed_dir, hooks_dir, merged = sys.argv[1:5]
gates = sys.argv[5:]

def root_owned(path):
    st = os.stat(path)
    return st.st_uid == 0 and not st.st_mode & (stat.S_IWGRP | stat.S_IWOTH)

def entries(d):
    for event, groups in (d.get("hooks") or {}).items():
        if event.startswith("_") or not isinstance(groups, list):
            continue
        for g in groups:
            if not isinstance(g, dict):
                continue
            for e in g.get("hooks", []):
                if isinstance(e, dict):
                    path = str((e.get("args") or [e.get("command", "")])[-1])
                    yield event, g, e, os.path.basename(path), path

user = json.load(open(settings, encoding="utf-8"))
found = {}
for _, _, e, name, path in entries(user):
    if name in gates and e.get("onFailure") == "block":
        found[name] = ("python3", os.path.join(hooks_dir, name))

files = [os.path.join(managed_dir, "managed-settings.json")]
files += sorted(glob.glob(os.path.join(managed_dir, "managed-settings.d", "*.json")))
add = {}
for f in files:
    if not os.path.isfile(f) or not root_owned(f):
        continue
    for event, g, e, name, path in entries(json.load(open(f, encoding="utf-8"))):
        if name not in gates or name in found or e.get("onFailure") != "block":
            continue
        if not (os.path.isabs(path) and os.path.isfile(path) and root_owned(path)):
            continue
        found[name] = (e.get("command", ""), path)
        add.setdefault(event, []).append({"matcher": g.get("matcher", ""), "hooks": [e]})

missing = [g for g in gates if g not in found]
if missing:
    print("not registered fail-closed: " + ", ".join(missing), file=sys.stderr)
    sys.exit(1)
hooks = user.setdefault("hooks", {})
for event, groups in add.items():
    hooks.setdefault(event, []).extend(groups)
fd = os.open(merged, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(fd, "w", encoding="utf-8") as out:
    json.dump(user, out)
for name in gates:
    print("\t".join(found[name]))
PY
)" || fail "settings file and managed settings do not register every gate fail-closed"

# Start probe: each gate run by its registered interpreter on empty stdin
# must exit 0 or 2. 127 means no interpreter, 1 means a crash, either of
# which would block the whole run.
while IFS=$'\t' read -r interp path; do
  [[ -f "$path" ]] || fail "gate missing on disk: $path"
  set +e
  "$interp" -I "$path" </dev/null >/dev/null 2>&1
  rc=$?
  set -e
  if [[ $rc -ne 0 && $rc -ne 2 ]]; then
    fail "gate cannot start cleanly (exit $rc): $path"
  fi
done <<< "$probes"

# Not exec: the EXIT trap has to remove the merged settings copy, which can
# carry the same env and helper settings as the original.
set +e
claude -p --settings "$MERGED" "$@"
rc=$?
set -e
exit "$rc"
