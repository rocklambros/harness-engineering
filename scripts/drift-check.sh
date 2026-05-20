#!/usr/bin/env bash
# drift-check.sh - Verify that cited references in artifacts match actual content.
#
# Runs at pre-commit. Checks:
#   1. Foundation docs reference research files that actually exist in research/.
#   2. Phase prompts reference QC IDs that exist in foundation/00-quality-contract.md.
#   3. Skills and hooks reference Threat IDs that exist in foundation/01-threat-model.md.
#   4. Shell hooks pass shellcheck.
#   5. Deployed ~/.claude/hooks copies match their tracked source byte for byte.
#
# Exit codes:
#   0  no drift found
#   1  drift found (commit blocked)
#   2  script error (commit blocked, fail-closed per AP.8)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Colors for terminal output, fall back to plain if not a tty.
if [[ -t 1 ]]; then
  RED=$'\e[31m'
  YELLOW=$'\e[33m'
  GREEN=$'\e[32m'
  RESET=$'\e[0m'
else
  RED=""
  YELLOW=""
  GREEN=""
  RESET=""
fi

DRIFT_FOUND=0

log_drift() {
  echo "${RED}DRIFT:${RESET} $1" >&2
  DRIFT_FOUND=1
}

log_warn() {
  echo "${YELLOW}WARN:${RESET} $1" >&2
}

log_ok() {
  echo "${GREEN}OK:${RESET} $1"
}

# Deterministic ID extraction from stdin. Mode arg: "qc" or "threat".
#
# Three engine traps make the obvious approaches non-portable here:
#   1. macOS ships ugrep; `grep -o` with an optional-suffix pattern emits a
#      phantom shorter token from a suffixed ID, producing false drift.
#   2. BSD awk's match() is not reliably leftmost-longest for an optional
#      trailing class, so an awk regex ending in one has the same problem.
#   3. A regex passed via `awk -v` is subject to escape processing that
#      differs across awks, so the dot can collapse to "any char".
#
# Defenses: the pattern is a hardcoded awk regex literal (no -v, no escape
# ambiguity); the base is digit-terminated (`[0-9]+` is unambiguous, no
# optional tail); one trailing lowercase letter is peeked deterministically
# for QC IDs only. nawk has no \b, so the left word boundary is checked by
# hand. LC_ALL=C: IDs are pure ASCII and BSD awk otherwise aborts input with
# "towc: multibyte conversion failure" on the non-ASCII bytes in the prose.
extract_ids() {
  LC_ALL=C awk -v mode="$1" '
    {
      line = $0
      for (;;) {
        if (mode == "qc")     { ok = match(line, /QC\.[0-9]+/) }
        else                  { ok = match(line, /T\.[0-9]+/) }
        if (!ok) break
        tok = substr(line, RSTART, RLENGTH)
        nx  = substr(line, RSTART + RLENGTH, 1)
        adv = RLENGTH
        if (mode == "qc" && nx ~ /[a-z]/) { tok = tok nx; adv = adv + 1 }
        before = (RSTART == 1) ? "" : substr(line, RSTART - 1, 1)
        if (before !~ /[A-Za-z0-9_]/) print tok
        line = substr(line, RSTART + adv)
      }
    }' | sort -u
}

# Check 1: foundation docs reference research files that exist.
check_research_references() {
  local fail=0
  if [[ ! -d "research" ]]; then
    log_warn "research/ does not exist yet, skipping research reference check"
    return 0
  fi

  # Look for references like research/Claude_Architecture.md in foundation/
  while IFS= read -r ref; do
    local path
    path="$(echo "$ref" | sed -E 's|.*(research/[A-Za-z0-9._-]+\.md).*|\1|')"
    if [[ ! -f "$path" ]]; then
      log_drift "foundation references missing file: $path"
      fail=1
    fi
  done < <(grep -rohE 'research/[A-Za-z0-9._-]+\.md' foundation/ 2>/dev/null | sort -u || true)

  [[ $fail -eq 0 ]] && log_ok "research references resolve"
}

# Check 2: prompts reference QC IDs that exist in the Quality Contract.
check_qc_references() {
  local qc_file="foundation/00-quality-contract.md"
  if [[ ! -f "$qc_file" ]]; then
    log_drift "missing $qc_file"
    return
  fi

  # Extract defined QC IDs (e.g., QC.1, QC.4a, QC.4b).
  local defined_ids
  defined_ids="$(extract_ids qc < "$qc_file")"

  # Find all QC ID references across tracked artifacts. git grep scans only
  # tracked files, so .gitignore is honored: build-internal scratch like
  # phase-outputs/ (which discusses IDs as examples) does not false-trip the
  # check. extract_ids does the deterministic tokenize. research/ holds
  # large third-party source docs and is excluded by pathspec.
  local referenced_ids
  referenced_ids="$(git grep -hE 'QC\.[0-9]+' -- \
    '*.md' '*.sh' '*.yaml' '*.json' ':(exclude)research/' \
    2>/dev/null | extract_ids qc || true)"

  local fail=0
  for id in $referenced_ids; do
    if ! printf '%s\n' "$defined_ids" | grep -Fxq -- "$id"; then
      log_drift "reference to undefined Quality Contract ID: $id"
      fail=1
    fi
  done

  [[ $fail -eq 0 ]] && log_ok "QC references resolve"
}

