# filesystem-allow-scratch-roots

## Pattern

```
Read(//tmp/**)
Edit(//tmp/**)
Read(//private/tmp/**)
Edit(//private/tmp/**)
Read(//var/folders/*/*/T/**)
Edit(//var/folders/*/*/T/**)
Read(//private/var/folders/*/*/T/**)
Edit(//private/var/folders/*/*/T/**)
```

Absolute-path allow rules. The `//` prefix anchors the pattern at the filesystem root. `Edit(path)` is the rule shape Claude Code matches for the Write, Edit, and NotebookEdit tools. `Read(path)` covers Read and, on a best-effort basis, Grep and Glob. A single `*` matches one path segment, so `//var/folders/*/*/T/**` reaches the per-user temp directory (`/var/folders/<xx>/<hash>/T`) and nothing beside it. The `0`, `C`, and `X` siblings hold persistent application state and stay outside the rule. On macOS `/tmp` and `/var` are symlinks into `/private`, so a resolved path can arrive in either spelling, and both are listed so a rule matches whichever one the model sends. On Linux the `/private` and `/var/folders` entries match nothing and cost nothing.

The rules carry the intent in `default`, `acceptEdits`, and `auto` modes. They have no effect in `bypassPermissions` mode, where Claude Code ignores allow rules and the one remaining prompt source for file tools is a PreToolUse hook that answers `ask`. The matching enforcement for that mode is Class 2 of `mac/harness/hooks/PreToolUse-external-write-gate.py`, which treats `/tmp`, `$TMPDIR`, and the per-user temp directory that `getconf DARWIN_USER_TEMP_DIR` reports as scratch roots and stays silent for writes under them. The `getconf` lookup is what closes the gap this rule exists for: a session launched from the Desktop app or launchd has no `$TMPDIR`, and before October 30, 2026 every write to the per-user temp tree asked.

## What this does and does not deliver

Create, read, and update through the file tools under these roots never prompt, in every mode. Three things still can.

Deletes go through Bash, which these rules do not touch. In `bypassPermissions` mode `rm` under a scratch root runs without a prompt (verified October 30, 2026 against a path under `/private/tmp`). In `auto` mode the classifier decides, and Anthropic's published classifier defaults treat glob deletes in shared scratch as blocked by default. No `Bash(rm ...)` allow rule is added, because an unconditional allow would skip classifier review in `default` mode. `PreToolUse-bash-deny-rm-protected-paths.py` lets the glob form of a scratch root pass (`rm -rf /tmp/*` is cleanup) and denies the root itself (`rm -rf /tmp`).

Claude Code's own critical-path check prompts for `rm` targets it recognizes as critical even in `bypassPermissions`: the session's working directory and its parents, and the shape `rm -rf "$VAR"/*`. A session whose cwd is a scratch directory gets that prompt on `rm -rf .`, and `rm -rf "$TMPDIR"/*` gets it everywhere. Spell the target out instead: `rm -rf /tmp/build`.

Pre-trust names under a scratch root stay gated. A `.claude` directory, `.mcp.json`, `.claude.json`, `CLAUDE.md`, `CLAUDE.local.md`, or anything under `.git` written into `/tmp/<clone>` loads or runs in the next session that opens the clone, so the write gate asks for those exactly as it does for any other repository on disk.

## Threat addressed

`foundation/02-architectural-principles.md` AP.11 (reversibility weights friction). Scratch space is cleaned by the OS and never under version control, so the "not reversible from version control" test the external-write gate applies does not hold there. Prompting there trains reflexive approval (Hughes 2026, 93% approval rate) and erodes the gate's signal for writes that matter.

`foundation/01-threat-model.md` T.2 (prompt injection through agent inputs). Trade-off accepted: scratch directories are a known injection landing zone (drop a payload, plant a fake socket). The widening is bounded to `/tmp` and the per-user `T/` tree. An earlier revision of this decision exempted all of `/private`, which also covered persistent per-user application state and world-writable system directories (`/private/var/db/mds`, `/private/var/OOPJit`). That revision was withdrawn the same day after an adversarial premortem measured what it opened.

## Why allow, not ask

Operator decision, October 30, 2026: scratch-space writes never prompt, including under `--dangerously-skip-permissions`. The prior `/tmp` and `$TMPDIR` exemptions (May 25 and September 26, 2026) left the `$TMPDIR`-unset gap described above.

## Test

The hook half runs from the repo root and is the automated record:

```
python3 -I mac/harness/hooks/tests/test_external_write_gate.py mac/harness/hooks/PreToolUse-external-write-gate.py
```

Rule-layer spot checks, expected to pass without a prompt in `default` mode:

```
Write to /tmp/x.txt
Write to /private/tmp/x.txt
Write to $(getconf DARWIN_USER_TEMP_DIR)x.txt
```

Rule-layer spot checks, expected to prompt in `default` mode:

```
Write to /private/var/folders/<xx>/<hash>/0/com.example/x.txt
Write to /var/tmp/x.txt
Write to /tmp/clone/.claude/settings.json
```

Read back live on October 30, 2026 in nested `default`-mode `-p` sessions on Claude Code 2.1.314, with no `--allowedTools` so only the rules could approve: a Write to `/tmp/harness-allow-probe.txt` succeeded with no prompt, a Write to the `$TMPDIR` spelling (`/var/folders/<xx>/<hash>/T/harness-allow-probe.txt`) succeeded with no prompt, and a Write to `/private/var/db/harness-allow-probe.txt` was refused with the write gate's reversibility message. The `//var/folders/*/*/T/**` rule matches the unresolved spelling the model sends.

## Provenance

October 30, 2026. Foundation: AP.11, T.2. Companion hook change: `PreToolUse-external-write-gate.py` Class 2 (scratch roots from `getconf`, pre-trust guard, fail-closed exits), applied to the Mac, Jetson, and Windows copies to keep the scripts byte-identical. The rule-layer allows live in `mac/harness/settings.json`, `mac/harness/settings.json.template`, and `jetson/harness/settings.json.template`.
