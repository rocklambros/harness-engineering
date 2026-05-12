#!/usr/bin/env bash
# audit-claude-config.sh
#
# Audit helper for the SessionStart-audit-claude-config.py hook.
#
# Walks the current working directory for `.claude/settings.json`,
# `.claude/settings.local.json`, and `.mcp.json`. Computes sha256 of each.
# For each file whose hash is not already in the audited-hashes registry,
# prompts for an audit note and appends a registry entry.
#
# Registry: ~/.claude/audited-hashes.json
# Hook: mac/harness/hooks/SessionStart-audit-claude-config.py
#
# Purpose: reduce the per-edit friction of the every-clone hash-gated audit
# cadence (Phase 2 Q5). The hook's posture is unchanged; this script makes
# the legitimate audit workflow a single command rather than manual jq
# manipulation of the registry.
#
# Usage:
#   cd <directory containing .claude/ or .mcp.json>
#   bash /path/to/audit-claude-config.sh [--auto-note "<note>"] [--auditor "<name>"]
#
# Flags:
#   --auto-note "<note>"   Use the given note for all new entries (skips
#                          per-file prompts).
#   --auditor "<name>"     Override the auditor name (defaults to $USER).
#   --dry-run              Print what would change without modifying the
#                          registry. Useful for review before commit.
#   --help                 Show this help and exit.
#
# Exit codes:
#   0  success (zero or more entries added)
#   1  no candidate files found in cwd
#   2  registry file is malformed
#   3  user aborted the prompt
#
# Owner: harness-engineering (Post-launch revision, 2026-05-12)

set -euo pipefail

REGISTRY="$HOME/.claude/audited-hashes.json"
CANDIDATES=(".claude/settings.json" ".claude/settings.local.json" ".mcp.json")
AUTO_NOTE=""
AUDITOR="${USER:-unknown}"
DRY_RUN=0

usage() {
    sed -n '2,32p' "$0" | sed 's/^# \{0,1\}//'
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --auto-note)
            AUTO_NOTE="$2"
            shift 2
            ;;
        --auditor)
            AUDITOR="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=1
            shift
            ;;
        --help|-h)
            usage
            ;;
        *)
            echo "Unknown flag: $1" >&2
            echo "Run with --help for usage." >&2
            exit 1
            ;;
    esac
done

# Verify python3 is available (we rely on it for JSON manipulation).
if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: python3 not found on PATH. Required for registry JSON manipulation." >&2
    exit 1
fi

# Find candidate files in cwd.
FOUND=()
for cand in "${CANDIDATES[@]}"; do
    if [[ -f "$cand" ]]; then
        FOUND+=("$cand")
    fi
done

if [[ ${#FOUND[@]} -eq 0 ]]; then
    echo "No candidate files found in $(pwd)."
    echo "Looked for: ${CANDIDATES[*]}"
    exit 1
fi

# Load registry (or initialize empty if absent).
mkdir -p "$(dirname "$REGISTRY")"
if [[ ! -f "$REGISTRY" ]]; then
    echo "{}" > "$REGISTRY"
fi

# Verify registry parses as JSON.
if ! python3 -c "import json; json.load(open('$REGISTRY'))" 2>/dev/null; then
    echo "Error: $REGISTRY is malformed JSON. Repair before continuing." >&2
    exit 2
fi

# Compute hashes and check against registry.
declare -a NEW_ENTRIES=()
TODAY=$(date +%Y-%m-%d)

for file in "${FOUND[@]}"; do
    ABS=$(cd "$(dirname "$file")" && pwd)/$(basename "$file")
    HASH=$(shasum -a 256 "$file" | awk '{print $1}')

    # Check if hash is already in registry.
    EXISTS=$(python3 -c "
import json
with open('$REGISTRY') as f:
    r = json.load(f)
print('1' if '$HASH' in r else '0')
")

    if [[ "$EXISTS" == "1" ]]; then
        echo "[already audited] $ABS"
        continue
    fi

    echo ""
    echo "[NEW] $ABS"
    echo "  sha256: $HASH"

    if [[ -n "$AUTO_NOTE" ]]; then
        NOTE="$AUTO_NOTE"
        echo "  note (auto): $NOTE"
    else
        echo -n "  Enter audit note (or 'skip' to skip, 'abort' to stop): "
        read -r NOTE
        case "$NOTE" in
            skip)
                echo "  skipping"
                continue
                ;;
            abort)
                echo "Aborted by user. Registry unchanged." >&2
                exit 3
                ;;
            "")
                NOTE="Audited via audit-claude-config.sh; no note provided."
                ;;
        esac
    fi

    NEW_ENTRIES+=("$HASH|$ABS|$NOTE")
done

if [[ ${#NEW_ENTRIES[@]} -eq 0 ]]; then
    echo ""
    echo "No new entries to add. Registry unchanged."
    exit 0
fi

echo ""
echo "Will add ${#NEW_ENTRIES[@]} entries to $REGISTRY:"
for entry in "${NEW_ENTRIES[@]}"; do
    H="${entry%%|*}"
    REST="${entry#*|}"
    P="${REST%%|*}"
    N="${REST#*|}"
    echo "  $H  $P"
    echo "    note: $N"
done

if [[ "$DRY_RUN" -eq 1 ]]; then
    echo ""
    echo "DRY RUN: no changes written."
    exit 0
fi

# Append entries to registry via Python (preserves JSON formatting).
python3 - <<PYEOF
import json

with open('$REGISTRY') as f:
    registry = json.load(f)

entries = [
$(for entry in "${NEW_ENTRIES[@]}"; do
    H="${entry%%|*}"
    REST="${entry#*|}"
    P="${REST%%|*}"
    N="${REST#*|}"
    printf '    ("%s", "%s", %s),\n' "$H" "$P" "$(python3 -c "import json,sys; print(json.dumps(sys.argv[1]))" "$N")"
done)
]

for h, p, n in entries:
    registry[h] = {
        "path": p,
        "audited_at": "$TODAY",
        "auditor": "$AUDITOR",
        "note": n,
    }

with open('$REGISTRY', 'w') as f:
    json.dump(registry, f, indent=2, sort_keys=True)

print(f"Added {len(entries)} entries. Registry now has {len(registry)} total.")
PYEOF
