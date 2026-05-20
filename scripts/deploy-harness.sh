#!/usr/bin/env bash
# Deploy the harness from the checked-out repo to the live host.
#
# Copies hook scripts byte-for-byte into ~/.claude/hooks/. Renders the
# platform settings template (substituting {{REPO_ROOT}}) and diffs the
# hooks block against the deployed ~/.claude/settings.json so the operator
# can apply the change manually. Does NOT overwrite settings.json: the
# deployed copy typically carries operator personalizations (model
# selection, plugins, MCP servers, custom permission allows) that a
# wholesale overwrite would destroy.
#
# Usage:
#   scripts/deploy-harness.sh --platform jetson|mac|windows [--dry-run]
#
# Exit codes:
#   0  deploy completed cleanly (or dry-run succeeded)
#   1  deploy detected a problem the operator must resolve
#   2  script error (bad args, missing files, fail-closed per AP.8)
#
# Owner: harness-engineering, post-Phase 3 follow-up (May 20, 2026)

set -euo pipefail

PLATFORM=""
DRY_RUN=0

while (( $# > 0 )); do
  case "$1" in
    --platform)
      PLATFORM="${2:-}"
      shift 2
      ;;
    --platform=*)
      PLATFORM="${1#--platform=}"
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      sed -n '2,15p' "$0"
      exit 0
      ;;
    *)
      echo "ERROR: unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

case "$PLATFORM" in
  jetson|mac|windows) ;;
  "")
    echo "ERROR: --platform is required (jetson|mac|windows)" >&2
    exit 2
    ;;
  *)
    echo "ERROR: --platform must be jetson, mac, or windows (got: $PLATFORM)" >&2
    exit 2
    ;;
esac

# Resolve repo root from the script's own location so the script works
# regardless of the operator's cwd at invocation time.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

SRC_HOOKS="$REPO_ROOT/$PLATFORM/harness/hooks"
SRC_TEMPLATE_CANDIDATES=(
  "$REPO_ROOT/$PLATFORM/harness/settings.json.template"
  "$REPO_ROOT/$PLATFORM/harness/settings.json"
)

# Pick the first settings source that exists. Mac uses settings.json
# (no substitution needed today); jetson and windows use the .template.
SRC_TEMPLATE=""
for candidate in "${SRC_TEMPLATE_CANDIDATES[@]}"; do
  if [[ -f "$candidate" ]]; then
    SRC_TEMPLATE="$candidate"
    break
  fi
done

DST_HOOKS="$HOME/.claude/hooks"
DEPLOYED_SETTINGS="$HOME/.claude/settings.json"

if [[ ! -d "$SRC_HOOKS" ]]; then
  echo "ERROR: source hooks dir not found: $SRC_HOOKS" >&2
  exit 2
fi
if [[ -z "$SRC_TEMPLATE" ]]; then
  echo "ERROR: no settings.json or settings.json.template found under $REPO_ROOT/$PLATFORM/harness/" >&2
  exit 2
fi

mkdir -p "$DST_HOOKS"

prefix="[deploy-harness:$PLATFORM]"
(( DRY_RUN )) && prefix="$prefix(dry-run)"
echo "$prefix repo: $REPO_ROOT"
echo "$prefix source hooks: $SRC_HOOKS"
echo "$prefix source settings: $SRC_TEMPLATE"
echo "$prefix deployed hooks: $DST_HOOKS"
echo "$prefix deployed settings: $DEPLOYED_SETTINGS"
echo ""

# --- Hook files: byte-for-byte deploy --------------------------------------

