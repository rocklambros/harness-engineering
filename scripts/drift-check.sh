#!/usr/bin/env bash
# drift-check.sh - Verify that cited references in artifacts match actual content.
#
# Runs at pre-commit. Checks:
#   1. Foundation docs reference research files that actually exist in research/.
#   2. Phase prompts reference QC IDs that exist in foundation/00-quality-contract.md.
#   3. Skills and hooks reference Threat IDs that exist in foundation/01-threat-model.md.
#   4. Shell hooks pass shellcheck.
#   5. Deployed ~/.claude/hooks copies match their tracked source byte for byte.
#   6. Hook registrations agree across the reference settings, the template,
#      and the live user settings, with documented per-source extras only.
#   7. Every file the secret gate excludes from scanning is covered by the
#      shape gate, so an exclusion can never be both unscanned and unvalidated.
#   8. Live user settings carry every permissions deny and ask rule the
#      platform settings source ships. Allow rules are not checked.
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

# Detect which platform source tree to compare deployed hooks against.
# Darwin = mac, aarch64 Linux = jetson, x86_64 Linux or MINGW/MSYS = windows.
detect_hook_source_dir() {
  local kernel arch
  kernel="$(uname -s)"
  arch="$(uname -m)"
  case "$kernel" in
    Darwin)          echo "mac/harness/hooks" ;;
    Linux)
      if [[ "$arch" == "aarch64" ]]; then
        echo "jetson/harness/hooks"
      else
        echo "linux/harness/hooks"
      fi
      ;;
    MINGW*|MSYS*|CYGWIN*)  echo "windows/harness/hooks" ;;
    *)               echo "mac/harness/hooks" ;;
  esac
}

HOOK_SOURCE_DIR="$(detect_hook_source_dir)"

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

  if (( fail == 0 )); then log_ok "research references resolve"; fi
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

  if (( fail == 0 )); then log_ok "QC references resolve"; fi
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

  if (( fail == 0 )); then log_ok "Threat references resolve"; fi
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

  if (( fail == 0 )); then log_ok "hook scripts pass shellcheck"; fi
}

# Check 5: deployed hooks match their tracked source byte for byte.
#
# The live hooks under ~/.claude/hooks/ are copies of the tracked source in
# the platform-specific harness directory (detected by HOOK_SOURCE_DIR).
# The on-disk name differs by the event-prefix convention
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

  if [[ ! -d "$HOOK_SOURCE_DIR" ]]; then
    log_warn "$HOOK_SOURCE_DIR absent, skipping deployed-hook parity check"
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
          log_drift "deployed hook differs from source: $cand vs $HOOK_SOURCE_DIR/$base"
          fail=1
        fi
        break
      fi
    done
  done < <(find "$HOOK_SOURCE_DIR" -type f \( -name '*.sh' -o -name '*.py' \) 2>/dev/null || true)

  if (( fail == 0 )); then log_ok "deployed hooks match tracked source ($HOOK_SOURCE_DIR)"; fi
}

# Check 6: hook registrations agree across settings sources.
#
# Check 5 proves the hook files match. This proves the registrations do: the
# same harness hooks on the same events in mac/harness/settings.json, the
# adopter template, and the live ~/.claude/settings.json, each allowed only
# its documented extras, and the five destructive-class hooks registered
# fail-closed everywhere. A hook that exists on disk but is registered in
# one source and not another is the drift the October 30, 2026 premortem
# found and this check closes.
check_hook_registrations() {
  if ! command -v python3 >/dev/null 2>&1; then
    log_warn "python3 not installed, skipping hook registration check"
    return 0
  fi
  local out
  if out="$(python3 -I scripts/check-hook-registrations.py 2>&1)"; then
    log_ok "$out"
  else
    while IFS= read -r line; do
      log_drift "${line#drift: }"
    done <<< "$out"
  fi
}

