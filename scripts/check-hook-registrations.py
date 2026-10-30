#!/usr/bin/env python3
"""Drift check 6: hook registrations agree across the three settings sources.

Compares the hooks registered in the Mac reference file
(mac/harness/settings.json), the adopter template
(mac/harness/settings.json.template), and the live user settings
(~/.claude/settings.json, when present) as sets of
(event, matcher, hook basename). Each source is allowed a documented set of
extras; anything else that differs is drift. The five destructive-class
hooks must carry onFailure: block, the exec form under python3 -I, and a
timeout, in every source that registers them.

Exit 0 when the sets agree, 1 on drift, 2 on a script error. Called from
scripts/drift-check.sh.

Owner: harness-engineering (October 30, 2026)
"""

import json
import os
import sys

import platform

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIVE = os.path.join(
    os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude"),
    "settings.json",
)


def _platform() -> str:
    # Same detection as drift-check.sh: Darwin is the Mac reference build,
    # aarch64 Linux is the Jetson. Anything else compares against the Mac
    # sources.
    if platform.system() == "Linux" and platform.machine() == "aarch64":
        return "jetson"
    return "mac"


PLATFORM = _platform()
REFERENCE = os.path.join(REPO, "mac", "harness", "settings.json")
TEMPLATE = os.path.join(REPO, PLATFORM, "harness", "settings.json.template")

# Hooks each source may carry that the others do not. Everything else must
# match. Update this table in the same commit that adds a source-specific
# hook, so the exception is a decision and not an accident.
REFERENCE_ONLY = {
    "SessionStart-mempalace-protocol.sh",
    "Stop-mempalace-diary-reminder.sh",
}
TEMPLATE_ONLY = {
    "post-tool-use-semgrep.sh",
    "pre-tool-use-shell-audit.sh",
    "session-start.sh",
    "pre-compact-preserve.sh",
}
LIVE_ONLY_BY_PLATFORM = {
    # The Mac reference host: attribution guard, config backup, Semgrep
    # feedback, the hardened security-guidance fork, the watermarks cleaner.
    "mac": {
        "PreToolUse-no-ai-attribution.sh",
        "backup-config.sh",
        "PostToolUse-semgrep.sh",
        "security_reminder_hook.py",
        "hook_written_file.py",
    },
    # The Jetson: add a name here in the same commit that registers a
    # Jetson-only hook in its live settings, so the exception is a decision.
    "jetson": set(),
}
LIVE_ONLY = LIVE_ONLY_BY_PLATFORM[PLATFORM]
DESTRUCTIVE = {
    "PreToolUse-external-write-gate.py",
    "PreToolUse-cached-prefix-write-gate.py",
    "PreToolUse-git-push-force-ask.py",
    "PreToolUse-bash-deny-rm-protected-paths.py",
    "ConfigChange-audit-claude-config.py",
}


def basename_of(entry: dict) -> str:
    path = (
        entry.get("args", [None])[-1] if entry.get("args") else entry.get("command", "")
    )
    if path is None:
        path = entry.get("command", "")
    return os.path.basename(path.strip('"').split()[-1]) if path else ""


def registrations(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    found = {}
    for event, groups in (data.get("hooks") or {}).items():
        if event.startswith("_") or not isinstance(groups, list):
            continue
        for group in groups:
            if not isinstance(group, dict):
                continue
            # No matcher and "*" both mean every occurrence of the event.
            matcher = group.get("matcher") or "*"
            for entry in group.get("hooks", []):
                if not isinstance(entry, dict) or entry.get("type") != "command":
                    continue
                name = basename_of(entry)
                found[(event, matcher, name)] = entry
    return found


def main() -> int:
    # The Mac reference file is a Mac source. On the Jetson the template is
    # the only tracked source and the live file is compared against it.
    sources = {"template": (TEMPLATE, TEMPLATE_ONLY)}
    if PLATFORM == "mac":
        sources = {"reference": (REFERENCE, REFERENCE_ONLY), **sources}
    if os.path.isfile(LIVE):
        sources["live"] = (LIVE, LIVE_ONLY)
    regs = {}
    for label, (path, _) in sources.items():
        try:
            regs[label] = registrations(path)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"error: cannot read {path}: {exc}", file=sys.stderr)
            return 2
    drift = []
    harness_sets = {}
    for label, (_, extras) in sources.items():
        harness_sets[label] = {
            k
            for k in regs[label]
            if k[2] not in extras
            and k[2] not in REFERENCE_ONLY | TEMPLATE_ONLY | LIVE_ONLY
        }
    labels = list(sources)
    for i, a in enumerate(labels):
        for b in labels[i + 1 :]:
            for key in sorted(harness_sets[a] - harness_sets[b]):
                drift.append(
                    f"{a} registers {key[2]} on {key[0]} ({key[1] or 'no matcher'}) and {b} does not"
                )
            for key in sorted(harness_sets[b] - harness_sets[a]):
                drift.append(
                    f"{b} registers {key[2]} on {key[0]} ({key[1] or 'no matcher'}) and {a} does not"
                )
    for label in labels:
        for key, entry in regs[label].items():
            if key[2] in DESTRUCTIVE:
                if entry.get("onFailure") != "block":
                    drift.append(f"{label}: {key[2]} lacks onFailure: block")
                if entry.get("command") != "python3" or "-I" not in (
                    entry.get("args") or []
                ):
                    drift.append(
                        f"{label}: {key[2]} is not registered as python3 -I (exec form)"
                    )
                if not entry.get("timeout"):
                    drift.append(f"{label}: {key[2]} has no timeout")
        present = {k[2] for k in regs[label]}
        for name in sorted(DESTRUCTIVE - present):
            drift.append(f"{label}: destructive-class hook {name} is not registered")
    for line in drift:
        print(f"drift: {line}")
    if drift:
        return 1
    print(
        f"hook registrations agree across {', '.join(labels)} ({len(harness_sets[labels[0]])} shared harness hooks, {PLATFORM})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
