#!/usr/bin/env bash
# session-start.sh
#
# Runs at every Claude Code SessionStart event. Surfaces drift between cited
# references and actual artifacts, and warns if the Claude Code version is
# outside the validated range.
#
# Quality Contract: QC.5 (versioning posture).
# Threat Model: T.7 (configuration drift).
#
# Jetson divergence from Mac: fixed version parsing. Mac uses awk $NF which
# grabs "Code)" from "2.1.143 (Claude Code)". Changed to $1 for the version.

set -uo pipefail

LOG_DIR="${HOME}/.claude-harness"
LOG_FILE="${LOG_DIR}/hook.log"
mkdir -p "${LOG_DIR}"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Validated Claude Code minor-version range. Update when QC.5 re-evaluation
# completes against a new minor version.
VALIDATED_RANGE_PREFIX="2.1."

log() {
  printf '%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >> "${LOG_FILE}"
}

# --- Drift check -------------------------------------------------------------

if [[ -x "${REPO_ROOT}/scripts/drift-check.sh" ]]; then
  if ! "${REPO_ROOT}/scripts/drift-check.sh" >/dev/null 2>&1; then
    log "WARN drift detected at session start"
    cat <<EOF
[session-start] Drift check failed. Run scripts/drift-check.sh manually to see details.
This is advisory at session start. Pre-commit will block commits with drift.
EOF
  else
    log "OK drift check passed at session start"
  fi
else
  log "SKIP drift-check.sh not executable at ${REPO_ROOT}/scripts/drift-check.sh"
fi

# --- Claude Code version check -----------------------------------------------

if command -v claude >/dev/null 2>&1; then
  CLAUDE_VERSION="$(claude --version 2>/dev/null | head -n1 | awk '{print $1}' || echo "unknown")"
  log "INFO claude_version=${CLAUDE_VERSION}"

  if [[ "${CLAUDE_VERSION}" != "${VALIDATED_RANGE_PREFIX}"* && "${CLAUDE_VERSION}" != "unknown" ]]; then
    cat <<EOF
[session-start] Claude Code version ${CLAUDE_VERSION} is outside the validated range (${VALIDATED_RANGE_PREFIX}x).
Per QC.5, minor-version bumps trigger Quality Contract re-evaluation. Verify before relying on the harness.
EOF
    log "WARN version_out_of_range=${CLAUDE_VERSION}"
  fi
fi

exit 0
