#!/usr/bin/env python3
"""Verification matrix for PreToolUse-bash-deny-rm-protected-paths.py.

Run from the repo root with the hook path as the only argument:
    python3 -I mac/harness/hooks/tests/test_bash_deny_rm_protected_paths.py \
        mac/harness/hooks/PreToolUse-bash-deny-rm-protected-paths.py

Every case pipes a PreToolUse payload through the hook as a subprocess, so
the matrix exercises the real entry point, the exit code, and the stderr
reason. Expectations are built from the running account's home so the same
file passes on Mac and Jetson. Cases that only make sense on a
case-insensitive filesystem or under the macOS /private layout are marked
and skipped elsewhere. Exit status is 0 when every case matches.

Owner: harness-engineering (October 30, 2026)
"""

import json
import os
import subprocess
import sys

HOOK = sys.argv[1]
HOME = os.path.abspath(os.path.expanduser("~"))
PROJ = os.path.join(HOME, "proj")
SUB = os.path.join(PROJ, "sub")
DARWIN = sys.platform == "darwin"
CONFIG = os.path.abspath(
    os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(HOME, ".claude")
)

DENY = True
ALLOW = False

# (command, cwd, expectation, platform-only or None)
CASES = [
    # root and its spellings
    ("rm -rf /", PROJ, DENY, None),
    ("rm -rf /*", PROJ, DENY, None),
    ("rm -rf //", PROJ, DENY, None),
    ("rm -rf /System/Volumes/Data", PROJ, DENY, None),
    ("rm -rf /System/Volumes/Data/", PROJ, DENY, None),
    ("rm -rf /System/Volumes/Data/*", PROJ, DENY, None),
    (f"rm -rf /System/Volumes/Data{HOME}", PROJ, DENY, None),
    # home and its spellings
    ("rm -rf ~", PROJ, DENY, None),
    ("rm -rf ~/", PROJ, DENY, None),
    ("rm -rf ~/*", PROJ, DENY, None),
    ("rm -rf ~/.*", PROJ, DENY, None),
    ("rm -rf ~/{*,.*}", PROJ, DENY, None),
    ("rm -rf ~/?*", PROJ, DENY, None),
    ("rm -rf $HOME", PROJ, DENY, None),
    ("rm -rf $HOME/", PROJ, DENY, None),
    ("rm -rf ${HOME}/*", PROJ, DENY, None),
    ('rm -rf "$HOME"', PROJ, DENY, None),
    (f"rm -rf {HOME}", PROJ, DENY, None),
    (f"rm -rf {HOME}/", PROJ, DENY, None),
    (f"rm -f {HOME}/*", PROJ, DENY, None),
    (f"rm {HOME}/*", PROJ, DENY, None),
    (f"rmdir {HOME}", PROJ, DENY, None),
    ("rm -rf ~root", PROJ, DENY, None),
    (f"rm -rf {HOME.lower()}", PROJ, DENY, "darwin"),
    (f"rm -rf {HOME.upper()}", PROJ, DENY, "darwin"),
    # other homes and home parents
    ("rm -rf /Users/someoneelse", PROJ, DENY, None),
    ("rm -rf /Users", PROJ, DENY, None),
    ("rm -rf /home/alex", PROJ, DENY, None),
    ("rm -rf /private/tmp", PROJ, DENY, None),
    ("rm -rf /private/var", PROJ, DENY, None),
    # top-level directories and flag permutations
    ("rm -rf /usr", PROJ, DENY, None),
    ("rm -fr /usr", PROJ, DENY, None),
    ("rm -Rf /etc", PROJ, DENY, None),
    ("rm -rfv /tmp", PROJ, DENY, None),
    ("rm -rf /tmp/", PROJ, DENY, None),
    ("rm -r -f /var", PROJ, DENY, None),
    ("rm --recursive --force /opt", PROJ, DENY, None),
    ("rm -rf -- /Library", PROJ, DENY, None),
    # mounted volumes
    ("rm -rf /Volumes/Backup", PROJ, DENY, None),
    ("rm -rf /Volumes/Backup/*", PROJ, DENY, None),
    ("rm -rf /System/Volumes/Preboot", PROJ, DENY, None),
    ("rm -rf /media/alex", PROJ, DENY, None),
    ("rm -rf /media/alex/usb", PROJ, DENY, None),
    ("rm -rf /mnt/data", PROJ, DENY, None),
    ("rm -rf /run/media/alex/usb", PROJ, DENY, None),
    # working directory and ancestors
    ("rm -rf .", PROJ, DENY, None),
    ("rm -rf ..", PROJ, DENY, None),
    ("rm -rf ..", SUB, DENY, None),
    ("rm -rf ../..", SUB, DENY, None),
    ("rm -rf .", HOME, DENY, None),
    ("rm -rf *", HOME, DENY, None),
    ("rm -rf ./*", HOME, DENY, None),
    (f"rm -rf {PROJ}", SUB, DENY, None),
    # cd tracking
    ("cd ~ && rm -rf *", PROJ, DENY, None),
    ("cd .. && rm -rf *", PROJ, DENY, None),
    ("cd / && rm -rf *", PROJ, DENY, None),
    ("cd /tmp && cd ~ && rm -rf .", PROJ, DENY, None),
    ("cd /tmp; cd -; rm -rf ..", PROJ, DENY, None),
    ("pushd ~ && rm -rf *", PROJ, DENY, None),
    ("cd && rm -rf .ssh", PROJ, DENY, None),
    ("cd $X && rm -rf *", PROJ, DENY, None),
    ("cd $X && rm -rf .", PROJ, DENY, None),
    ("cd $X && rm -rf ..", PROJ, DENY, None),
    # credential stores and the config root
    ("rm -rf ~/.ssh", PROJ, DENY, None),
    ("rm ~/.ssh/id_rsa", PROJ, DENY, None),
    ("rm -f ~/.ssh/known_hosts", PROJ, DENY, None),
    ("rm -rf ~/.gnupg ~/Documents", PROJ, DENY, None),
    ("rm -rf ~/.aws", PROJ, DENY, None),
    ("rm -rf ~/.config/gh", PROJ, DENY, None),
    ("rm -rf ~/Library/Keychains", PROJ, DENY, None),
    (f"rm -rf {CONFIG}", PROJ, DENY, None),
    (f"rm -rf {CONFIG}/hooks", PROJ, DENY, None),
    (f"rm -f {CONFIG}/hooks/x.py", PROJ, DENY, None),
    (f"rm {CONFIG}/settings.json", PROJ, DENY, None),
    (f"rm -rf {CONFIG}/rules", PROJ, DENY, None),
    # wrappers, chains, groups, substitutions, inline scripts
    ("sudo rm -rf /", PROJ, DENY, None),
    ("doas rm -rf /usr", PROJ, DENY, None),
    ("/bin/rm -rf ~", PROJ, DENY, None),
    ("command rm -rf ~", PROJ, DENY, None),
    ("env FOO=1 rm -rf ~", PROJ, DENY, None),
    ("FOO=1 rm -rf ~", PROJ, DENY, None),
    ("timeout 10 rm -rf ~", PROJ, DENY, None),
    ("nice -n 5 rm -rf ~", PROJ, DENY, None),
    ("caffeinate rm -rf ~", PROJ, DENY, None),
    ("setsid rm -rf ~", PROJ, DENY, None),
    ("ionice -c 3 rm -rf ~", PROJ, DENY, None),
    ("cd /tmp && rm -rf ~", PROJ, DENY, None),
    ("ls; rm -rf /usr", PROJ, DENY, None),
    ("true || rm -rf /etc", PROJ, DENY, None),
    ("echo hi | rm -rf /var", PROJ, DENY, None),
    ("rm -rf /tmp/x 2>&1 & rm -rf ~", PROJ, DENY, None),
    ("(rm -rf ~)", PROJ, DENY, None),
    ("{ rm -rf ~; }", PROJ, DENY, None),
    ('echo "$(rm -rf ~)"', PROJ, DENY, None),
    ("echo `rm -rf /usr`", PROJ, DENY, None),
    ('sh -c "rm -rf $HOME"', PROJ, DENY, None),
    ("bash -c 'rm -rf ~'", PROJ, DENY, None),
    ("bash -ec 'rm -rf /usr'", PROJ, DENY, None),
    ("timeout 5 bash -c 'cd .. && rm -rf *'", PROJ, DENY, None),
    ("echo it's bad && rm -rf ~", PROJ, DENY, None),
    # round 2 bypasses: ancestor globs, quote splicing, eval, process substitution, quoted <<
    ("rm -rf ../*", SUB, DENY, None),
    ("rm -rf ../.*", SUB, DENY, None),
    (f"rm -rf {PROJ}/*", SUB, DENY, None),
    ("r''m -rf ~", PROJ, DENY, None),
    ('"r"m -rf ~', PROJ, DENY, None),
    ("eval 'rm -rf ~'", PROJ, DENY, None),
    ("cat <(rm -rf ~)", PROJ, DENY, None),
    ('echo "<<EOF"\nrm -rf ~', PROJ, DENY, None),
    ("echo $((1<<3))\nrm -rf ~", PROJ, DENY, None),
    ('python3 -c "x = 1<<3"\nrm -rf ~', PROJ, DENY, None),
    ("cat <<EOF\nno terminator here\nrm -rf ~", PROJ, DENY, None),
    ("rm -rf ~root/", PROJ, DENY, None),
    ("rm ~/.aws/credentials", PROJ, DENY, None),
    ("rm -f ~/.kube/config", PROJ, DENY, None),
    ("rm -rf /mnt/c/Users/alex", PROJ, DENY, None),
    (f"rm -rf {os.path.dirname(os.path.abspath(HOOK))}", PROJ, DENY, None),
    # round 2 red team: shells fed by here-string or pipe, loops, aliases, case, braces, deep globs, expansions, other deleters
    ("bash <<< 'rm -rf ~'", PROJ, DENY, None),
    ("echo 'rm -rf ~' | bash", PROJ, DENY, None),
    ("printf 'rm -rf %s' ~ | sh", PROJ, DENY, None),
    ("for d in ~; do rm -rf $d; done", PROJ, DENY, None),
    ("for d in build ~; do rm -rf $d; done", PROJ, DENY, None),
    ("alias z='rm -rf ~'; z", PROJ, DENY, None),
    ("RM -rf ~", PROJ, DENY, "darwin"),
    ("/bin/RM -rf ~", PROJ, DENY, "darwin"),
    ("RMDIR /Users/x", PROJ, DENY, "darwin"),
    ("{rm,-rf,~}", PROJ, DENY, None),
    ("rm -rf ~/**/*", PROJ, DENY, None),
    ("rm -rf $HOME/**/*", PROJ, DENY, None),
    ("rm -rf ~/*/*", PROJ, DENY, None),
    ("rm -rf ~/Library/*", PROJ, DENY, None),
    ("rm -rf ~/.config/*", PROJ, DENY, None),
    ('rm -rf "${HOME%/}"', PROJ, DENY, None),
    ('rm -rf "$(echo ~)"', PROJ, DENY, None),
    ("rm -rf $UNKNOWN", PROJ, DENY, None),
    ('echo "$( (rm -rf ~) )"', PROJ, DENY, None),
    ("unlink ~/.ssh/id_rsa", PROJ, DENY, None),
    ("shred -u ~/.ssh/id_rsa", PROJ, DENY, None),
    ("mv ~/.ssh /tmp/exfil", PROJ, DENY, None),
    ("mv ~/.aws/credentials /tmp/c", PROJ, DENY, None),
    ("find ~ -delete", PROJ, DENY, None),
    ("find ~ -name x -exec rm -rf {} +", PROJ, DENY, None),
    ("echo ~ | xargs rm -rf", PROJ, DENY, None),
    (f"rm -rf {CONFIG}/skills", PROJ, DENY, None),
    (f"rm -rf {CONFIG}/agents", PROJ, DENY, None),
    (f"rm -f {CONFIG}/mcp.json", PROJ, DENY, None),
    (f"rm -f {CONFIG}/.credentials.json", PROJ, DENY, None),
    (f"rm -rf {CONFIG}/plugins", PROJ, DENY, None),
    ("rm -f ~/.claude.json", PROJ, DENY, None),
    ("grep '<<END' f\nrm -rf ~\nEND", PROJ, DENY, None),
    # allowed: scoped cleanup below protected paths
    ("find . -name '*.pyc' -delete", PROJ, ALLOW, None),
    ("find /tmp -mtime +1 -delete", PROJ, ALLOW, None),
    ("find ~/proj -name __pycache__ -exec rm -rf {} +", PROJ, ALLOW, None),
    ("find . -name '*.orig' | xargs rm -f", PROJ, ALLOW, None),
    ("mv build build.old", PROJ, ALLOW, None),
    ("mv ~/Downloads/x.zip /tmp/", PROJ, ALLOW, None),
    ("for d in build dist; do rm -rf $d; done", PROJ, ALLOW, None),
    ('rm -rf "$TMPDIR"/x', PROJ, ALLOW, None),
    ('rm -rf "$PWD"/build', PROJ, ALLOW, None),
    (f"rm -rf {CONFIG}/projects/-x-y/memory", PROJ, ALLOW, None),
    (f"rm -rf {CONFIG}/shell-snapshots", PROJ, ALLOW, None),
    ("echo 'rm -rf ~' | grep rm", PROJ, ALLOW, None),
    ("bash -c 'echo hi' | bash", PROJ, ALLOW, None),
    ("git rm -r --cached .", PROJ, ALLOW, None),
    ("git rm -rf --cached . && git add .", PROJ, ALLOW, None),
    ("git rm -r .", PROJ, ALLOW, None),
    ("docker exec web rm -rf /data", PROJ, ALLOW, None),
    ("docker run --rm img rm -rf /tmp", PROJ, ALLOW, None),
    ("ssh deploy@host rm -rf /srv", PROJ, ALLOW, None),
    ("kubectl exec pod -- rm -rf /home/app", PROJ, ALLOW, None),
    ("rm -rf ~/.kube/cache", PROJ, ALLOW, None),
    ("rm -rf ~/.aws/cli/cache", PROJ, ALLOW, None),
    ("rm -rf ~/.aws/sso/cache", PROJ, ALLOW, None),
    ("(cd ~); rm -rf *", PROJ, ALLOW, None),
    ("(cd ~) && rm -rf *", PROJ, ALLOW, None),
    ("rm -rf dist/ build/ *.egg-info", PROJ, ALLOW, None),
    ("find . -name __pycache__ -exec rm -rf {} +", PROJ, ALLOW, None),
    ("rm -rf ~/Library/Caches/*", PROJ, ALLOW, None),
    ("cd .. && rm -rf build && mkdir build", os.path.join(PROJ, "build"), DENY, None),
    ("rm -rf ~/proj/build", PROJ, ALLOW, None),
    ("rm -rf /tmp/x", PROJ, ALLOW, None),
    ("rm -rf /tmp/*", PROJ, ALLOW, None),
    ("rm -rf /tmp/*.log", PROJ, ALLOW, None),
    ("rm -rf /private/tmp/*", PROJ, ALLOW, "darwin"),
    ("rm -rf /private/tmp/claude-501/scratch", PROJ, ALLOW, None),
    ("rm -rf /private/var/folders/c0/x", PROJ, ALLOW, None),
    ("rm -rf /private/var/folders/*", PROJ, ALLOW, None),
    ("rm -rf ~/Downloads/x", PROJ, ALLOW, None),
    ("rm -rf $HOME/.cache/pip", PROJ, ALLOW, None),
    (f"rm -rf {CONFIG}/plugins/cache/x", PROJ, ALLOW, None),
    (f"rm -rf {CONFIG}/projects/p/memory", PROJ, ALLOW, None),
    ("rm -rf build dist node_modules", PROJ, ALLOW, None),
    ("rm -rf *", PROJ, ALLOW, None),
    ("rm -rf ./*", PROJ, ALLOW, None),
    ("rm -rf ./*", SUB, ALLOW, None),
    ("rm -rf ../build", SUB, ALLOW, None),
    ("cd build && rm -rf ./*", PROJ, ALLOW, None),
    ("cd /tmp/x && rm -rf .", PROJ, ALLOW, None),
    ("cd $X && rm -rf build", PROJ, ALLOW, None),
    ("rm /tmp/log.txt", PROJ, ALLOW, None),
    ("rm -f ~/.zcompdump", PROJ, ALLOW, None),
    ("rm /usr", PROJ, ALLOW, None),
    ("rm -rf $DIR/*", PROJ, DENY, None),
    ('rm -rf "$TMPDIR"/x', PROJ, ALLOW, None),
    ("rm -rf -v -- ./out", PROJ, ALLOW, None),
    ("rm -rf ~otheruser/proj/build", PROJ, ALLOW, None),
    ("ls -la ~", PROJ, ALLOW, None),
    ("git rm -r --cached ~/x", PROJ, ALLOW, None),
    ("npm run clean", PROJ, ALLOW, None),
    ("echo 'rm -rf ~'", PROJ, ALLOW, None),
    ('git commit -m "rm -rf ~ was a bad idea"', PROJ, ALLOW, None),
    ("cat > notes.md <<'EOF'\nrm -rf ~\nrm -rf /\nEOF", PROJ, ALLOW, None),
    ("python3 - <<'PY'\nx = \"rm -rf /usr\"\nPY\necho done", PROJ, ALLOW, None),
    ("cat <<EOF > f\nrm -rf $HOME\nEOF\nrm -rf /tmp/x", PROJ, ALLOW, None),
    ("rm -rf /tmp/x; cat > n <<EOF\nrm -rf ~\nEOF", PROJ, ALLOW, None),
    ("grep -rn 'rm -rf /' .", PROJ, ALLOW, None),
    (r"find . -name '*.tmp' -exec rm -rf {} \;", PROJ, ALLOW, None),
    ("xargs rm -rf < list.txt", PROJ, ALLOW, None),
    ("rm -rf '/tmp/has space'", PROJ, ALLOW, None),
    ("echo it's fine && rm -rf /tmp/y", PROJ, ALLOW, None),
]


