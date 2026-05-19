#!/usr/bin/env bash
# Hook: Stop-mempalace-diary-reminder
# Event: Stop
# Purpose: Remind the model to write a MemPalace diary entry once per session
#          before allowing the stop to proceed. Tracks via a session-scoped
#          marker so a second Stop call (after the diary write) passes cleanly.
#
# Threat: Same per-session amnesia threat the SessionStart hook addresses.
#         Without an exit-time enforcement, the diary step is the easiest
#         protocol step to silently skip.
#
# Decision: Deterministic block on first Stop per session, no LLM in the
#           loop. The marker file is keyed on session_id and lives under /tmp
#           so it self-cleans across reboots and never grows. If session_id
#           is unavailable in the payload (older Claude Code versions), the
#           hook falls through without blocking rather than wedging exits.
#
# Owner: harness-engineering (post-Phase 3 refinement, 2026-05-19)

set -uo pipefail

PAYLOAD="$(cat)"
SESSION_ID="$(printf '%s' "$PAYLOAD" | jq -r '.session_id // empty' 2>/dev/null || echo "")"

if [[ -z "$SESSION_ID" ]]; then
  exit 0
fi

MARKER="/tmp/mempalace-stop-reminded-${SESSION_ID}"
if [[ -f "$MARKER" ]]; then
  exit 0
fi

touch "$MARKER"
cat <<'EOF'
{"decision":"block","reason":"MemPalace protocol step 4: write a session diary before stopping. Call mempalace_diary_write with agent=\"claude-code-opus\", topic=<project-or-task>, entry in AAAK format (e.g. SESSION:YYYY-MM-DD|what.was.done|ROK.req:what.user.asked|outcomes|stars). After writing, you may stop. This reminder fires once per session."}
EOF
