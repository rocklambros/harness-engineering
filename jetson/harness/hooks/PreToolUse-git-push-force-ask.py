#!/usr/bin/env python3
"""
Hook: PreToolUse-git-push-force-ask
Event: PreToolUse
Purpose: Ask for confirmation on git push --force, -f, and --force-with-lease.

Threat: foundation/02-architectural-principles.md Principle 3 (reversibility-
        weighted risk). A force-push overwrites remote history. Local branch
        protection can roll it back if reflog or backups exist, but the
        operation crosses a trust boundary into the shared GitHub remote,
        which the harness treats as out-of-band reversibility.

        Also foundation/01-threat-model.md Asset #1 (source code integrity).
        The most common harness-fault scenario for source-code integrity is
        an automated push of stale or wrong history.

Decision: Operationally, the operator (Rock) is the sole contributor on
          several public repos with branch protection that requires PRs to
          merge to main. The legitimate workflow includes admin-bypass
          pushes (git push --force, git push --force-with-lease) directly
          to main when there is no reviewer. The original posture was deny
          (post-launch revision 2026-05-12 converts deny to ask). The
          conversion preserves the deterministic floor through hook-
          mediated ask: every force-push invocation by the model fires
          this hook and gets an interactive prompt. The operator confirms
          per invocation rather than removing the rule for the session.

          Three patterns covered:
          - git push --force
          - git push -f
          - git push --force-with-lease

          --force-with-lease is included because the lease check protects
          only against losing intermediate commits. An unauthorized push
          of new history still happens, and the asymmetry between local
          intent and remote outcome is the same. The operator still gets
          asked.

Out of scope: Operator-initiated force-push from the terminal (outside
              Claude Code) is not governed by this hook. The hook fires
              on tool calls the model proposes during a session. Terminal-
              direct invocations pass through normally.

Verify (allow):
    echo '{"tool_name":"Bash","tool_input":{"command":"git push origin main"}}' | \\
        python3 PreToolUse-git-push-force-ask.py
    # exit 0, empty stdout

Verify (ask, --force):
    echo '{"tool_name":"Bash","tool_input":{"command":"git push --force origin main"}}' | \\
        python3 PreToolUse-git-push-force-ask.py
    # exit 0, stdout: permissionDecision=ask

Verify (ask, -f):
    echo '{"tool_name":"Bash","tool_input":{"command":"git push -f origin main"}}' | \\
        python3 PreToolUse-git-push-force-ask.py
    # exit 0, stdout: permissionDecision=ask

Verify (ask, --force-with-lease):
    echo '{"tool_name":"Bash","tool_input":{"command":"git push --force-with-lease origin main"}}' | \\
        python3 PreToolUse-git-push-force-ask.py
    # exit 0, stdout: permissionDecision=ask

Owner: harness-engineering (Post-launch revision, 2026-05-12. Originally
       bash-deny-git-push-force deny rule from Phase 3, 2026-05-11.)
"""
import json
import re
import sys

# Match git push followed by --force, --force-with-lease, or -f (as a token).
# Anchored to the command head to avoid matching strings inside quoted args.
PATTERNS = [
    re.compile(r"^\s*git\s+push\s+(?:[^-]\S*\s+)*--force(?:\s|$)"),
    re.compile(r"^\s*git\s+push\s+(?:[^-]\S*\s+)*--force-with-lease(?:\s|$)"),
    re.compile(r"^\s*git\s+push\s+(?:[^-]\S*\s+)*-f(?:\s|$)"),
]


def matches_force_push(cmd: str) -> str:
    for pat in PATTERNS:
        if pat.search(cmd):
            return pat.pattern
    return ""


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    if data.get("tool_name") != "Bash":
        return 0
    cmd = data.get("tool_input", {}).get("command", "")
    if not cmd:
        return 0
    matched = matches_force_push(cmd)
    if not matched:
        return 0
    out = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": (
                "git push force variant detected. The harness asks for "
                "confirmation on model-proposed force-push to give the "
                "operator a chance to confirm intent (Principle 3 "
                "reversibility, foundation/01 Asset #1 source code "
                "integrity). The operator's terminal-direct invocations "
                "are out of scope. Confirm or deny."
            ),
        }
    }
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
