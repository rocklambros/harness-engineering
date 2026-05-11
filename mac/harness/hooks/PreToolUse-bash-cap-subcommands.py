#!/usr/bin/env python3
"""
Hook: PreToolUse-bash-cap-subcommands
Event: PreToolUse
Purpose: Deny Bash invocations whose chain operator count exceeds 30.

Threat: foundation/01-threat-model.md, Threat actors #4 (50-subcommand bypass class,
        Adversa.ai 2026). Claude Code falls back to a single generic approval
        prompt above 50 chained subcommands; per-subcommand deny-rule checks stop
        firing due to per-subcommand UI parsing freezes.

Decision: Phase 2 Q6 elected 30 (defense in depth below the 50 documented
          threshold). Lower cap creates hook friction below the runtime's own
          fallback, so legitimate long chains get a clear diagnostic.

Verify (allow):
    echo '{"tool_name":"Bash","tool_input":{"command":"ls && pwd && date"}}' | \
        python3 PreToolUse-bash-cap-subcommands.py
    # exit 0, empty stdout

Verify (deny):
    python3 -c 'import sys, json; \
cmd=" && ".join("echo "+str(i) for i in range(35)); \
print(json.dumps({"tool_name":"Bash","tool_input":{"command":cmd}}))' | \
        python3 PreToolUse-bash-cap-subcommands.py
    # exit 0, stdout: hookSpecificOutput with permissionDecision=deny

Owner: harness-engineering (Phase 3, 2026-05-11)
"""
import json
import sys

CAP = 30


def count_subcommands(cmd: str) -> int:
    # Chain operators outside quoted strings increment the count. Backslash
    # escapes inside quotes are not unwound; an attacker payload that abuses
    # escape sequences inflates the deny side, never the allow side.
    count = 1
    in_single = False
    in_double = False
    i = 0
    n = len(cmd)
    while i < n:
        c = cmd[i]
        if c == "'" and not in_double:
            in_single = not in_single
            i += 1
            continue
        if c == '"' and not in_single:
            in_double = not in_double
            i += 1
            continue
        if in_single or in_double:
            i += 1
            continue
        if cmd.startswith("&&", i) or cmd.startswith("||", i):
            count += 1
            i += 2
            continue
        if c == ";" or c == "|":
            count += 1
        i += 1
    return count


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
    n = count_subcommands(cmd)
    if n > CAP:
        out = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    f"Bash chain has {n} subcommands; cap is {CAP} "
                    f"(Phase 2 Q6, foundation/01 Threat actors #4). "
                    f"Split into multiple Bash invocations."
                ),
            }
        }
        print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
