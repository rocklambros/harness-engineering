#!/usr/bin/env bash
# post-tool-use-semgrep.sh
#
# Commit-time hardening hook. Runs after every Write, Edit, or MultiEdit by
# Claude Code against the file that was modified. Returns structured Semgrep
# findings on stdout so the model can see them and fix in the same session.
#
# This implements the methodology described in:
#   Liu, H., Einstein, L., Yang, J., et al. (2026). SecureForge: Finding and
#   Preventing Vulnerabilities in LLM-Generated Code via Prompt Optimization.
#   arXiv:2605.08382, Appendix C.
#
# Cited measurement: feedback-loop hardening reduced CWE rate by ~48% in the
# paper's evaluation on benign-prompt vulnerability generation. The hook is
# the deterministic-enforcement equivalent of Appendix C's prompt-level loop.
#
# Quality Contract: QC.1 (SSDF PW.7, PW.8).
# Architectural Principle: AP.2 (three-layer security, Layer 2).
# Threat Model: T.1 (benign-prompt vulnerability generation).
#
# Failure mode: fail closed per AP.8. If Semgrep is missing or the hook errors,
# exit non-zero so Claude Code surfaces the failure rather than silently
# allowing the write.

set -uo pipefail

# --- Configuration -----------------------------------------------------------

LOG_DIR="${HOME}/.claude-harness"
LOG_FILE="${LOG_DIR}/hook.log"
SEMGREP_CONFIG_DEFAULT="p/default"
SEMGREP_CONFIG_SECURITY="p/security-audit"
SEMGREP_TIMEOUT_SECONDS=45
MAX_FINDINGS_REPORTED=20

mkdir -p "${LOG_DIR}"

log() {
  # Append a structured line to the hook log. ISO-8601 timestamp.
  printf '%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >> "${LOG_FILE}"
}

# --- Read hook payload from stdin --------------------------------------------

# Claude Code sends a JSON payload describing the tool call. We extract the
# file path from the tool_input field. Schema (as of Claude Code v2.1.x):
#   { "tool_name": "Write" | "Edit" | "MultiEdit",
#     "tool_input": { "file_path": "...", ... }, ... }

PAYLOAD="$(cat 2>/dev/null || true)"

if [[ -z "${PAYLOAD}" ]]; then
  log "ERROR empty payload on stdin"
  echo "post-tool-use-semgrep: empty hook payload" >&2
  exit 2
fi

# Extract the file path. Use jq if available, fall back to a sed approximation
# only if jq is missing (jq is a hard dependency of the harness; document
# install in HARNESS_GUIDE.md).
if command -v jq >/dev/null 2>&1; then
  FILE_PATH="$(printf '%s' "${PAYLOAD}" | jq -r '.tool_input.file_path // empty')"
  TOOL_NAME="$(printf '%s' "${PAYLOAD}" | jq -r '.tool_name // "unknown"')"
else
  log "ERROR jq not installed, hook cannot parse payload"
  echo "post-tool-use-semgrep: jq is required. Install with 'brew install jq' on macOS." >&2
  exit 2
fi

if [[ -z "${FILE_PATH}" ]]; then
  log "WARN no file_path in payload for tool=${TOOL_NAME}, skipping"
  exit 0
fi

if [[ ! -f "${FILE_PATH}" ]]; then
  log "WARN file not on disk: ${FILE_PATH}"
  exit 0
fi

# Skip files outside scope. The hook is for code files, not generated docs.
# Extension allow-list keeps Semgrep runs cheap.
case "${FILE_PATH}" in
  *.py|*.pyx|*.pyi) ;;
  *.js|*.jsx|*.ts|*.tsx|*.mjs|*.cjs) ;;
  *.go|*.rs|*.rb|*.php|*.java|*.kt|*.scala) ;;
  *.sh|*.bash|*.zsh) ;;
  *.yaml|*.yml|*.json|*.toml) ;;
  *.tf|*.tfvars|*.hcl) ;;
  *.sql) ;;
  *.c|*.cpp|*.cc|*.h|*.hpp) ;;
  *)
    log "SKIP not in code-extension allow-list: ${FILE_PATH}"
    exit 0
    ;;
esac

# --- Pin to the isolated Semgrep, not conda or system Python -----------------

# The harness Semgrep lives in a dedicated pipx environment with its own
# pinned dependency set. A conda or Homebrew Python can shadow it on PATH,
# and the modern Semgrep launcher resolves its pysemgrep helper through PATH
# as well, so a drifted conda environment can break this gate even when the
# pinned environment is healthy. Prepend the pipx bin directory first, so
# both the launcher and pysemgrep resolve to the pinned environment. Set
# HARNESS_SEMGREP_BIN_DIR when pipx installs elsewhere.

HARNESS_SEMGREP_BIN_DIR="${HARNESS_SEMGREP_BIN_DIR:-${HOME}/.local/bin}"
if [[ -x "${HARNESS_SEMGREP_BIN_DIR}/semgrep" ]]; then
  PATH="${HARNESS_SEMGREP_BIN_DIR}:${PATH}"
  export PATH
fi

# --- Verify Semgrep is installed ---------------------------------------------

