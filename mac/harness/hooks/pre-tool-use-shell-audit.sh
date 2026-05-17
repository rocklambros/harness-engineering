#!/usr/bin/env bash
# pre-tool-use-shell-audit.sh
#
# Logs shell command invocations before Claude Code executes them. Audit only,
# does not block. The deny patterns in settings.json handle blocking.
#
# Quality Contract: QC.1 (audit trail for PW.7 review).
# Threat Model: T.2 (prompt injection through agent inputs), T.4 (hook bypass).
# Architectural Principle: AP.8 (fail closed on internal errors).

set -uo pipefail

LOG_DIR="${HOME}/.claude-harness"
LOG_FILE="${LOG_DIR}/shell-audit.log"
mkdir -p "${LOG_DIR}"

PAYLOAD="$(cat 2>/dev/null || true)"

if [[ -z "${PAYLOAD}" ]]; then
  # Empty payload is unusual but not blocking. Log and continue.
  printf '%s\tWARN\tempty payload\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "${LOG_FILE}"
  exit 0
fi

if command -v jq >/dev/null 2>&1; then
  COMMAND="$(printf '%s' "${PAYLOAD}" | jq -r '.tool_input.command // empty')"
  DESCRIPTION="$(printf '%s' "${PAYLOAD}" | jq -r '.tool_input.description // empty')"
else
  printf '%s\tERROR\tjq not installed\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "${LOG_FILE}"
  echo "pre-tool-use-shell-audit: jq is required. Install with 'brew install jq'." >&2
  exit 2
fi

if [[ -z "${COMMAND}" ]]; then
  exit 0
fi

# Log: timestamp, description (one line), command (escaped newlines).
COMMAND_ESCAPED="${COMMAND//$'\n'/\\n}"
printf '%s\tAUDIT\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${DESCRIPTION}" "${COMMAND_ESCAPED}" >> "${LOG_FILE}"

exit 0
