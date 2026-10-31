#!/usr/bin/env python3
"""Drift check 6: hook registrations agree across the three settings sources.

Compares the hooks registered in the Mac reference file
(mac/harness/settings.json), the adopter template
(mac/harness/settings.json.template), and the live user settings
(~/.claude/settings.json, when present) as sets of
(event, matcher, hook basename). Each source is allowed a documented set of
extras; anything else that differs is drift. The six fail-closed
hooks must carry onFailure: block, the exec form under python3 -I, and a
timeout, in every source that registers them. Every live registration
must point at a script file that exists.

The live side also reads root-owned managed settings. A hook registered
there counts as live, must use an absolute interpreter, and must not also
appear in the user file, where it would run twice.

Run its matrix with python3 -I scripts/tests/test_check_hook_registrations.py.

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
# Root-owned managed policy, where scripts/install-managed-gates.sh registers
# the gates. A gate registered here satisfies the live requirement, and the
# same gate also in the user file is drift, since it runs twice for no added
# protection (operator decision, October 31, 2026). HARNESS_MANAGED_DIR is a
# test seam. This check reports, it does not enforce, so redirecting it can
# hide drift but cannot switch a gate off.
MANAGED_DIR = os.environ.get("HARNESS_MANAGED_DIR") or {
    "Darwin": "/Library/Application Support/ClaudeCode",
    "Windows": r"C:\Program Files\ClaudeCode",
}.get(platform.system(), "/etc/claude-code")
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
    # Not destructive itself, but its hard cap is the floor that keeps
    # per-subcommand deny rules firing (operator decision, October 31, 2026).
    "PreToolUse-bash-cap-subcommands.py",
}


def basename_of(entry: dict) -> str:
    path = (
        entry.get("args", [None])[-1] if entry.get("args") else entry.get("command", "")
    )
    if path is None:
        path = entry.get("command", "")
    return os.path.basename(path.strip('"').split()[-1]) if path else ""


def script_path_of(entry: dict) -> str:
    # The same token basename_of reads, with ~ and $HOME expanded. Only those
    # two are expanded: a path that still carries another variable cannot be
    # resolved here and returns "" rather than a false missing-file report.
    raw = (entry.get("args") or [entry.get("command") or ""])[-1] or ""
    token = raw.strip('"').split()[-1] if raw.strip() else ""
    home = os.path.expanduser("~")
    token = token.replace("${HOME}", home).replace("$HOME", home)
    token = os.path.expanduser(token)
    if "$" in token or not os.path.isabs(token):
        return ""
    return token


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


def managed_registrations() -> dict:
    # Same file set Claude Code merges: the base file, then the drop-ins in
    # name order.
    paths = [os.path.join(MANAGED_DIR, "managed-settings.json")]
    dropins = os.path.join(MANAGED_DIR, "managed-settings.d")
    if os.path.isdir(dropins):
        paths += [
            os.path.join(dropins, n)
            for n in sorted(os.listdir(dropins))
            if n.endswith(".json")
        ]
    found = {}
    for path in paths:
        if os.path.isfile(path):
            found.update(registrations(path))
    return found


def fail_closed_drift(label: str, key: tuple, entry: dict, interpreter_ok) -> list:
    drift = []
    if entry.get("onFailure") != "block":
        drift.append(f"{label}: {key[2]} lacks onFailure: block")
    if not interpreter_ok(entry.get("command", "")) or "-I" not in (
        entry.get("args") or []
    ):
        drift.append(f"{label}: {key[2]} is not registered as python3 -I (exec form)")
    if not entry.get("timeout"):
        drift.append(f"{label}: {key[2]} has no timeout")
    return drift


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
    managed = {}
    if "live" in regs:
        try:
            managed = managed_registrations()
        except (OSError, json.JSONDecodeError) as exc:
            print(f"error: cannot read managed settings: {exc}", file=sys.stderr)
            return 2
        user = {(k[0], k[2]) for k in regs["live"]}
        for key in sorted(managed):
            if (key[0], key[2]) in user:
                drift.append(
                    f"{key[2]} on {key[0]} is registered in both managed and user "
                    f"settings; remove the user copy"
                )
        # Managed entries count as live for the template comparison and the
        # presence check below. Their interpreter rule is checked here: the
        # installer pins an absolute path so a python3 planted earlier on
        # PATH cannot run in its place.
        for key, entry in managed.items():
            if key[2] in DESTRUCTIVE:
                drift += fail_closed_drift(
                    "managed",
                    key,
                    entry,
                    lambda c: os.path.basename(c) == "python3",
                )
                if not os.path.isabs(entry.get("command", "")):
                    drift.append(
                        f"managed: {key[2]} needs an absolute interpreter path"
                    )
        regs["live"] = {**regs["live"], **managed}
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
            if key[2] in DESTRUCTIVE and not (label == "live" and key in managed):
                drift += fail_closed_drift(label, key, entry, lambda c: c == "python3")
        present = {k[2] for k in regs[label]}
        for name in sorted(DESTRUCTIVE - present):
            drift.append(f"{label}: destructive-class hook {name} is not registered")
    # Matching names prove nothing when the registered file is gone: Claude
    # Code then fails the hook on every event. Live paths are absolute after
    # deploy. Template paths carry {{REPO_ROOT}} and cannot be resolved.
    if "live" in regs:
        for key, entry in sorted(regs["live"].items()):
            script = script_path_of(entry)
            if script and not os.path.isfile(script):
                drift.append(
                    f"live: {key[2]} on {key[0]} is registered at {script}, which does not exist"
                )
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
