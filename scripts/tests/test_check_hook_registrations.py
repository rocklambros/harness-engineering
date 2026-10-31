#!/usr/bin/env python3
"""Verification matrix for scripts/check-hook-registrations.py.

Run from the repo root:
    python3 -I scripts/tests/test_check_hook_registrations.py

Each case builds a live settings file from this platform's tracked template
under a temporary CLAUDE_CONFIG_DIR, and a managed drop-in under a temporary
HARNESS_MANAGED_DIR, so nothing reads the host's real settings or managed
policy. The managed cases cover the October 31, 2026 decision that a gate
registered in managed settings satisfies the live requirement, and that the
same gate registered in both places is drift. Exit status is 0 when every
case matches.

Owner: harness-engineering (October 31, 2026)
"""

import atexit
import copy
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CHECKER = os.path.join(REPO, "scripts", "check-hook-registrations.py")
PLATFORM = (
    "jetson"
    if platform.system() == "Linux" and platform.machine() == "aarch64"
    else "mac"
)
TEMPLATE = os.path.join(REPO, PLATFORM, "harness", "settings.json.template")

FAIL_CLOSED = [
    ("PreToolUse", "Bash", "PreToolUse-bash-deny-rm-protected-paths.py"),
    ("PreToolUse", "Bash", "PreToolUse-git-push-force-ask.py"),
    ("PreToolUse", "Bash", "PreToolUse-bash-cap-subcommands.py"),
    (
        "PreToolUse",
        "Write|Edit|MultiEdit|NotebookEdit",
        "PreToolUse-external-write-gate.py",
    ),
    (
        "PreToolUse",
        "Write|Edit|MultiEdit|NotebookEdit",
        "PreToolUse-cached-prefix-write-gate.py",
    ),
    (
        "ConfigChange",
        "project_settings|local_settings",
        "ConfigChange-audit-claude-config.py",
    ),
]
ADVISORY = [("PreToolUse", "Bash", "PreToolUse-supply-chain-bash-checks.py")]
MANAGED_NAMES = {g[2] for g in FAIL_CLOSED + ADVISORY}

# The drop-in's hook paths must point somewhere that EXISTS, because the
# checker reports a registered-but-missing script as drift (commit 7b0eb25).
# This was the install path /usr/local/lib/claude-harness/hooks, which exists
# only on a host that has already run install-managed-gates.sh. The suite then
# passed on the Jetson and reported 5/6 on the Mac, where all seven paths are
# absent, which contradicts this file's own promise that nothing reads the
# host's real settings or managed policy. A temporary directory holding the
# seven names keeps every case meaningful on any host, installed or not.
# Skipping the case when the path is absent would have hidden the Mac result.
MANAGED_LIB = tempfile.mkdtemp(prefix="harness-managed-lib-")
for _name in MANAGED_NAMES:
    with open(os.path.join(MANAGED_LIB, _name), "w", encoding="utf-8") as _f:
        _f.write("#!/usr/bin/env python3\n")
atexit.register(shutil.rmtree, MANAGED_LIB, True)


def template():
    with open(TEMPLATE, encoding="utf-8") as f:
        return json.load(f)


def strip(settings, names):
    """Drop every registration whose script basename is in names."""
    out = copy.deepcopy(settings)
    for groups in out.get("hooks", {}).values():
        if not isinstance(groups, list):
            continue
        for g in groups:
            g["hooks"] = [
                h
                for h in g.get("hooks", [])
                if os.path.basename(
                    ((h.get("args") or [h.get("command", "")])[-1]).split()[-1]
                )
                not in names
            ]
    return out


def dropin(fail_closed_entry=None, python="/usr/bin/python3"):
    """The drop-in install-managed-gates.sh writes, with optional overrides."""
    lib = MANAGED_LIB
    hooks = {}
    for cls, gates in (("fail-closed", FAIL_CLOSED), ("advisory", ADVISORY)):
        for event, matcher, script in gates:
            entry = {
                "type": "command",
                "command": python,
                "args": ["-I", f"{lib}/{script}"],
                "timeout": 10,
            }
            if cls == "fail-closed":
                entry["onFailure"] = "block"
                if fail_closed_entry:
                    entry.update(fail_closed_entry)
                    entry = {k: v for k, v in entry.items() if v is not None}
            groups = hooks.setdefault(event, [])
            for g in groups:
                if g["matcher"] == matcher:
                    g["hooks"].append(entry)
                    break
            else:
                groups.append({"matcher": matcher, "hooks": [entry]})
    return {"hooks": hooks}


def run(live, managed):
    with tempfile.TemporaryDirectory() as cfg, tempfile.TemporaryDirectory() as mgd:
        with open(os.path.join(cfg, "settings.json"), "w", encoding="utf-8") as f:
            json.dump(live, f)
        if managed is not None:
            os.makedirs(os.path.join(mgd, "managed-settings.d"))
            path = os.path.join(mgd, "managed-settings.d", "50-harness-gates.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(managed, f)
        env = dict(os.environ, CLAUDE_CONFIG_DIR=cfg, HARNESS_MANAGED_DIR=mgd)
        r = subprocess.run(
            [sys.executable, "-I", CHECKER],
            capture_output=True,
            text=True,
            env=env,
            cwd=REPO,
        )
        return r.returncode, r.stdout + r.stderr


CASES = [
    # (name, live, managed, expected rc, substring that must appear)
    ("user only, no managed", template(), None, 0, "agree"),
    (
        "managed holds the seven, user copies removed",
        strip(template(), MANAGED_NAMES),
        dropin(),
        0,
        "agree",
    ),
    (
        "user copies removed, no managed",
        strip(template(), MANAGED_NAMES),
        None,
        1,
        "is not registered",
    ),
    (
        "same gate in managed and user",
        template(),
        dropin(),
        1,
        "registered in both managed and user settings",
    ),
    (
        "managed gate without onFailure block",
        strip(template(), MANAGED_NAMES),
        dropin({"onFailure": None}),
        1,
        "lacks onFailure: block",
    ),
    (
        "managed gate on a PATH-resolved python3",
        strip(template(), MANAGED_NAMES),
        dropin(python="python3"),
        1,
        "absolute interpreter",
    ),
]


def main() -> int:
    fails = 0
    for name, live, managed, want_rc, want_text in CASES:
        rc, out = run(live, managed)
        ok = rc == want_rc and want_text in out
        fails += not ok
        print(f"{'PASS' if ok else 'FAIL'}  {name}  (rc={rc})")
        if not ok:
            print("      " + out.strip().replace("\n", "\n      "))
    print(f"{len(CASES) - fails}/{len(CASES)} cases passed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
