# Patch: scratch roots and rm protected paths (Jetson)

Post-Phase-3 refinement. Deploy the October 30, 2026 Mac change to the Jetson
host: the narrowed scratch-root exemption in `PreToolUse-external-write-gate.py`,
the new `PreToolUse-bash-deny-rm-protected-paths.py` and
`ConfigChange-audit-claude-config.py` hooks, the fail-closed registrations,
the rule-layer changes, and drift check 6. The repository side is already done
and byte-identical across platforms. This runbook is the on-device half.

Reference commits on Mac: the October 30, 2026 entries in `JOURNEY.md` and `git log --since=2026-10-30 main`. The Mac sources
`mac/harness/hooks/PreToolUse-external-write-gate.py`,
`mac/harness/hooks/PreToolUse-bash-deny-rm-protected-paths.py`, and
`mac/harness/hooks/ConfigChange-audit-claude-config.py` are the canonical
implementations. Jetson hook scripts are byte-identical to Mac unless a
platform-specific reason to diverge is documented (AP.3, parity not
portability). This prompt is a port runbook, not a redesign.

---

<role>
You are a senior harness engineer applying a post-Phase-3 refinement on Jetson.
The change is mechanical: confirm the tracked Jetson files match Mac, deploy the
three hooks to the live hooks directory, render the settings template, register
at user level, and prove all three hooks on this host with the committed test
matrices and drift check 6.

Match the writing rules.
</role>

<effort>medium</effort>
<mode>default</mode>
<thinking>standard</thinking>
<context_budget>One pass. No compaction expected.</context_budget>
<scope>Strict. Three hook files and three test files already tracked, three deployed copies on disk, one rendered settings file merged at user level, one commit.</scope>

<context>
What changed and why is in three places. Read them before touching the host:

- `jetson/harness/rules/filesystem-allow-scratch-roots.md` (the scratch-root
  decision and what it does not deliver)
- `jetson/harness/rules/bash-deny-rm-rf-root.md` (why the `:*` rules never
  covered root-prefixed paths and what the hook protects)
- `jetson/harness/hooks/README.md` (which hooks fail closed and why the others
  do not)
- `HARNESS_GUIDE.md`, sections "Which hooks fail closed", "The deterministic
  gates", and "Unattended runs"

On Jetson the home is `/home/<user>`, there is no `/private`, and `getconf
DARWIN_USER_TEMP_DIR` does not exist. Both hooks handle that: the write gate's
scratch roots collapse to `/tmp` and `$TMPDIR`, and the rm hook's `/private`
and `/Volumes` shapes never match a real path. `/media/<user>` and
`/mnt/<name>` are the mounted-volume shapes that matter here. No path edits are
needed in either script.

The rm hook ignores `HARNESS_AUTONOMOUS_MODE`. If the Jetson user-level
`settings.json` sets the flag, the deny still holds. The ConfigChange gate
reads `~/.claude/audited-hashes.json`, the same registry the SessionStart
audit on this host already uses. Drift check 6
(`scripts/check-hook-registrations.py`) detects the Jetson by
`uname -m` and compares the Jetson template against the live user settings.
If the Jetson's live settings register a hook of its own that the template
does not (claude-mem, for example), add its basename to
`LIVE_ONLY_BY_PLATFORM["jetson"]` in that script in the same commit.
</context>

<investigate_before_answering>
Read:

- `mac/harness/hooks/PreToolUse-external-write-gate.py`,
  `mac/harness/hooks/PreToolUse-bash-deny-rm-protected-paths.py`, and
  `mac/harness/hooks/ConfigChange-audit-claude-config.py` (canonical
  sources, module headers carry the rationale)
- `jetson/harness/hooks/` copies of both, and `jetson/harness/hooks/tests/`
- `jetson/harness/settings.json.template` (the `onFailure` and `python3 -I`
  registrations, the ConfigChange registration, the allow and deny changes)
- `scripts/check-hook-registrations.py` and `scripts/drift-check.sh` check 6
- `foundation/02-architectural-principles.md` AP.3 (parity), AP.5 (commit),
  AP.8 (fail closed), AP.11 (reversibility)
- `scripts/drift-check.sh` (check 5 enforces deployed == source via `cmp -s`)
</investigate_before_answering>

<instructions>

### 1. Confirm the tracked Jetson copies match Mac

```bash
for f in PreToolUse-external-write-gate.py PreToolUse-bash-deny-rm-protected-paths.py ConfigChange-audit-claude-config.py; do
  cmp -s mac/harness/hooks/$f jetson/harness/hooks/$f && echo "byte-identical: $f"
done
for f in test_external_write_gate.py test_bash_deny_rm_protected_paths.py test_configchange_audit_claude_config.py; do
  cmp -s mac/harness/hooks/tests/$f jetson/harness/hooks/tests/$f && echo "byte-identical: tests/$f"
done
```

If any differs, replace the Jetson copy with the Mac source unless
`jetson/ARCHITECTURE.md` documents a reason to diverge.

### 2. Deploy to the live hooks directory

```bash
for f in PreToolUse-external-write-gate.py PreToolUse-bash-deny-rm-protected-paths.py ConfigChange-audit-claude-config.py; do
  cp jetson/harness/hooks/$f ~/.claude/hooks/$f
  chmod +x ~/.claude/hooks/$f
  cmp -s jetson/harness/hooks/$f ~/.claude/hooks/$f && echo "deployed == source: $f"
done
```

