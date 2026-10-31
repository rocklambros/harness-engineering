#!/usr/bin/env python3
"""Drift check 7: live settings carry every deny and ask rule the platform ships.

deploy-harness.sh diffs only the hooks block, and check 6 reads only hooks,
so a deny or ask rule dropped from ~/.claude/settings.json went unnoticed.
This reports each permissions.deny and permissions.ask rule in the platform
settings source that the live file lacks. The source is picked the way
deploy-harness.sh picks it: settings.json first, then settings.json.template.

Allow rules are not checked on purpose. The source's allows are project
scope (Read(./**) and similar) and must not be pushed to user level, so
their absence from the live file is correct, not drift.

Exit 0 when every rule is present or there is no live file, 1 on drift, 2
on a script error. Called from scripts/drift-check.sh.

Owner: harness-engineering (October 30, 2026)
"""

import json
import os
import platform
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIVE = os.path.join(
    os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude"),
    "settings.json",
)
CHECKED = ("deny", "ask")


def _platform() -> str:
    # Same detection as drift-check.sh. Hosts it does not name compare
    # against the Mac reference, as check 6 does.
    system = platform.system()
    if system == "Linux" and platform.machine() == "aarch64":
        return "jetson"
    if system.startswith(("MINGW", "MSYS", "CYGWIN")) or system == "Windows":
        return "windows"
    return "mac"


def source_path(plat: str) -> str:
    for name in ("settings.json", "settings.json.template"):
        path = os.path.join(REPO, plat, "harness", name)
        if os.path.isfile(path):
            return path
    return ""


def rules(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        perms = json.load(f).get("permissions") or {}
    return {kind: list(perms.get(kind) or []) for kind in CHECKED}


def main() -> int:
    plat = _platform()
    source = source_path(plat)
    if not source:
        print(
            f"error: no settings source under {REPO}/{plat}/harness/", file=sys.stderr
        )
        return 2
    if not os.path.isfile(LIVE):
        print(f"no live settings at {LIVE}, permission rule check skipped")
        return 0
    try:
        want, have = rules(source), rules(LIVE)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: cannot read settings: {exc}", file=sys.stderr)
        return 2
    drift = [
        f"live settings.json lacks permissions.{kind} rule {rule} from {os.path.relpath(source, REPO)}"
        for kind in CHECKED
        for rule in want[kind]
        if rule not in have[kind]
    ]
    for line in drift:
        print(f"drift: {line}")
    if drift:
        return 1
    counts = ", ".join(f"{len(want[k])} {k}" for k in CHECKED)
    print(f"live permissions carry every {plat} source rule ({counts})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
