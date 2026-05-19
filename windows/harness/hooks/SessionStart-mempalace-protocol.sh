#!/usr/bin/env bash
# Hook: SessionStart-mempalace-protocol
# Event: SessionStart
# Purpose: Re-anchor the MemPalace protocol at the start of every session.
#
# Threat: Per-session amnesia. The MemPalace plugin is enabled and the palace
#         carries cross-session knowledge, but without an explicit protocol
#         reminder the model defaults to auto-memory and never escalates to
#         MemPalace for structured cross-session decisions. Observed
#         2026-05-19: an entire session passed with zero deliberate MemPalace
#         calls until the user surfaced the gap.
#
# Decision: Inject a slim protocol reminder as additionalContext on every
#           SessionStart, not the full mempalace_status response (which is
#           large and would inflate the cached prefix against QC.4b). The Stop
#           hook enforces the diary write half of the protocol.
#
# Owner: harness-engineering (post-Phase 3 refinement, 2026-05-19)

set -uo pipefail

cat <<'EOF'
{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "MemPalace protocol active. 1) Before answering about any past person/project/event, call mempalace_search or mempalace_kg_query first; never guess. 2) For structured cross-session decisions (architecture, security, design rationale), file via mempalace_kg_add plus mempalace_add_drawer (wing=project name, room=decisions). 3) Before ending the session, call mempalace_diary_write (agent=claude-code-opus, topic=project-or-task, entry in AAAK format). The Stop hook will block exit once per session if no diary write has occurred."}}
EOF
