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
The change is mechanical: confirm the tracked Jetson files match Mac, deploy
every hook the template registers to the live hooks directory, render the
settings template, register at user level, and prove the three gates on this
host with the committed test matrices and drift check 6.

Match the writing rules.
</role>

<effort>medium</effort>
<mode>default</mode>
<thinking>standard</thinking>
<context_budget>One pass. No compaction expected.</context_budget>
<scope>Strict. Three hook files and three test files already tracked. Every hook the rendered template registers, plus any whose tracked source changed, deployed on disk. One rendered settings file merged at user level. One commit.</scope>

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
scratch roots collapse to `/tmp` plus `$TMPDIR` when it is set, and the rm
hook's `/private` and `/Volumes` shapes never match a real path. `$TMPDIR` is
usually unset on Linux, and it was unset on the first Jetson run, so the
effective scratch set is `/tmp` alone. Of the eight scratch allow rules, only
`Read(//tmp/**)` and `Edit(//tmp/**)` match a real path here. The
`//private/...` and `//var/folders/...` rules stay in the template for parity
and match nothing. `/media/<user>` and
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

`~/.claude` is not a git repository on Jetson and `backup-config.sh` does not
exist here, so take a snapshot first. It is the rollback path.

```bash
mkdir -p ~/backups
tar -czf ~/backups/claude-config-$(date +%F).tgz -C ~ .claude/settings.json .claude/hooks
```

Deploy every hook the rendered template registers, not only the three this
change touches. The template registers hooks that may be missing on disk
(`SessionStart-audit-plugin-updates.py` was on the first run), and a missing
fail-closed hook blocks every call. Drift check 5 also requires any hook whose
tracked source changed since the last deploy. On the first run that was
`PreToolUse-supply-chain-bash-checks.py` and
`PreToolUse-bash-cap-subcommands.py`, after commit 2cc63ac moved the bypass log
to `~/.claude/logs/`. The deploy script copies every `.py` and `.sh` in
`jetson/harness/hooks/` that differs from the deployed copy, which covers both
cases. Review the dry run, then run it for real.

```bash
bash scripts/deploy-harness.sh --platform jetson --dry-run
bash scripts/deploy-harness.sh --platform jetson
for src in jetson/harness/hooks/*.py jetson/harness/hooks/*.sh; do
  f=$(basename "$src")
  cmp -s "$src" ~/.claude/hooks/"$f" && echo "deployed == source: $f" || echo "DIFFERS: $f"
done
```

The script never overwrites an existing `~/.claude/settings.json`. It prints
the hooks-block diff for step 3.

Create the bypass log directory. Claude Code does not create it, and hook
copies older than the commit `hook: create the bypass log directory before
writing` drop every autonomous-mode log line when it is missing.

```bash
mkdir -m 700 -p ~/.claude/logs
```

If an old `~/.claude/hooks/autonomous-bypass.log` exists, move it into
`~/.claude/logs/` by hand in a terminal. Run from a session, the rm hook denies
an `mv` that takes a file out of `~/.claude`, by design.

### 3. Render the settings template and confirm the registrations

The deploy script's dry run in step 2 already rendered the template and
printed the hooks-block diff. It rewrites `{{REPO_ROOT}}/harness/hooks` to
`~/.claude/hooks`, where step 2 put the files, and refuses to continue if a
placeholder survives in a hook path. A plain `sed` of `{{REPO_ROOT}}` to the
repo root would register `<repo>/harness/hooks/...`, which does not exist in
this build repository, and the four fail-closed hooks would then block every
call. Render once more into a private directory to check the registrations and
rules. A render under `/tmp` is world-readable.

```bash
render=$(mktemp -d)
sed "s|{{REPO_ROOT}}/harness/hooks|$HOME/.claude/hooks|g" jetson/harness/settings.json.template > "$render/settings.json"
python3 - "$render/settings.json" <<'PY'
import json, os, sys
d = json.load(open(sys.argv[1]))
for ev, groups in d["hooks"].items():
    for g in groups if isinstance(groups, list) else []:
        for e in g.get("hooks", []):
            path = (e.get("args") or [e.get("command")])[-1]
            print(ev, e.get("onFailure", "-"), e.get("timeout", "-"), path, "OK" if os.path.exists(path) else "MISSING")
print("scratch allows:", [r for r in d["permissions"]["allow"] if "tmp" in r or "/T/" in r])
expected = ["Edit(//etc/**)", "Edit(//private/etc/**)", "Edit(~/.ssh/**)", "Edit(~/.gnupg/**)",
            "Edit(~/.aws/credentials)", "Edit(~/.aws/config)", "Edit(~/.kube/config)"]
print("missing denies:", [r for r in expected if r not in d["permissions"]["deny"]])
PY
```

Expected: every registered path prints `OK`, the five destructive-class hooks
(git-push-force-ask, bash-deny-rm-protected-paths, external-write-gate,
cached-prefix-write-gate, and ConfigChange-audit-claude-config on
`project_settings|local_settings`) show `block 10`, eight scratch allow rules,
and `missing denies: []`. The seven expected denies are:

- `Edit(//etc/**)` and `Edit(//private/etc/**)`
- `Edit(~/.ssh/**)` and `Edit(~/.gnupg/**)`
- `Edit(~/.aws/credentials)` and `Edit(~/.aws/config)`
- `Edit(~/.kube/config)`

Register at user level in `~/.claude/settings.json`, as the Mac reference host
does, so the gates apply to every project on the device. Merge the `hooks`
block and the `permissions` block from the render. Leave out `Read(./**)`,
`Edit(./**)`, and `Bash(./scripts/**)`. They are project-scope allows, and at
user level they widen every project on the device. Remove the render directory
when done. Confirm `claude --version`
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
post-Phase-3 refinement section. `phase-outputs/` is gitignored, so that file
stays on the host. The commit body in step 6 carries the evidence into the
repository: matrix counts, the probe result, drift check, and Semgrep.

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
On Jetson $TMPDIR is unset, so the effective scratch set is /tmp alone. A
$TMPDIR-relative recursive rm denies, which is the safe direction.

Validated on Jetson (aarch64, Claude Code <version>): external-write-gate
<n>/<n>, rm protected-paths <n>/<n>, ConfigChange <n>/<n>. Live probe
rm -rf /usr denied by PreToolUse-bash-deny-rm-protected-paths. drift-check.sh
clean, including check 6. Semgrep exits 0 on the three Jetson hook copies.
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

`PHASE_3_VALIDATION.md` records the run and outcome on the host, and the
commit body carries the same counts into the repository.
</verification>