# Forms this hook does not judge, asserted as ALLOW so a change in either
# direction is noticed and reported as a known gap rather than a pass.
KNOWN_GAPS = [
    (
        "python3 -c 'import shutil; shutil.rmtree(\"/Users/x\")'",
        PROJ,
        "deletion by another program",
    ),
    ("rsync -a --delete /empty/ ~/", PROJ, "deletion by another program"),
    (
        "git clean -fdx",
        PROJ,
        "git clean inside cwd is recoverable from the index only for tracked files",
    ),
]


def run_case(cmd, cwd):
    payload = json.dumps(
        {"tool_name": "Bash", "tool_input": {"command": cmd}, "cwd": cwd}
    )
    r = subprocess.run(
        [sys.executable, "-I", HOOK], input=payload, capture_output=True, text=True
    )
    return r.returncode, r.stdout, r.stderr


def main() -> int:
    fails = 0
    skipped = 0
    for cmd, cwd, expect_deny, platform in CASES:
        if platform and sys.platform != platform:
            skipped += 1
            continue
        code, out, err = run_case(cmd, cwd)
        denied = (
            code == 2 and "Denied by PreToolUse-bash-deny-rm-protected-paths" in err
        )
        clean_allow = code == 0 and out == "" and err == ""
        ok = (denied and expect_deny) or (clean_allow and not expect_deny)
        if not ok:
            fails += 1
        tag = "ok  " if ok else "FAIL"
        verdict = "DENY " if denied else ("allow" if clean_allow else f"exit={code}")
        print(f"{tag} {verdict} {cmd!r} cwd={cwd.replace(HOME, '~')}")
    # Fail-closed paths: a non-JSON payload and a crash both exit 2.
    r = subprocess.run(
        [sys.executable, "-I", HOOK], input="not json", capture_output=True, text=True
    )
    bad_json_ok = r.returncode == 2 and "Blocked per AP.8" in r.stderr
    r = subprocess.run(
        [sys.executable, "-I", HOOK],
        input=json.dumps(
            {"tool_name": "Bash", "tool_input": {"command": "rm -rf x"}, "cwd": 123}
        ),
        capture_output=True,
        text=True,
    )
    crash_ok = r.returncode == 2 and "Blocked per AP.8" in r.stderr
    for name, ok in (
        ("non-JSON payload exits 2", bad_json_ok),
        ("malformed cwd exits 2", crash_ok),
    ):
        print(f"{'ok  ' if ok else 'FAIL'} {name}")
        fails += 0 if ok else 1
    gaps = 0
    for cmd, cwd, why in KNOWN_GAPS:
        code, out, err = run_case(cmd, cwd)
        if code == 0 and out == "" and err == "":
            gaps += 1
            print(f"gap  allow {cmd!r}: {why}")
        else:
            print(
                f"NOTE {cmd!r} no longer passes silently (exit={code}); update KNOWN_GAPS"
            )
    total = len(CASES) - skipped + 2
    print(
        f"\n{total - fails}/{total} cases as expected ({skipped} platform-specific cases skipped, {gaps} known gaps)"
    )
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
