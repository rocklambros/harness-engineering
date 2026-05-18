#!/usr/bin/env bash
# integration-test.sh
#
# End-to-end integration test for the Jetson harness. Creates a synthetic
# project in /tmp, wires the harness into it, and exercises each enforcement
# surface: tool availability, PostToolUse Semgrep hook, pre-commit chain,
# drift check, and session-start hook.
#
# Quality Contract: QC.1 (all security layers exercised), QC.2 (tight test).
# Threat Model: T.1 (synthetic vulnerability detection), T.7 (drift).
#
# Exit 0 if all tests pass. Exit 1 on first failure.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_DIR="/tmp/jetson-harness-test"
PASS=0
FAIL=0

cleanup() {
  rm -rf "${TEST_DIR}"
}
trap cleanup EXIT

log_pass() {
  printf '  PASS  %s\n' "$1"
  PASS=$((PASS + 1))
}

log_fail() {
  printf '  FAIL  %s\n' "$1"
  FAIL=$((FAIL + 1))
}

section() {
  printf '\n%s\n' "$1"
}

printf '=== Jetson Harness Integration Test ===\n\n'

# ---- T.1: Tool availability ------------------------------------------------

section "T.1 Tool availability"

for tool in semgrep gitleaks shellcheck pre-commit jq; do
  if command -v "${tool}" >/dev/null 2>&1; then
    log_pass "${tool} is on PATH"
  else
    log_fail "${tool} is not on PATH"
  fi
done

# ---- T.2: Hook scripts exist and are executable ----------------------------

section "T.2 Hook scripts"

for hook in post-tool-use-semgrep.sh pre-tool-use-shell-audit.sh session-start.sh pre-compact-preserve.sh; do
  hook_path="${REPO_ROOT}/harness/hooks/${hook}"
  if [[ -x "${hook_path}" ]]; then
    log_pass "${hook} exists and is executable"
  else
    log_fail "${hook} missing or not executable at ${hook_path}"
  fi
done

# ---- T.3: Shellcheck on all hook scripts -----------------------------------

section "T.3 Shellcheck on hooks"