### 3. Render the settings template and confirm the registrations

Use the deploy script's dry run for the rendering: it rewrites `{{REPO_ROOT}}/harness/hooks` to `~/.claude/hooks`, where step 2 put the files, and refuses to continue if a placeholder survives in a hook path. A plain `sed` of `{{REPO_ROOT}}` to the repo root would register `<repo>/harness/hooks/...`, which does not exist in this build repository, and the four fail-closed hooks would then block every call.

```bash
bash scripts/deploy-harness.sh --platform jetson --dry-run
sed "s|{{REPO_ROOT}}/harness/hooks|$HOME/.claude/hooks|g" jetson/harness/settings.json.template > /tmp/rendered-settings.json
python3 - <<'PY'
import json
d = json.load(open("/tmp/rendered-settings.json"))
import os
for ev, groups in d["hooks"].items():
    for g in groups if isinstance(groups, list) else []:
        for e in g.get("hooks", []):
            path = (e.get("args") or [e.get("command")])[-1]
            print(ev, e.get("onFailure", "-"), e.get("timeout", "-"), path, "OK" if os.path.exists(path) else "MISSING")
print("scratch allows:", [r for r in d["permissions"]["allow"] if "tmp" in r])
print("etc/ssh denies:", [r for r in d["permissions"]["deny"] if "etc" in r or ".ssh" in r])
PY
```

Expected: every registered path prints `OK`, the five destructive-class hooks
(git-push-force-ask, bash-deny-rm-protected-paths, external-write-gate,
cached-prefix-write-gate, and ConfigChange-audit-claude-config on
`project_settings|local_settings`) show `block 10`, eight scratch allow rules,
and the `Edit(//etc/**)`, `Edit(//private/etc/**)`, `Edit(~/.ssh/**)`,
`Edit(~/.gnupg/**)`, `Edit(~/.aws/credentials)`, `Edit(~/.aws/config)`, and
`Edit(~/.kube/config)` denies. Register
at user level in `~/.claude/settings.json`, as the Mac reference host does, so
the gates apply to every project on the device. Confirm `claude --version`
reports 2.1.295 or later. Below that floor `onFailure` is ignored and the five
gates fail open: upgrade first, and do not record the port as deployed until
the version is at or above the floor.

### 4. Verification matrices

Run both from the repo root against the deployed copies. Platform-specific
rows skip themselves on Linux.

```bash
python3 -I jetson/harness/hooks/tests/test_external_write_gate.py ~/.claude/hooks/PreToolUse-external-write-gate.py
python3 -I jetson/harness/hooks/tests/test_bash_deny_rm_protected_paths.py ~/.claude/hooks/PreToolUse-bash-deny-rm-protected-paths.py
python3 -I jetson/harness/hooks/tests/test_configchange_audit_claude_config.py ~/.claude/hooks/ConfigChange-audit-claude-config.py
```

All three must end with every non-skipped case as expected. Then one live probe in a
session on this host against a target no settings rule covers, so the probe
cannot pass on the rule layer alone: ask Claude to run `rm -rf /usr` and
confirm the transcript shows the string `Denied by
PreToolUse-bash-deny-rm-protected-paths`, not a prompt and not a rule-layer
refusal. Document the matrix counts and the probe in
`phase-outputs/PHASE_3_VALIDATION.md` (create it if absent) under a Jetson
post-Phase-3 refinement section.

### 5. Drift and SAST

```bash
bash scripts/drift-check.sh
# Required: "deployed hooks match tracked source" and
#           "hook registrations agree across template, live"

semgrep --error --quiet --config p/python --config p/security-audit \
  jetson/harness/hooks/PreToolUse-external-write-gate.py \
  jetson/harness/hooks/PreToolUse-bash-deny-rm-protected-paths.py \
  jetson/harness/hooks/ConfigChange-audit-claude-config.py
```

Both must exit 0.

### 6. Commit

AP.5 template. Single decision. Example:

```
hook(jetson): deploy scratch roots, the rm protected-paths deny, and the ConfigChange gate

Context: The Mac change of October 30, 2026 landed in the Jetson tree
byte-identical. The live hooks directory and the rendered settings on this
host still carried the previous versions.

Decision: Deploy all three hooks and the five fail-closed registrations as
tracked. No platform-specific divergence.

Why: AP.3 (parity), AP.8 (fail closed), AP.11 (reversibility). Reference:
JOURNEY.md, October 30, 2026.

Tradeoff: The write gate's per-user temp root is macOS-only by construction.
On Jetson the scratch set is /tmp and $TMPDIR, which is the documented
Linux behavior, not a gap.
```

</instructions>

<deliverable>
Deployed copies byte-identical to source. Rendered settings carrying five
fail-closed registrations and the rule changes, merged at user level. All
three matrices passing on the host, drift check 6 green, one live probe
recorded. Drift check green. Semgrep clean. One commit on
a feature branch. Short summary report.
</deliverable>

<verification>
Drift check passes with "deployed hooks match tracked source".

Semgrep exits 0 on all three Jetson hook copies.

All three matrices report every non-skipped case as expected, and drift check
6 reports the registrations agree.

`PHASE_3_VALIDATION.md` records the run and outcome.
</verification>
