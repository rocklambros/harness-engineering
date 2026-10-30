#!/usr/bin/env python3
"""Verification matrix for ConfigChange-audit-claude-config.py.

Run from the repo root with the hook path as the only argument:
    python3 -I mac/harness/hooks/tests/test_configchange_audit_claude_config.py \
        mac/harness/hooks/ConfigChange-audit-claude-config.py

The hook reads its registry from $CLAUDE_CONFIG_DIR/audited-hashes.json, so
every case runs against a temporary config root with a registry the test
controls. Nothing touches the real registry. Exit status is 0 when every
case matches.

Owner: harness-engineering (October 30, 2026)
"""

import hashlib
import json
import os
import subprocess
import sys
import tempfile

HOOK = sys.argv[1]


def run(payload, config_root):
    env = dict(os.environ, CLAUDE_CONFIG_DIR=config_root)
    r = subprocess.run(
        [sys.executable, "-I", HOOK],
        input=payload if isinstance(payload, str) else json.dumps(payload),
        capture_output=True,
        text=True,
        env=env,
    )
    return r.returncode, r.stdout, r.stderr


def main() -> int:
    fails = 0
    with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as proj:
        settings_dir = os.path.join(proj, ".claude")
        os.makedirs(settings_dir)
        settings = os.path.join(settings_dir, "settings.json")
        local = os.path.join(settings_dir, "settings.local.json")
        open(settings, "w").write('{"disableAllHooks": true}\n')
        open(local, "w").write('{"permissions": {"allow": ["Bash(ls *)"]}}\n')
        audited = hashlib.sha256(open(local, "rb").read()).hexdigest()
        json.dump(
            {audited: {"path": local, "audited_at": "2026-10-30", "auditor": "test"}},
            open(os.path.join(root, "audited-hashes.json"), "w"),
        )

        def case(name, payload, expect):
            nonlocal fails
            code, out, err = run(payload, root)
            blocked = code == 0 and '"decision": "block"' in out
            allowed = code == 0 and out == "" and err == ""
            failed_closed = code == 2 and "Blocked per AP.8" in err
            got = (
                "block"
                if blocked
                else "allow"
                if allowed
                else "exit2"
                if failed_closed
                else f"exit={code}"
            )
            ok = got == expect
            fails += 0 if ok else 1
            print(f"{'ok  ' if ok else 'FAIL'} {got:5} {name}")

        base = {"hook_event_name": "ConfigChange", "cwd": proj}
        case(
            "unaudited project settings blocks",
            {**base, "source": "project_settings", "file_path": settings},
            "block",
        )
        case(
            "unaudited project settings blocks without file_path",
            {**base, "source": "project_settings"},
            "block",
        )
        case(
            "audited local settings allows",
            {**base, "source": "local_settings", "file_path": local},
            "allow",
        )
        case(
            "removed file allows",
            {
                **base,
                "source": "project_settings",
                "file_path": os.path.join(settings_dir, "gone.json"),
            },
            "allow",
        )
        case(
            "user settings not gated",
            {**base, "source": "user_settings", "file_path": settings},
            "allow",
        )
        case(
            "policy settings not gated",
            {**base, "source": "policy_settings", "file_path": settings},
            "allow",
        )
        case(
            "skills not gated",
            {**base, "source": "skills", "file_path": settings},
            "allow",
        )
        case("non-JSON payload exits 2", "not json", "exit2")
        # registry that is not JSON fails closed
        open(os.path.join(root, "audited-hashes.json"), "w").write("{broken")
        case(
            "unreadable registry exits 2",
            {**base, "source": "project_settings", "file_path": settings},
            "exit2",
        )
        log = os.path.join(root, "logs", "config-change-gate.log")
        ok = os.path.exists(log) and "BLOCK" in open(log).read()
        fails += 0 if ok else 1
        print(f"{'ok  ' if ok else 'FAIL'} decisions are logged under the config root")
    total = 10
    print(f"\n{total - fails}/{total} cases as expected")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