if ! command -v semgrep >/dev/null 2>&1; then
  log "ERROR semgrep not installed"
  echo "post-tool-use-semgrep: Semgrep is required but not on PATH." >&2
  echo "Install the pinned Semgrep with 'pipx install semgrep==1.162.0'." >&2
  echo "The harness fails closed per AP.8. Install Semgrep or remove this hook." >&2
  exit 2
fi

# --- Run Semgrep -------------------------------------------------------------

# macOS ships no GNU timeout. The earlier version hard-coded timeout and
# masked the resulting command-not-found with a trailing true, so a missing
# coreutils turned this gate into a silent no-op while misreporting the cause
# as a Semgrep install problem. Resolve a portable wall-clock bound. Prefer
# GNU timeout or gtimeout. Fall back to a perl fork and alarm shim, since
# perl is part of the macOS base system. Fail closed per AP.8 if none exist.

if command -v timeout >/dev/null 2>&1; then
  run_bounded() { timeout "${SEMGREP_TIMEOUT_SECONDS}" "$@"; }
elif command -v gtimeout >/dev/null 2>&1; then
  run_bounded() { gtimeout "${SEMGREP_TIMEOUT_SECONDS}" "$@"; }
elif command -v perl >/dev/null 2>&1; then
  run_bounded() {
    perl -e '
      my $s = shift;
      my $pid = fork();
      if (!defined $pid) { exit 127 }
      if ($pid == 0) { exec @ARGV or exit 127 }
      my $timed_out = 0;
      local $SIG{ALRM} = sub { kill "KILL", $pid; $timed_out = 1 };
      alarm $s;
      waitpid($pid, 0);
      my $st = $?;
      alarm 0;
      exit 124 if $timed_out;
      exit($st >> 8);
    ' "${SEMGREP_TIMEOUT_SECONDS}" "$@"
  }
else
  log "ERROR no timeout, gtimeout, or perl to bound the run"
  echo "post-tool-use-semgrep: no timeout, gtimeout, or perl to bound the run." >&2
  echo "Install coreutils with 'brew install coreutils'. Fails closed per AP.8." >&2
  exit 2
fi

log "RUN file=${FILE_PATH} tool=${TOOL_NAME}"

# Both rule packs. JSON output is parsed by jq for stable extraction. No
# trailing true, so the command substitution exit status reflects the real
# Semgrep or runner result. That keeps the timeout case, exit 124, distinct
# from a genuine no-output failure. set -uo pipefail without -e keeps the
# script from aborting on the non-zero exit here.
SEMGREP_OUTPUT="$(run_bounded semgrep \
  --config "${SEMGREP_CONFIG_DEFAULT}" \
  --config "${SEMGREP_CONFIG_SECURITY}" \
  --json \
  --quiet \
  --error \
  --skip-unknown-extensions \
  "${FILE_PATH}" 2>/dev/null)"
SEMGREP_EXIT=$?

if [[ "${SEMGREP_EXIT}" -eq 124 ]]; then
  log "ERROR semgrep timed out after ${SEMGREP_TIMEOUT_SECONDS}s file=${FILE_PATH}"
  echo "post-tool-use-semgrep: Semgrep timed out after ${SEMGREP_TIMEOUT_SECONDS}s." >&2
  exit 2
fi

if [[ -z "${SEMGREP_OUTPUT}" ]]; then
  log "ERROR semgrep no output (exit=${SEMGREP_EXIT}) file=${FILE_PATH}"
  echo "post-tool-use-semgrep: Semgrep produced no output (exit=${SEMGREP_EXIT})." >&2
  echo "Run 'semgrep --version' to diagnose. Fails closed per AP.8." >&2
  exit 2
fi

# Parse findings count.
FINDINGS_COUNT="$(printf '%s' "${SEMGREP_OUTPUT}" | jq '.results | length' 2>/dev/null || echo "0")"

if [[ "${FINDINGS_COUNT}" == "0" ]]; then
  log "OK no findings file=${FILE_PATH}"
  exit 0
fi

# --- Format findings for the model -------------------------------------------

# Emit findings on stdout in a compact format the model can act on. Include
# rule ID, line, severity, and a short message. Truncate at MAX_FINDINGS to
# avoid context blowout on heavily-flagged files.

log "FINDINGS count=${FINDINGS_COUNT} file=${FILE_PATH}"

cat <<EOF
Semgrep findings in ${FILE_PATH} (${FINDINGS_COUNT} total, showing first ${MAX_FINDINGS_REPORTED}):

EOF

printf '%s' "${SEMGREP_OUTPUT}" | jq -r \
  --argjson max "${MAX_FINDINGS_REPORTED}" \
  '.results[:$max] | .[] |
   "[\(.extra.severity // "INFO")] \(.check_id)
   line \(.start.line): \(.extra.message // "no message")
   "'

cat <<EOF

This is the commit-time hardening loop (SecureForge Appendix C pattern).
Fix these findings in the same session, then re-write the file. The hook will
re-run and report whether the issues are resolved.

Do not suppress findings with comments unless the suppression has a stated
justification that ties to a Quality Contract decision.
EOF

# Hook exits 0 (success). The exit code does not block the write; it surfaces
# the findings to the model. Blocking writes is a different security model
# that would require a PreToolUse hook with the same logic.
exit 0
