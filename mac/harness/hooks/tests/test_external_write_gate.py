#!/usr/bin/env python3
"""Verification matrix for PreToolUse-external-write-gate.py.

Run from the repo root with the hook path as the only argument:
    python3 -I mac/harness/hooks/tests/test_external_write_gate.py \
        mac/harness/hooks/PreToolUse-external-write-gate.py

Each case pipes a PreToolUse payload through the hook as a subprocess. The
"allow" expectation means exit 0 with empty stdout (the hook stays silent
and the permission mode decides). The "ask" expectation means exit 0 with a
permissionDecision of ask on stdout. Cases are built from the running
account's home and, on macOS, the per-user temp directory from getconf, so
the same file passes on Mac and Jetson. Exit status is 0 when every case
matches.

Owner: harness-engineering (October 30, 2026)
"""

import json
import os
import re
import subprocess
import sys
import tempfile

HOOK = sys.argv[1]
HOME = os.path.abspath(os.path.expanduser("~"))
CWD = os.path.join(HOME, "proj")
DARWIN = sys.platform == "darwin"
TMPDIR = (
    (os.environ.get("TMPDIR", "").rstrip("/") + "/") if os.environ.get("TMPDIR") else ""
)
USER_TEMP = ""
if DARWIN:
    USER_TEMP = subprocess.run(
        ["getconf", "DARWIN_USER_TEMP_DIR"], capture_output=True, text=True, check=False
    ).stdout.strip()

ALLOW = "allow"
ASK = "ask"

# (path, expectation, env overrides, platform-only or None)
CASES = [
    # inside cwd and managed stores
    (f"{CWD}/src/x.py", ALLOW, {}, None),
    (f"{HOME}/.claude/plans/foo.md", ALLOW, {}, None),
    (
        f"{HOME}/.claude/projects/{re.sub(r'[/.]', '-', CWD)}/memory/MEMORY.md",
        ALLOW,
        {},
        None,
    ),
    (f"{HOME}/.claude/projects/-Some-other-project/memory/MEMORY.md", ASK, {}, None),
    # scratch roots, every spelling, with and without $TMPDIR
    ("/tmp/x.txt", ALLOW, {}, None),
    ("/tmp/claude-501/foo/scratchpad/x.txt", ALLOW, {}, None),
    ("/private/tmp/x.txt", ALLOW, {}, "darwin"),
    (f"{TMPDIR}x.txt" if TMPDIR else "/tmp/x2.txt", ALLOW, {}, "darwin"),
    (f"{TMPDIR}x.txt" if TMPDIR else "/tmp/x3.txt", ALLOW, {"TMPDIR": None}, "darwin"),
    (f"{USER_TEMP}x.txt", ALLOW, {"TMPDIR": None}, "darwin"),
    (f"/private{USER_TEMP}x.txt", ALLOW, {"TMPDIR": None}, "darwin"),
    # pre-trust names and the config root under a scratch root stay gated
    ("/tmp/clone/.claude/settings.json", ASK, {}, None),
    ("/tmp/clone/.mcp.json", ASK, {}, None),
    ("/tmp/clone/CLAUDE.md", ASK, {}, None),
    ("/tmp/clone/claude.local.md", ASK, {}, None),
    ("/tmp/clone/.git/hooks/pre-commit", ASK, {}, None),
    ("/tmp/cfg/hooks/x.py", ASK, {"CLAUDE_CONFIG_DIR": "/tmp/cfg"}, None),
    # /private outside the scratch roots, /var/tmp, and /etc stay gated
    ("/private/var/db/x.txt", ASK, {}, None),
    ("/private/var/log/x.txt", ASK, {}, None),
    ("/private/var/folders/zz/abc/0/com.example/x.txt", ASK, {}, None),
    ("/private/var/folders/zz/abc/C/x.txt", ASK, {}, None),
    ("/private/x.txt", ASK, {}, None),
    ("/var/tmp/x.txt", ASK, {}, None),
    ("/private/var/tmp/x.txt", ASK, {}, None),
    ("/private/etc/hosts", ASK, {}, None),
    ("/etc/hosts", ASK, {}, None),
    # unrelated locations and the user-level config
    (f"{HOME}/Documents/foo.txt", ASK, {}, None),
    (f"{HOME}/.claude/hooks/x.py", ASK, {}, None),
    (f"{HOME}/.claude/settings.json", ASK, {}, None),
    ("/usr/local/x.txt", ASK, {}, None),
    # a bad $TMPDIR must not widen the exemption
    ("/usr/local/x.txt", ASK, {"TMPDIR": "/"}, None),
    (f"{HOME}/Documents/foo.txt", ASK, {"TMPDIR": HOME}, None),
]


