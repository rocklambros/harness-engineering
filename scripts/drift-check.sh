#!/usr/bin/env bash
#
# drift-check.sh
#
# Enforces QC.4b (context window discipline) from
# foundation/00-quality-contract.md. Run by pre-commit and by CI.
#
# Two checks:
#
# 1. Worst-case per-session CLAUDE.md hierarchy line count.
#    Each Claude Code session walks from cwd up to the project root,
#    loading every CLAUDE.md it finds. The cached prefix per session
#    is root CLAUDE.md plus the platform-specific hierarchy under one
#    platform directory (e.g., mac/CLAUDE.md if present plus
#    mac/harness/CLAUDE.md). The drift check computes the worst case
#    across all platform-session combinations and tests against the
#    cap. The 400-line cap reflects the threshold above which
#    instruction-following degrades non-trivially. The 250-line target
#    leaves headroom for platform CLAUDE.md files to grow without
#    immediately tripping the cap.
#
#    Earlier versions of this script summed every CLAUDE.md file in the
#    repo. That was correct as a paranoid guardrail but wrong as a
#    model of per-session cache prefix reality, since only one platform
#    loads per session. The current model tracks what actually loads.
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

# Configuration. Editable here. The rationale is in the header.
LINE_CAP=400
LINE_TARGET=250

# Globs that identify cached-prefix files for the poisoning check.
# The line-count check categorizes by path pattern below and does not
# use these globs directly.
CACHED_PREFIX_GLOBS=(
    "CLAUDE.md"
    "*/CLAUDE.md"
    "*/harness/CLAUDE.md"
)

# Patterns that indicate per-run state in a cached-prefix file.
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

# Helper. Returns line count for a file if it exists, otherwise 0.
lines_or_zero() {
    if [ -f "$1" ]; then
        wc -l < "$1"
    else
        echo 0
    fi
}

# Categorize CLAUDE.md files by path pattern.
ROOT_LINES=$(lines_or_zero "./CLAUDE.md")

# Discover platform directories from the */harness/CLAUDE.md pattern.
declare -a PLATFORMS=()
for f in */harness/CLAUDE.md; do
    if [ -f "$f" ]; then
        platform_path="${f%/harness/CLAUDE.md}"
        PLATFORMS+=("$platform_path")
    fi
done

# Per-platform session totals. Each platform's worst case is the sum
# of root CLAUDE.md, an optional platform-level CLAUDE.md, and the
# platform's operational harness/CLAUDE.md.
declare -a SESSION_REPORT=()
WORST_CASE=$ROOT_LINES
for p in "${PLATFORMS[@]}"; do
    platform_lines=$(lines_or_zero "./$p/CLAUDE.md")
    harness_lines=$(lines_or_zero "./$p/harness/CLAUDE.md")
    session_total=$((ROOT_LINES + platform_lines + harness_lines))
    SESSION_REPORT+=("  $p session: $session_total lines (root=$ROOT_LINES, $p/CLAUDE.md=$platform_lines, $p/harness/CLAUDE.md=$harness_lines)")
    if [ "$session_total" -gt "$WORST_CASE" ]; then
        WORST_CASE=$session_total
    fi
done

# Identify any CLAUDE.md files outside the expected root/platform pattern.
# These are not necessarily wrong but should be visible.
declare -a OTHER_FILES=()
for f in "${CLAUDE_FILES[@]}"; do
    case "$f" in
        ./CLAUDE.md) ;;
        ./*/CLAUDE.md) ;;
        ./*/harness/CLAUDE.md) ;;
        *) OTHER_FILES+=("$f") ;;
    esac
done

# Verify every CLAUDE.md found is readable. Catches permissions issues
# that would otherwise pollute the count silently.
for f in "${CLAUDE_FILES[@]}"; do
    if [ ! -r "$f" ]; then
        echo "drift-check: cannot read $f" >&2
        exit 2
    fi
done

line_count_status=0
if [ "$WORST_CASE" -gt "$LINE_CAP" ]; then
    line_count_status=1
    echo "FAIL: worst-case per-session CLAUDE.md hierarchy is $WORST_CASE lines, over the $LINE_CAP cap."
    if [ ${#SESSION_REPORT[@]} -gt 0 ]; then
        echo "Per-platform session totals:"
        for line in "${SESSION_REPORT[@]}"; do
            echo "$line"
        done
    fi
    if [ ${#OTHER_FILES[@]} -gt 0 ]; then
        echo "CLAUDE.md files outside the root/platform pattern:"
        for f in "${OTHER_FILES[@]}"; do
            echo "  $(wc -l < "$f") $f"
        done
    fi
    echo "QC.4b context discipline: trim the worst-case session to under $LINE_CAP lines."
elif [ "$WORST_CASE" -gt "$LINE_TARGET" ]; then
    echo "WARN: worst-case per-session CLAUDE.md hierarchy is $WORST_CASE lines, over the $LINE_TARGET target."
    if [ ${#SESSION_REPORT[@]} -gt 0 ]; then
        echo "Per-platform session totals:"
        for line in "${SESSION_REPORT[@]}"; do
            echo "$line"
        done
    fi
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

echo "drift-check: OK (worst-case per-session $WORST_CASE lines across ${#CLAUDE_FILES[@]} CLAUDE.md file(s))"
exit 0
