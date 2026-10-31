#!/usr/bin/env bash
# Install the six fail-closed gates as managed (system) hooks.
#
# Why: hooks in ~/.claude/settings.json and the scripts in ~/.claude/hooks
# are owned by the same user the agent runs as, so a Bash write can replace
# a gate or set "disableAllHooks": true, and neither the ConfigChange gate
# (project and local settings only) nor the external-write gate (file tools
# only) sees it. Managed hooks cannot be disabled from user, project, or
# local settings, and root-owned script copies cannot be rewritten without
# root (https://code.claude.com/docs/en/hooks.md, Hook locations).
#
# What it does, as root:
#   1. Copies the six gate scripts from the platform source tree into
#      LIB_DIR, owned by root, mode 0755 (directory) and 0644 (scripts).
#   2. Writes DROPIN with one registration per gate in exec form, run by
#      an absolute python3 under -I, onFailure "block", timeout 10. The
#      absolute interpreter path keeps a python3 planted earlier on PATH
#      (~/.local/bin is user-writable) from running in its place.
#
# What it does not do: set allowManagedHooksOnly (that would block plugin
# hooks such as claude-mem) or touch the user-level registrations, which
# keep running alongside the managed copies until the operator removes them.
#
# Usage:
#   sudo bash scripts/install-managed-gates.sh --platform jetson
#   sudo bash scripts/install-managed-gates.sh --platform mac
#   bash scripts/install-managed-gates.sh --platform jetson --dry-run
#
# Rerun after every deploy that changes one of the six scripts: drift
# between ~/.claude/hooks and LIB_DIR is not checked yet.
#
# Owner: harness-engineering (October 31, 2026)

set -euo pipefail

PLATFORM=""
DRY_RUN=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --platform) PLATFORM="${2:-}"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) sed -n '2,32p' "$0"; exit 0 ;;
    *) echo "install-managed-gates: unknown argument $1" >&2; exit 2 ;;
  esac
done

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
case "$PLATFORM" in
  jetson)
    SRC="$REPO_ROOT/jetson/harness/hooks"
    MANAGED_DIR="/etc/claude-code"
    LIB_DIR="/usr/local/lib/claude-harness/hooks"
    OWNER="root:root"
    ;;
  mac)
    SRC="$REPO_ROOT/mac/harness/hooks"
    MANAGED_DIR="/Library/Application Support/ClaudeCode"
    LIB_DIR="/usr/local/lib/claude-harness/hooks"
    OWNER="root:wheel"
    ;;
  *) echo "install-managed-gates: --platform jetson|mac is required" >&2; exit 2 ;;
esac
DROPIN="$MANAGED_DIR/managed-settings.d/50-harness-gates.json"
PYTHON="/usr/bin/python3"

[[ -x "$PYTHON" ]] || { echo "install-managed-gates: $PYTHON not found" >&2; exit 2; }

# event|matcher|script
GATES=(
  "PreToolUse|Bash|PreToolUse-bash-deny-rm-protected-paths.py"
  "PreToolUse|Bash|PreToolUse-git-push-force-ask.py"
  "PreToolUse|Bash|PreToolUse-bash-cap-subcommands.py"
  "PreToolUse|Write|Edit|MultiEdit|NotebookEdit|PreToolUse-external-write-gate.py"
  "PreToolUse|Write|Edit|MultiEdit|NotebookEdit|PreToolUse-cached-prefix-write-gate.py"
  "ConfigChange|project_settings|local_settings|ConfigChange-audit-claude-config.py"
)

for gate in "${GATES[@]}"; do
  script="${gate##*|}"
  [[ -f "$SRC/$script" ]] || { echo "install-managed-gates: missing $SRC/$script" >&2; exit 2; }
done

JSON="$("$PYTHON" -I - "$PYTHON" "$LIB_DIR" "${GATES[@]}" <<'PY'
import json, sys
python, lib = sys.argv[1], sys.argv[2]
hooks = {}
for gate in sys.argv[3:]:
    event, rest = gate.split("|", 1)
    matcher, script = rest.rsplit("|", 1)
    entry = {
        "type": "command",
        "command": python,
        "args": ["-I", f"{lib}/{script}"],
        "onFailure": "block",
        "timeout": 10,
    }
    groups = hooks.setdefault(event, [])
    for g in groups:
        if g["matcher"] == matcher:
            g["hooks"].append(entry)
            break
    else:
        groups.append({"matcher": matcher, "hooks": [entry]})
print(json.dumps({"hooks": hooks}, indent=2))
PY
)"

if [[ $DRY_RUN -eq 1 ]]; then
  echo "Would copy into $LIB_DIR (owner $OWNER):"
  for gate in "${GATES[@]}"; do echo "  ${gate##*|}"; done
  echo "Would write $DROPIN:"
  echo "$JSON"
  exit 0
fi

[[ $EUID -eq 0 ]] || { echo "install-managed-gates: run with sudo" >&2; exit 2; }

install -d -o "${OWNER%:*}" -g "${OWNER#*:}" -m 0755 "$LIB_DIR"
for gate in "${GATES[@]}"; do
  script="${gate##*|}"
  install -o "${OWNER%:*}" -g "${OWNER#*:}" -m 0644 "$SRC/$script" "$LIB_DIR/$script"
  cmp -s "$SRC/$script" "$LIB_DIR/$script" || { echo "install-managed-gates: copy mismatch $script" >&2; exit 2; }
done
install -d -o "${OWNER%:*}" -g "${OWNER#*:}" -m 0755 "$MANAGED_DIR/managed-settings.d"
tmp="$(mktemp)"
printf '%s\n' "$JSON" > "$tmp"
install -o "${OWNER%:*}" -g "${OWNER#*:}" -m 0644 "$tmp" "$DROPIN"
rm -f "$tmp"

# Prove each managed gate starts under the managed interpreter. A gate that
# cannot start blocks every matching call, which is the expensive failure.
for gate in "${GATES[@]}"; do
  script="${gate##*|}"
  rc=0
  echo '{}' | "$PYTHON" -I "$LIB_DIR/$script" >/dev/null 2>&1 || rc=$?
  [[ $rc -eq 0 || $rc -eq 2 ]] || { echo "install-managed-gates: $script exited $rc" >&2; exit 2; }
done
echo "Installed six managed gates: $DROPIN"
echo "Restart Claude Code, then run /hooks and confirm each gate lists a managed source."