REPO = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
).stdout.strip()
if REPO and not REPO.startswith(CWD):
    CASES += [
        # Class 4: ordinary source in another repo passes, its executable trees ask
        (f"{REPO}/README.md", ALLOW, {}, None),
        (f"{REPO}/mac/harness/hooks/PreToolUse-external-write-gate.py", ASK, {}, None),
        (f"{REPO}/mac/harness/rules/bash-deny-rm-rf-root.md", ASK, {}, None),
        (f"{REPO}/scripts/deploy-harness.sh", ASK, {}, None),
        (f"{REPO}/.github/workflows/ci.yml", ASK, {}, None),
        (f"{REPO}/mac/harness/settings.json", ALLOW, {}, None),
    ]


def run_case(path, env_overrides, cwd=None):
    env = dict(os.environ)
    for k, v in env_overrides.items():
        if v is None:
            env.pop(k, None)
        else:
            env[k] = v
    payload = json.dumps(
        {"tool_name": "Write", "tool_input": {"file_path": path}, "cwd": cwd or CWD}
    )
    r = subprocess.run(
        [sys.executable, "-I", HOOK],
        input=payload,
        capture_output=True,
        text=True,
        env=env,
    )
    return r.returncode, r.stdout, r.stderr


def main() -> int:
    fails = 0
    skipped = 0
    for path, expect, env_overrides, platform in CASES:
        if platform and sys.platform != platform:
            skipped += 1
            continue
        code, out, err = run_case(path, env_overrides)
        if expect == ALLOW:
            ok = code == 0 and out == "" and err == ""
        else:
            ok = code == 0 and '"permissionDecision": "ask"' in out
        if not ok:
            fails += 1
        verdict = (
            "allow"
            if out == "" and code == 0
            else ("ask  " if "ask" in out else f"exit={code}")
        )
        print(
            f"{'ok  ' if ok else 'FAIL'} {verdict} {path.replace(HOME, '~')} {env_overrides or ''}"
        )
    # symlink spoof: a link under /tmp that points at /etc must still ask
    link = "/tmp/claude-gate-symlink-probe"
    try:
        if os.path.lexists(link):
            os.remove(link)
        os.symlink("/etc", link)
        code, out, _ = run_case(f"{link}/hosts", {})
        ok = code == 0 and '"permissionDecision": "ask"' in out
    finally:
        if os.path.lexists(link):
            os.remove(link)
    print(f"{'ok  ' if ok else 'FAIL'} symlink under /tmp pointing at /etc asks")
    fails += 0 if ok else 1
    # symlink inside the working directory pointing outside it must not carry the inside-cwd pass
    with tempfile.TemporaryDirectory() as td:
        os.symlink("/etc", os.path.join(td, "sshlink"))
        code, out, _ = run_case(f"{td}/sshlink/hosts", {}, cwd=td)
        ok = code == 0 and '"permissionDecision": "ask"' in out
        print(f"{'ok  ' if ok else 'FAIL'} in-cwd symlink to /etc asks")
        fails += 0 if ok else 1
        code, out, _ = run_case(f"{td}/plain.txt", {}, cwd=td)
        ok = code == 0 and out == ""
        print(f"{'ok  ' if ok else 'FAIL'} plain file in cwd allows")
        fails += 0 if ok else 1
    r = subprocess.run(
        [sys.executable, "-I", HOOK], input="not json", capture_output=True, text=True
    )
    ok = r.returncode == 2 and "Blocked per AP.8" in r.stderr
    print(f"{'ok  ' if ok else 'FAIL'} non-JSON payload exits 2")
    fails += 0 if ok else 1
    total = len(CASES) - skipped + 4
    print(
        f"\n{total - fails}/{total} cases as expected ({skipped} platform-specific cases skipped)"
    )
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