echo "=== Hook file deployment ==="
hooks_changed=0
shopt -s nullglob
for src in "$SRC_HOOKS"/*.sh "$SRC_HOOKS"/*.py; do
  base="$(basename "$src")"
  dst="$DST_HOOKS/$base"
  if [[ ! -f "$dst" ]] || ! cmp -s "$src" "$dst"; then
    if (( DRY_RUN )); then
      echo "  WOULD UPDATE: $base"
    else
      cp -p "$src" "$dst"
      chmod +x "$dst"
      echo "  updated: $base"
    fi
    hooks_changed=$((hooks_changed + 1))
  else
    echo "  unchanged: $base"
  fi
done
shopt -u nullglob
echo "Hook files changed: $hooks_changed"

# --- Orphan check: deployed hooks not in source ----------------------------

echo ""
echo "=== Orphan hooks in $DST_HOOKS (deployed but not in $PLATFORM source) ==="
orphans=0
shopt -s nullglob
for dst in "$DST_HOOKS"/*.sh "$DST_HOOKS"/*.py; do
  base="$(basename "$dst")"
  if [[ ! -f "$SRC_HOOKS/$base" ]]; then
    echo "  ORPHAN: $base"
    orphans=$((orphans + 1))
  fi
done
shopt -u nullglob
if (( orphans == 0 )); then
  echo "  (none)"
else
  echo ""
  echo "  Orphans are deployed hooks the $PLATFORM source no longer carries."
  echo "  Common cause: a prior install of a hook that was later removed"
  echo "  (e.g., MemPalace hooks on Jetson per the Memory layer divergence"
  echo "  in jetson/ARCHITECTURE.md). This script does NOT delete them."
  echo "  Review each one and remove manually if confirmed stale:"
  echo "    rm $DST_HOOKS/<filename>"
fi

# --- settings.json: diff-only (deliberately no auto-merge) -----------------

echo ""
echo "=== settings.json diff (template-substituted vs deployed) ==="

substituted="$(mktemp)"
# Trap cleanup of the tempfile on any exit path.
trap 'rm -f "$substituted"' EXIT

# The template references hooks at {{REPO_ROOT}}/harness/hooks/<name>, a path
# layout that fits adopting projects (where the harness is copied in at root)
# but not this build repo (where it lives at <platform>/harness/). Since the
# Hook file deployment step above already copies hook scripts into
# ~/.claude/hooks/, rewrite the placeholder to that deployed location so the
# substituted settings.json references files that actually exist on the host.
sed "s|{{REPO_ROOT}}/harness/hooks|$HOME/.claude/hooks|g" "$SRC_TEMPLATE" > "$substituted"

# Any remaining {{REPO_ROOT}} placeholder is unrelated to hook paths and
# probably an unhandled case in this script. Surface it loudly so the
# operator does not silently end up with a literal {{REPO_ROOT}} in their
# deployed settings. Documentation-only references inside _comment_*
# template keys are inert (the comments do not affect runtime) so we
# filter those out.
remaining="$(grep -n "{{REPO_ROOT}}" "$substituted" | grep -vE '"_comment_[a-z_]+":' || true)"
if [[ -n "$remaining" ]]; then
  echo "WARN: unhandled {{REPO_ROOT}} placeholders remain after substitution:" >&2
  printf '%s\n' "$remaining" >&2
  echo "WARN: rewrite these manually in $DEPLOYED_SETTINGS, or extend this script." >&2
fi

# Validate the substituted result is valid JSON before going further.
if ! python3 -c "import json,sys; json.load(open('$substituted'))" 2>/dev/null; then
  echo "ERROR: substituted template is not valid JSON: $SRC_TEMPLATE" >&2
  exit 2
fi

if [[ ! -f "$DEPLOYED_SETTINGS" ]]; then
  echo "  $DEPLOYED_SETTINGS does not exist yet."
  if (( DRY_RUN )); then
    echo "  WOULD INSTALL: cp $substituted $DEPLOYED_SETTINGS"
  else
    cp "$substituted" "$DEPLOYED_SETTINGS"
    echo "  installed fresh: $DEPLOYED_SETTINGS"
  fi
else
  # Compare only the hooks block since the template owns hook registrations.
  # Other top-level keys (permissions, model, env, plugins, mcpServers) may
  # carry operator personalizations the template should not touch.
  python3 - <<PY
import json, sys, difflib
with open("$substituted") as f:
    sub = json.load(f)
with open("$DEPLOYED_SETTINGS") as f:
    dep = json.load(f)
sub_hooks = json.dumps(sub.get("hooks", {}), indent=2, sort_keys=True)
dep_hooks = json.dumps(dep.get("hooks", {}), indent=2, sort_keys=True)
if sub_hooks == dep_hooks:
    print("  hooks block: identical, deployed settings.json is up to date")
    sys.exit(0)
print("  hooks block: DIFFERS")
print("")
for line in difflib.unified_diff(
        dep_hooks.splitlines(),
        sub_hooks.splitlines(),
        fromfile="deployed:hooks",
        tofile="template:hooks (substituted)",
        lineterm=""):
    print("  " + line)
print("")
print("  This script does NOT modify $DEPLOYED_SETTINGS automatically.")
print("  Personal customizations elsewhere in that file (model, plugins,")
print("  MCP servers, custom Bash allows) would be lost in a wholesale")
print("  overwrite. Apply the hooks block change manually:")
print("    1. Open $DEPLOYED_SETTINGS")
print("    2. Replace the value of the top-level \"hooks\" key with the")
print("       block shown above as template:hooks")
print("    3. Re-run this script to confirm 'hooks block: identical'")
PY
fi

echo ""
if (( DRY_RUN )); then
  echo "=== Dry run complete ==="
else
  echo "=== Deploy complete ==="
fi