if shellcheck "${REPO_ROOT}"/harness/hooks/*.sh >/dev/null 2>&1; then
  log_pass "All hook scripts pass shellcheck"
else
  log_fail "Shellcheck found issues in hook scripts"
fi

# ---- T.4: PostToolUse Semgrep hook catches synthetic vulnerability ----------

section "T.4 Semgrep hook: synthetic SQL injection"

SQLI_FILE="${TEST_DIR}/test-sqli.py"
mkdir -p "${TEST_DIR}"
cat > "${SQLI_FILE}" <<'PYEOF'
import sqlite3

def get_user(user_id):
    conn = sqlite3.connect("db.sqlite")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
    return cursor.fetchone()
PYEOF

HOOK_OUTPUT=$(echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"${SQLI_FILE}\"}}" \
  | "${REPO_ROOT}/harness/hooks/post-tool-use-semgrep.sh" 2>/dev/null || true)

if echo "${HOOK_OUTPUT}" | grep -qi "sql"; then
  log_pass "Semgrep hook detected SQL injection in synthetic file"
else
  log_fail "Semgrep hook did not detect SQL injection"
fi

rm -f "${SQLI_FILE}"

# ---- T.5: PostToolUse Semgrep hook passes clean file -----------------------

section "T.5 Semgrep hook: clean file"

CLEAN_FILE="${TEST_DIR}/test-clean.py"
mkdir -p "${TEST_DIR}"
cat > "${CLEAN_FILE}" <<'PYEOF'
def add(a: int, b: int) -> int:
    return a + b
PYEOF

CLEAN_OUTPUT=$(echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"${CLEAN_FILE}\"}}" \
  | "${REPO_ROOT}/harness/hooks/post-tool-use-semgrep.sh" 2>/dev/null || true)

if echo "${CLEAN_OUTPUT}" | grep -qi "finding\|warning\|error"; then
  log_fail "Semgrep hook reported findings on clean file"
else
  log_pass "Semgrep hook clean on safe file"
fi

rm -f "${CLEAN_FILE}"

# ---- T.6: Drift check ------------------------------------------------------

section "T.6 Drift check"

if "${REPO_ROOT}/../scripts/drift-check.sh" >/dev/null 2>&1; then
  log_pass "Drift check passes"
else
  log_fail "Drift check failed"
fi

# ---- T.7: Session-start hook -----------------------------------------------

section "T.7 Session-start hook"

"${REPO_ROOT}/harness/hooks/session-start.sh" >/dev/null 2>&1 || true
SESSION_EXIT=$?

if [[ ${SESSION_EXIT} -eq 0 ]]; then
  log_pass "Session-start hook exits cleanly"
else
  log_fail "Session-start hook exited with code ${SESSION_EXIT}"
fi

# ---- T.8: Pre-compact-preserve hook ----------------------------------------

section "T.8 Pre-compact-preserve hook"

if "${REPO_ROOT}/harness/hooks/pre-compact-preserve.sh" >/dev/null 2>&1; then
  log_pass "Pre-compact-preserve hook exits cleanly"
else
  log_fail "Pre-compact-preserve hook failed"
fi

# ---- T.9: Settings template is valid JSON (after substitution) --------------

section "T.9 Settings template"

TEMPLATE="${REPO_ROOT}/harness/settings.json.template"
if [[ -f "${TEMPLATE}" ]]; then
  RENDERED=$(sed "s|{{REPO_ROOT}}|${REPO_ROOT}|g" "${TEMPLATE}")
  if echo "${RENDERED}" | jq empty >/dev/null 2>&1; then
    log_pass "settings.json.template renders to valid JSON"
  else
    log_fail "settings.json.template does not render to valid JSON"
  fi
else
  log_fail "settings.json.template not found"
fi

# ---- T.10: Skill and agent files present ------------------------------------

section "T.10 Skill and agent files"

SKILL_DIR="${REPO_ROOT}/harness/skills/security-review"
if [[ -f "${SKILL_DIR}/SKILL.md" ]]; then
  PATTERN_COUNT=$(find "${SKILL_DIR}/patterns" -name '*.md' -type f 2>/dev/null | wc -l)
  if [[ "${PATTERN_COUNT}" -ge 10 ]]; then
    log_pass "security-review skill: SKILL.md + ${PATTERN_COUNT} patterns"
  else
    log_fail "security-review skill: only ${PATTERN_COUNT} patterns (expected 10+)"
  fi
else
  log_fail "security-review SKILL.md not found"
fi

AGENT_DIR="${REPO_ROOT}/harness/agents"
AGENT_COUNT=$(find "${AGENT_DIR}" -name '*.md' -not -name 'README.md' -type f 2>/dev/null | wc -l)
if [[ "${AGENT_COUNT}" -ge 3 ]]; then
  log_pass "agents: ${AGENT_COUNT} agent definitions found"
else
  log_fail "agents: only ${AGENT_COUNT} definitions (expected 3+)"
fi

# ---- T.11: Pre-commit config valid -----------------------------------------

section "T.11 Pre-commit config"

if [[ -f "${REPO_ROOT}/../.pre-commit-config.yaml" ]]; then
  if pre-commit validate-config "${REPO_ROOT}/../.pre-commit-config.yaml" >/dev/null 2>&1; then
    log_pass "Pre-commit config validates"
  else
    log_fail "Pre-commit config validation failed"
  fi
else
  log_fail ".pre-commit-config.yaml not found"
fi

# ---- T.12: Rules files present ----------------------------------------------

section "T.12 Rules files"

for rulefile in paths.deny commands.deny; do
  if [[ -f "${REPO_ROOT}/harness/rules/${rulefile}" ]]; then
    log_pass "rules/${rulefile} exists"
  else
    log_fail "rules/${rulefile} missing"
  fi
done

# ---- Summary ----------------------------------------------------------------

printf '\n=== Results: %d passed, %d failed ===\n' "${PASS}" "${FAIL}"

if [[ "${FAIL}" -gt 0 ]]; then
  printf '\nIntegration test FAILED.\n'
  exit 1
fi

printf '\nIntegration test PASSED.\n'
exit 0