# Check 7: the secret gate's exclusion set is covered by the shape gate.
#
# ~/.claude/.gitleaks.toml excludes plugin-audit/manifests/*.json from the
# backup push scan, because a `paths` allowlist in gitleaks 8.30 is a
# file-level exclusion and those files are digests keyed by plugin file paths,
# which generic-api-key reads as hundreds of leaked credentials. An excluded
# file is an unscanned file, so hooks/validate-audit-manifests.py stands in for
# the scan and requires every value in an excluded file to be a digest.
#
# The original pairing hardcoded the manifest glob in backup-config.sh while
# the config carried its own regex. Two definitions of one set: widening the
# config without the glob would leave a path neither scanned nor validated, and
# nothing would fail. The gate now DERIVES its set from the config, so this
# check proves the derivation is still in place rather than comparing two
# patterns that are no longer meant to be compared.
check_secret_gate_coverage() {
  local live="${HOME}/.claude"
  local gate="${live}/hooks/validate-audit-manifests.py"
  local backup="${live}/hooks/backup-config.sh"
  local config="${live}/.gitleaks.toml"

  # Live-only Mac files. A host without them has no exclusion to cover.
  if [[ ! -f "$backup" && ! -f "$config" ]]; then
    log_warn "no live backup hook or gitleaks config, skipping secret-gate coverage check"
    return 0
  fi
  if ! command -v python3 >/dev/null 2>&1; then
    log_warn "python3 not installed, skipping secret-gate coverage check"
    return 0
  fi

  local fail=0

  # A gitleaks config that excludes paths, with no gate to cover them, is the
  # exact hole this check exists for.
  if [[ -f "$config" && ! -f "$gate" ]]; then
    log_drift "gitleaks config present but shape gate missing: $gate"
    return 0
  fi
  if [[ ! -f "$gate" ]]; then
    log_warn "no shape gate and no gitleaks config, nothing to cover"
    return 0
  fi

  # The gate's own invariant suite, including the live-config sanity case that
  # asserts no credential-bearing config file has been swept into an exclusion.
  local out
  if ! out="$(python3 -I "$gate" --self-test 2>&1)"; then
    while IFS= read -r line; do
      [[ "$line" == *FAIL* || "$line" == self-test:* ]] && log_drift "shape gate self-test: $line"
    done <<< "$out"
    fail=1
  fi

  # The gate has to be wired in, and wired in fail-closed. Either grep failing
  # means an exclusion could go unvalidated at push time.
  if [[ -f "$backup" ]]; then
    if ! grep -q 'validate-audit-manifests.py' "$backup"; then
      log_drift "backup-config.sh no longer invokes the shape gate; exclusions would go unvalidated"
      fail=1
    fi
    if ! grep -q 'refusing to push unscanned exclusions' "$backup"; then
      log_drift "backup-config.sh lost its fail-closed guard for a missing shape gate"
      fail=1
    fi
    # The coupling this check replaced: a path pattern hardcoded into the
    # staging query instead of derived from the config.
    if grep -qE "diff --cached[^|]*plugin-audit" "$backup"; then
      log_drift "backup-config.sh hardcodes a plugin-audit path pattern again; derive it from .gitleaks.toml"
      fail=1
    fi
  fi

  # An if block, not `[[ ]] && log_ok`: that compound returns 1 on drift, and as
  # the last command in the function it makes the function return 1, which under
  # set -e exits before the closing summary and any later check. Commit 77db09d
  # fixed the five checks that predate this one.
  if [[ $fail -eq 0 ]]; then
    log_ok "secret-gate exclusions are covered by the shape gate (self-test $(sed -n 's/^self-test: //p' <<< "$out"))"
  fi
}

# Check 8: live permission rules include every deny and ask rule shipped.
#
# deploy-harness.sh diffs only the hooks block and check 6 reads only hooks,
# so a deny rule dropped from ~/.claude/settings.json was invisible. Allows
# are excluded on purpose: the source's project-scope allows such as
# Read(./**) must not be pushed to user level.
check_permission_rules() {
  if ! command -v python3 >/dev/null 2>&1; then
    log_warn "python3 not installed, skipping permission rule check"
    return 0
  fi
  local out
  if out="$(python3 -I scripts/check-permission-rules.py 2>&1)"; then
    log_ok "$out"
  else
    while IFS= read -r line; do
      log_drift "${line#drift: }"
    done <<< "$out"
  fi
}

main() {
  echo "Running drift check from $REPO_ROOT"
  check_research_references
  check_qc_references
  check_threat_references
  check_hook_shell
  check_deployed_hooks
  check_hook_registrations
  check_secret_gate_coverage
  check_permission_rules

  if [[ $DRIFT_FOUND -eq 1 ]]; then
    echo "${RED}drift detected, commit blocked${RESET}" >&2
    exit 1
  fi

  echo "${GREEN}no drift detected${RESET}"
  exit 0
}

main "$@"
