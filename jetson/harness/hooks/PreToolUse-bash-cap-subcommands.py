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

Verify (autonomous, 31-49 allowed, >=50 still denied):
    HARNESS_AUTONOMOUS_MODE=1 python3 -c '...35 chain...' | \
        HARNESS_AUTONOMOUS_MODE=1 python3 PreToolUse-bash-cap-subcommands.py
    # exit 0, stdout: permissionDecision=allow, log line appended.
    # A 60-chain still denies: HARD_CAP=49 binds because Adversa.ai 2026
    # documents per-subcommand deny-rule checks stop firing above 50.

Owner: harness-engineering (Phase 3, 2026-05-11; autonomous-mode bypass 2026-05-20)
"""
import json
import os
import sys
from datetime import datetime, timezone

CAP = 30
HARD_CAP = 49  # below the runtime's 50-subcommand fallback (Adversa.ai 2026)


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


# Autonomous-mode bypass: HARNESS_AUTONOMOUS_MODE=1 silences the deny
# between CAP and HARD_CAP. Above HARD_CAP the deny stands regardless of
# the flag: the Adversa.ai 2026 finding is that per-subcommand deny-rule
# checks stop firing above 50, which is an irreversible safety regression
# the autonomous flag is not allowed to opt out of. Trust anchor and
# logging behavior mirror the supply-chain hook; see
# foundation/01-threat-model.md "Autonomous mode trade."
_BYPASS_LOG = os.path.expanduser("~/.claude/hooks/autonomous-bypass.log")
_BYPASS_LOG_MAX = 1 << 20  # 1 MiB, single .1 backup on rotate


def _rotate_bypass_log() -> None:
    try:
        if os.path.exists(_BYPASS_LOG) and os.path.getsize(_BYPASS_LOG) >= _BYPASS_LOG_MAX:
            backup = _BYPASS_LOG + ".1"
            try:
                if os.path.exists(backup):
                    os.remove(backup)
            except OSError:
                pass
            os.rename(_BYPASS_LOG, backup)
    except OSError:
        pass


def autonomous_bypass(tool_name: str, command: str,
                      hook_name: str, reason: str) -> bool:
    if os.environ.get("HARNESS_AUTONOMOUS_MODE", "0") != "1":
        return False
    _rotate_bypass_log()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = "\t".join((ts, hook_name, tool_name,
                      command.replace("\n", "\\n"), reason)) + "\n"
    try:
        with open(_BYPASS_LOG, "a", encoding="utf-8") as f:
            f.write(line)
    except OSError:
        pass
    out = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "permissionDecisionReason": (
                f"HARNESS_AUTONOMOUS_MODE=1: silenced {hook_name} "
                f"({reason}). Logged to ~/.claude/hooks/autonomous-bypass.log."
            ),
            "additionalContext": (
                f"[autonomous] {hook_name} silenced for tool={tool_name}: "
                f"{reason}. Forensic log: ~/.claude/hooks/autonomous-bypass.log."
            ),
        }
    }
    print(json.dumps(out))
    return True


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
    if n <= CAP:
        return 0
    if n <= HARD_CAP and autonomous_bypass(
        tool_name="Bash",
        command=cmd,
        hook_name="PreToolUse-bash-cap-subcommands",
        reason=f"chain of {n} subcommands (cap {CAP}, hard cap {HARD_CAP})",
    ):
        return 0
    out = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                f"Bash chain has {n} subcommands; cap is {CAP} "
                f"(hard cap {HARD_CAP} under HARNESS_AUTONOMOUS_MODE=1, "
                f"Phase 2 Q6, foundation/01 Threat actors #4). "
                f"Adversa.ai 2026: per-subcommand deny-rule checks stop "
                f"firing above 50. Split into multiple Bash invocations."
            ),
        }
    }
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
