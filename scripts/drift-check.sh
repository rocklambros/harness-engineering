#!/usr/bin/env bash
#
# drift-check.sh
#
# Enforces QC.4b (context window discipline) from
# foundation/00-quality-contract.md. Run by pre-commit and by CI.
#
# Two checks:
#
# 1. CLAUDE.md hierarchy line count.
#    Total lines across CLAUDE.md, harness/CLAUDE.md, and any nested
#    CLAUDE.md files must stay under 400. Target is 250. The 400-line
#    cap reflects the threshold above which instruction-following
#    degrades non-trivially in observation. The target of 250 leaves
#    headroom for the platform-specific harness CLAUDE.md to grow
#    without immediately tripping the cap.
#
# 2. Cached-prefix poisoning patterns.
#    The cached prefix must be cacheable across runs. Timestamps,
#    session identifiers, per-run state, and "last updated" markers
#    break cache reuse silently. The script flags these patterns
#    in any file that contributes to the cached prefix.
#
# Exit code 0: clean. Exit code 1: drift detected (script lists which
# files and which rule). Exit code 2: script error (missing
# dependencies, unreadable files, etc.).
#
# Invoke directly:
#   bash scripts/drift-check.sh
#
# Or via pre-commit:
#   pre-commit run drift-check --all-files

set -euo pipefail

# Resolve repo root so the script works from any working directory.
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT"

# Configuration. Editable here; the rationale is in the header.
LINE_CAP=400
LINE_TARGET=250

# Files that contribute to the cached prefix and therefore must stay
# free of per-run state. Add new entries here when new cached-prefix
# files appear (e.g., per-platform harness/CLAUDE.md as platforms get
# built out).
CACHED_PREFIX_GLOBS=(
    "CLAUDE.md"
    "*/CLAUDE.md"
    "*/harness/CLAUDE.md"
)

# Patterns that indicate per-run state in a cached-prefix file.
# Each pattern is paired with a short reason for the diagnostic.
# Patterns are ERE (extended regex). Case-sensitive on purpose:
# false positives on innocuous prose are worse than missed exact matches.
declare -a POISON_PATTERNS=(
    "Last (updated|run|modified):"
    "Generated (at|on):"
    "Session (ID|id):"
    "Run (ID|id):"
    "Today is "
    "Current date:"
    "Now:"
)

# Find all CLAUDE.md files in the repo (excluding .git and node_modules).
mapfile -t CLAUDE_FILES < <(
    find . \
        -path ./.git -prune -o \
        -path ./node_modules -prune -o \
        -name CLAUDE.md \
        -print 2>/dev/null | sort
)

if [ ${#CLAUDE_FILES[@]} -eq 0 ]; then
    # No CLAUDE.md files yet. Nothing to check.
    exit 0
fi

# Check 1: line count.
total=0
for f in "${CLAUDE_FILES[@]}"; do
    if [ -r "$f" ]; then
        lines=$(wc -l < "$f")
        total=$((total + lines))
    else
        echo "drift-check: cannot read $f" >&2
        exit 2
    fi
done

line_count_status=0
if [ "$total" -gt "$LINE_CAP" ]; then
    line_count_status=1
    echo "FAIL: CLAUDE.md hierarchy is $total lines, over the $LINE_CAP cap."
    for f in "${CLAUDE_FILES[@]}"; do
        echo "  $(wc -l < "$f") $f"
    done
    echo "QC.4b context discipline: trim the hierarchy to under $LINE_CAP lines."
elif [ "$total" -gt "$LINE_TARGET" ]; then
    echo "WARN: CLAUDE.md hierarchy is $total lines, over the $LINE_TARGET target."
    echo "Still under the $LINE_CAP cap but the slack is shrinking."
fi

# Check 2: cached-prefix poisoning.
# Build a list of files matching the cached-prefix globs.
poison_files=()
for glob in "${CACHED_PREFIX_GLOBS[@]}"; do
    # shellcheck disable=SC2086
    # We want word splitting on the glob expansion.
    for f in $glob; do
        if [ -f "$f" ]; then
            poison_files+=("$f")
        fi
    done
done

poison_status=0
for f in "${poison_files[@]}"; do
    for pattern in "${POISON_PATTERNS[@]}"; do
        if grep -nE "$pattern" "$f" >/dev/null 2>&1; then
            poison_status=1
            echo "FAIL: $f contains pattern: $pattern"
            grep -nE "$pattern" "$f" | head -5 | sed 's/^/  /'
        fi
    done
done

if [ "$poison_status" -ne 0 ]; then
    echo "QC.4b context discipline: cached-prefix files must not contain"
    echo "per-run state. Move dynamic content into <system-reminder> blocks."
fi

# Final exit code.
if [ "$line_count_status" -ne 0 ] || [ "$poison_status" -ne 0 ]; then
    exit 1
fi

echo "drift-check: OK ($total lines across ${#CLAUDE_FILES[@]} CLAUDE.md file(s))"
exit 0