# Check 3: artifacts reference Threat IDs that exist in the threat model.
check_threat_references() {
  local threat_file="foundation/01-threat-model.md"
  if [[ ! -f "$threat_file" ]]; then
    log_drift "missing $threat_file"
    return
  fi

  local defined_ids
  defined_ids="$(extract_ids threat < "$threat_file")"

  # Exclude integration-test.sh scripts: those use T.N as test section
  # labels (T for Test, not Threat), which collide with the threat-ID
  # convention. They are test scaffolding, not threat-model artifacts.
  local referenced_ids
  referenced_ids="$(git grep -hE 'T\.[0-9]+' -- \
    '*.md' '*.sh' \
    ':(exclude)research/' \
    ':(exclude)*/scripts/integration-test.sh' \
    2>/dev/null | extract_ids threat || true)"

  local fail=0
  for id in $referenced_ids; do
    if ! printf '%s\n' "$defined_ids" | grep -Fxq -- "$id"; then
      log_drift "reference to undefined Threat ID: $id"
      fail=1
    fi
  done

  [[ $fail -eq 0 ]] && log_ok "Threat references resolve"
}

# Check 4: hooks marked deterministic actually have shellcheck-clean shell.
check_hook_shell() {
  if ! command -v shellcheck >/dev/null 2>&1; then
    log_warn "shellcheck not installed, skipping hook script check"
    return 0
  fi

  local fail=0
  while IFS= read -r script; do
    if ! shellcheck "$script" >/dev/null 2>&1; then
      log_drift "hook script fails shellcheck: $script"
      fail=1
    fi
  done < <(find mac/harness/hooks jetson/harness/hooks windows/harness/hooks \
    -type f -name '*.sh' 2>/dev/null || true)

  [[ $fail -eq 0 ]] && log_ok "hook scripts pass shellcheck"
}

# Check 5: deployed hooks match their tracked source byte for byte.
#
# The live hooks under ~/.claude/hooks/ are copies of the tracked source in
# mac/harness/hooks/. The on-disk name differs by the event-prefix convention
# (post-tool-use-semgrep.sh deploys as PostToolUse-semgrep.sh) while the
# content must stay identical. A source edit that never reaches the live copy,
# or a live edit that never returns to source, is the silent-drift failure
# this catches. Only deployed counterparts are compared. A source hook with no
# live copy is simply not deployed on this host and is not drift. CI machines
# and fresh adopters have no ~/.claude/hooks, so the check skips when the
# directory is absent.
check_deployed_hooks() {
  local dst_dir="${HOME}/.claude/hooks"
  if [[ ! -d "$dst_dir" ]]; then
    log_warn "$dst_dir absent, skipping deployed-hook parity check"
    return 0
  fi

  local fail=0 src base mapped cand
  while IFS= read -r src; do
    base="$(basename "$src")"
    mapped="$base"
    mapped="${mapped/#post-tool-use-/PostToolUse-}"
    mapped="${mapped/#pre-tool-use-/PreToolUse-}"
    mapped="${mapped/#session-start-/SessionStart-}"
    mapped="${mapped/#pre-compact-/PreCompact-}"
    mapped="${mapped/#stop-/Stop-}"
    mapped="${mapped/#status-line./StatusLine.}"
    for cand in "$base" "$mapped"; do
      if [[ -f "$dst_dir/$cand" ]]; then
        if ! cmp -s "$src" "$dst_dir/$cand"; then
          log_drift "deployed hook differs from source: $cand vs mac/harness/hooks/$base"
          fail=1
        fi
        break
      fi
    done
  done < <(find mac/harness/hooks -type f \( -name '*.sh' -o -name '*.py' \) 2>/dev/null || true)

  [[ $fail -eq 0 ]] && log_ok "deployed hooks match tracked source"
}

main() {
  echo "Running drift check from $REPO_ROOT"
  check_research_references
  check_qc_references
  check_threat_references
  check_hook_shell
  check_deployed_hooks

  if [[ $DRIFT_FOUND -eq 1 ]]; then
    echo "${RED}drift detected, commit blocked${RESET}" >&2
    exit 1
  fi

  echo "${GREEN}no drift detected${RESET}"
  exit 0
}

main "$@"
