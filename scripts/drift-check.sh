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
# Exit code 0: clean OR user-level chain over cap (WARN, not FAIL).
# Exit code 1: project-controlled drift detected (root + platform CLAUDE.md
# over cap, or cached-prefix poisoning pattern present). Exit code 2:
# script error (missing dependencies, unreadable files, etc.).
#
# FAIL vs. WARN split: the project-controlled hierarchy (root CLAUDE.md
# plus one platform's CLAUDE.md plus that platform's harness/CLAUDE.md)
# is what this repo's authors directly control on every commit. That
# portion remains a hard FAIL above the cap. The user-level chain
# (~/.claude/CLAUDE.md and its transitive @imports) is per-machine
# state outside this repo. Mac Phase 2 Q3 / Post-Mac 4 Stage 4 elected
# to keep SuperClaude framework files @imported there, which holds
# the user-level chain above the cap by design. Pre-commit blocking
# on per-machine state would block every commit from that machine
# while saying nothing about the project content the commit changes.
# User-level pressure becomes WARN; project-controlled pressure stays
# FAIL.
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
# while-read pattern instead of mapfile so the script runs on bash 3.2 (macOS system bash).
CLAUDE_FILES=()
while IFS= read -r line; do
    CLAUDE_FILES+=("$line")
done < <(
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

# walk_imports recursively follows the Claude Code @import chain starting
# at $1 and accumulates lines into USER_LEVEL_TOTAL. The chain is the
# user-level cached prefix that loads per-session before any project
# CLAUDE.md, so its line count must factor into the worst-case-per-session
# budget per Phase 2 Q10.
#
# Cycle detection uses VISITED (linear search; bash 3.2 lacks associative
# arrays). Missing files contribute zero so the script stays usable on
# machines without ~/.claude/CLAUDE.md (e.g., CI runners).
walk_imports() {
    local file="$1"
    local v
    if [ "${#VISITED[@]}" -gt 0 ]; then
        for v in "${VISITED[@]}"; do
            if [ "$v" = "$file" ]; then
                return 0
            fi
        done
    fi
    VISITED+=("$file")

    if [ ! -f "$file" ]; then
        return 0
    fi

    local lines
    lines=$(wc -l < "$file")
    USER_LEVEL_TOTAL=$((USER_LEVEL_TOTAL + lines))
    USER_LEVEL_CHAIN+=("$lines $file")

    local dir
    dir="$(dirname "$file")"

    # Claude Code @import syntax: @<path> at start of line followed by a
    # non-space path. awk filters to that exact shape; false positives on
    # prose get filtered by the file-exists check during recursion.
    local imp target
    while IFS= read -r imp; do
        if [ -z "$imp" ]; then
            continue
        fi
        if [[ "$imp" = /* ]]; then
            target="$imp"
        else
            target="$dir/$imp"
        fi
        walk_imports "$target"
    done < <(awk '/^@[^[:space:]]/ { sub(/^@/, ""); print $1 }' "$file" 2>/dev/null)
}

# Walk the user-level chain once. The result feeds every platform's
# session_total below.
USER_LEVEL_FILE="$HOME/.claude/CLAUDE.md"
USER_LEVEL_TOTAL=0
declare -a USER_LEVEL_CHAIN=()
declare -a VISITED=()
if [ -f "$USER_LEVEL_FILE" ]; then
    walk_imports "$USER_LEVEL_FILE"
fi

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

# Per-platform session totals. PROJECT_WORST_CASE excludes the user-level
# chain (this repo's authors control it; it's the FAIL gate).
# FULL_WORST_CASE includes the user-level chain (per-machine state;
# WARN gate when it pushes the total over the cap with project-only
# under).
declare -a SESSION_REPORT=()
PROJECT_WORST_CASE=$ROOT_LINES
FULL_WORST_CASE=$((ROOT_LINES + USER_LEVEL_TOTAL))
for p in "${PLATFORMS[@]}"; do
    platform_lines=$(lines_or_zero "./$p/CLAUDE.md")
    harness_lines=$(lines_or_zero "./$p/harness/CLAUDE.md")
    project_total=$((ROOT_LINES + platform_lines + harness_lines))
    session_total=$((project_total + USER_LEVEL_TOTAL))
    SESSION_REPORT+=("  $p session: $session_total lines (root=$ROOT_LINES, $p/CLAUDE.md=$platform_lines, $p/harness/CLAUDE.md=$harness_lines, user-level=$USER_LEVEL_TOTAL)")
    if [ "$project_total" -gt "$PROJECT_WORST_CASE" ]; then
        PROJECT_WORST_CASE=$project_total
    fi
    if [ "$session_total" -gt "$FULL_WORST_CASE" ]; then
        FULL_WORST_CASE=$session_total
    fi
done

# Identify any CLAUDE.md files outside the expected root/platform pattern.
# These are not necessarily wrong but should be visible.
declare -a OTHER_FILES=()
for f in "${CLAUDE_FILES[@]}"; do
    case "$f" in
        ./CLAUDE.md) ;;
        # ./*/CLAUDE.md covers both platform-level (./mac/CLAUDE.md) and
        # harness-level (./mac/harness/CLAUDE.md) because case-statement
        # globs match across slashes; no additional pattern needed.
        ./*/CLAUDE.md) ;;
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
if [ "$PROJECT_WORST_CASE" -gt "$LINE_CAP" ]; then
    line_count_status=1
    echo "FAIL: project-controlled CLAUDE.md hierarchy (root + platform) is $PROJECT_WORST_CASE lines, over the $LINE_CAP cap."
    if [ ${#SESSION_REPORT[@]} -gt 0 ]; then
        echo "Per-platform session totals (full, incl. user-level):"
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
    echo "QC.4b context discipline: trim the project CLAUDE.md hierarchy to under $LINE_CAP lines."
elif [ "$FULL_WORST_CASE" -gt "$LINE_CAP" ]; then
    # Project-only is under cap; user-level chain pushes total over. WARN, not FAIL.
    echo "WARN: full worst-case per-session hierarchy is $FULL_WORST_CASE lines, over the $LINE_CAP cap."
    echo "Project-controlled portion is $PROJECT_WORST_CASE lines (under cap)."
    echo "User-level chain accounts for $USER_LEVEL_TOTAL lines (per-machine state)."
    echo "SuperClaude operational continuity per Mac Phase 2 Q3 / Post-Mac 4 Stage 4 is the accepted QC.4b exception."
    if [ ${#SESSION_REPORT[@]} -gt 0 ]; then
        echo "Per-platform session totals:"
        for line in "${SESSION_REPORT[@]}"; do
            echo "$line"
        done
    fi
    if [ "$USER_LEVEL_TOTAL" -gt 0 ]; then
        echo "User-level chain ($USER_LEVEL_FILE and transitive @imports):"
        for entry in "${USER_LEVEL_CHAIN[@]}"; do
            echo "  $entry"
        done
        echo "  Total: $USER_LEVEL_TOTAL lines"
    fi
elif [ "$FULL_WORST_CASE" -gt "$LINE_TARGET" ]; then
    echo "WARN: worst-case per-session CLAUDE.md hierarchy is $FULL_WORST_CASE lines, over the $LINE_TARGET target."
    if [ ${#SESSION_REPORT[@]} -gt 0 ]; then
        echo "Per-platform session totals:"
        for line in "${SESSION_REPORT[@]}"; do
            echo "$line"
        done
    fi
    if [ "$USER_LEVEL_TOTAL" -gt 0 ]; then
        echo "User-level chain ($USER_LEVEL_FILE and transitive @imports):"
        for entry in "${USER_LEVEL_CHAIN[@]}"; do
            echo "  $entry"
        done
        echo "  Total: $USER_LEVEL_TOTAL lines"
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

echo "drift-check: OK (project worst-case $PROJECT_WORST_CASE lines, full worst-case $FULL_WORST_CASE lines incl. user-level chain of ${#USER_LEVEL_CHAIN[@]} file(s) / $USER_LEVEL_TOTAL lines)"
exit 0
