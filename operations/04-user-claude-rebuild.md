# Post-Mac 4 — Rebuild ~/.claude/ from harness as source of truth

## Operational preconditions (read before invoking)

Open a fresh Claude Code session before running this prompt. Do not continue a session that ran Operations 1-3. The reason is concrete: this prompt modifies files in the active session's cached prefix (`~/.claude/CLAUDE.md`, `~/.claude/settings.json`, the loaded hook scripts). Mid-session modification of files the session is reading from is undefined behavior in Claude Code.

Run the session from `/Users/klambros/harness-engineering/` as the working directory, not from `~/.claude/`. Reads of `mac/harness/` are inside cwd and no-prompt. Writes to `~/.claude/` require explicit per-write interactive approval (assuming `additionalDirectories` is not pre-set), which is desirable for a destructive operation. The session that does the rebuild ends with the new `~/.claude/` on disk but does not benefit from it; its own context was loaded at start. The first session AFTER this one is the first running under the rebuilt harness.

<role>
You are executing the operational rebuild Phase 2 Q3 elected: replace the destructive subset of `~/.claude/` with content sourced from `mac/harness/`, preserve Rock's personal configuration by default, and initialize a separate private git repo at `~/.claude/` for backup and change tracking. This is the most destructive operation in the post-Mac-execution sequence. Every destructive action requires Rock's explicit confirmation before execution.

You are working OUTSIDE the harness-engineering repo. The repo is the read-only source. `~/.claude/` is the write target. The two are explicitly separate.

The current `~/.claude/` carries: SuperClaude framework files (~16.6k tokens across FLAGS.md, PRINCIPLES.md, RULES.md, five MODE_*.md, six MCP_*.md), 16 plugins in enabledPlugins, a plaintext Hetzner API token in `mcp.json` (HIGH-severity Phase 1 finding), the `skipDangerousModePermissionPrompt: true` setting (Q9 says REMOVE), 56 dangling symlinks under `commands/zerg/`, 4311 accumulated session logs, and a wide range of files Rock built up over time.

The rebuild's posture is default-keep for Rock's personal configuration. SuperClaude framework files, the 16-plugin enabledPlugins list, and the contents of `~/.claude/commands/` carry forward unless Rock explicitly elects replacement during the confirmation gate. Only four classes of items get touched without explicit per-item confirmation: the four non-negotiables (plaintext secrets, `skipDangerousModePermissionPrompt: true`, dangling symlinks, session logs older than 90 days) and items the executing session detects a specific concern about (which Rock confirms or overrides at the gate). Everything else preserves.
</role>

<effort>xhigh</effort>

<mode>plan mode for stages 1 through 3 (read, inventory, plan). Default mode only for stages 4 onward, and only after Rock explicitly confirms the plan via AskUserQuestion.</mode>

<thinking>adaptive</thinking>

<context_budget>Run /context at start and end. Phase reads the entire mac/harness/ tree, the current ~/.claude/ tree, and produces detailed plan and execution logs. Cache load is substantial. Record state in `phase-outputs/POST-MAC-4-CONTEXT.md`.</context_budget>

<parallel_tool_calls>
Read the mac/harness/ source in parallel: `mac/harness/CLAUDE.md`, `mac/harness/settings.json`, every file in `mac/harness/hooks/`, `mac/harness/rules/`, `mac/harness/skills/`, `mac/harness/agents/`.

Read the current `~/.claude/` state in parallel: `~/.claude/CLAUDE.md`, `~/.claude/settings.json`, `~/.claude/mcp.json` (handle absence gracefully), then a directory listing of `~/.claude/` top-level and one level deep.
</parallel_tool_calls>

<scope>
Read-only: anything in `/Users/klambros/harness-engineering/` (the harness repo).

Write target: `~/.claude/` directly. Outside the harness repo.

Build-internal records (inside the harness repo): `phase-outputs/POST-MAC-4-CONTEXT.md`, `phase-outputs/POST-MAC-4-PLAN.md`, `phase-outputs/POST-MAC-4-BACKUP.md`, `phase-outputs/POST-MAC-4-EXECUTION.md`, `phase-outputs/POST-MAC-4-VERIFICATION.md`.

Do not modify any file in `mac/`, `jetson/`, `windows/`, `foundation/`, `research/`, or `scripts/`.
</scope>

## What to do

Six stages. Each stage's output is a prerequisite for the next. Do not skip ahead.

### Stage 1: Backup

Create a full backup of the current `~/.claude/` tree at `~/.claude.backup-<YYYYMMDD-HHMMSS>/`. Use `cp -a` or `rsync -a` to preserve permissions, symlinks, and timestamps. Verify the backup by comparing file counts and total size against the source. If verification fails, abort and do not proceed.

Document the backup location, file count, and size in `phase-outputs/POST-MAC-4-BACKUP.md`.

### Stage 2: Inventory current state

Read every file in `~/.claude/` that the rebuild will touch. Build a manifest of what's there:

- Every CLAUDE.md and its @import chain
- settings.json contents
- mcp.json contents
- Every plugin in enabledPlugins
- Every hook script (whose enforcement model and whose origin)
- Every skill (which were Rock-authored, which were upstream)
- Every command (and which are dangling symlinks)
- The session log count and oldest log date
- The cumulative size of the `~/.claude/` tree

Apply the pre-trust audit pattern from `mac/harness/skills/mcp-server-pre-trust-audit/SKILL.md`. Any unsigned executable, any unexpected hook registration, any MCP server not on a whitelist gets called out.

Secret handling discipline. When you find a plaintext secret in any file: name the key, the file, and the shape of the problem (plaintext rather than env-var indirection). Never name the value. If reading a file would surface the value, redact it before recording anything in the inventory. The inventory file is committed to disk and may end up in conversation context; the value must not.

Document the inventory in the plan file under §Current State.

### Stage 3: Plan

Produce `phase-outputs/POST-MAC-4-PLAN.md`. The plan organizes every file in `~/.claude/` into one of five sections. Default-keep is the posture for everything not explicitly listed in the first four sections.

**§Files to write new**. Each file with its source path (from `mac/harness/`) and destination path (in `~/.claude/`). The harness deliverables: `~/.claude/CLAUDE.md` (from `mac/harness/CLAUDE.md`), `~/.claude/hooks/` (from `mac/harness/hooks/`), `~/.claude/skills/` (from `mac/harness/skills/`), `~/.claude/agents/` (from `mac/harness/agents/`), the populated `~/.claude/settings.json` (from `mac/harness/settings.json` minus the Q9 removal).

**§Files to modify**. Each file with the specific edit. The four non-negotiables: settings.json's `skipDangerousModePermissionPrompt` key removed (Q9). The plaintext Hetzner API token in mcp.json replaced with env-var indirection (security; Rock places the token in Keychain or a shell rc file separately, the prompt does not embed it). Any other plaintext secret found in Stage 2 receives the same treatment.

**§Files to delete**. Each file with the reason. Limited set: dangling symlinks under `commands/zerg/` (functionally broken, the targets do not exist). Session logs older than 90 days in `projects/<encoded-cwd>/` (Q11 retention; this is the initial backlog prune, the Stop hook handles the ongoing cadence).

**§Files to classify**. Files where Stage 2 detected a specific concern that warrants explicit Rock confirmation. Each entry includes: file path, concern reason, recommended classification (keep / replace with harness equivalent / merge content into harness CLAUDE.md / retire), and the executing session's reasoning for the recommendation. Triggers for landing in this section, not exhaustive:

- Orphan reference: e.g., a SuperClaude `MCP_<server>.md` whose underlying MCP server is being retired in this rebuild.
- Redundancy with new harness CLAUDE.md: e.g., a SuperClaude file whose content is substantively duplicated by `mac/harness/CLAUDE.md`'s advisory section.
- Broken state: e.g., a plugin in enabledPlugins whose source directory or manifest does not exist anymore.
- Conflicting state: e.g., a setting in current `~/.claude/settings.json` that conflicts with a setting in `mac/harness/settings.json` and Phase 2's answer did not settle which wins.

Default for any file the session does not flag with a specific concern is preservation. If §Files to classify ends up empty after Stage 2, that's a valid outcome and Stage 4 confirms preservation as the bulk action.

**§Files to preserve**. Every file in `~/.claude/` not listed in one of the four sections above, named individually. SuperClaude framework files (FLAGS.md, PRINCIPLES.md, RULES.md, five MODE_*.md, six MCP_*.md) land here unless flagged in §Files to classify. The 16-plugin enabledPlugins list entries land here unless flagged. The contents of `~/.claude/commands/` (minus the dangling symlinks) land here. Anything else not actively touched lands here.

Also enumerate in the plan: every MCP server in current mcp.json (which carry forward, which get re-registered with env-var indirection for secrets, which get retired); the post-rebuild `git init` at `~/.claude/`; the `.gitignore` for `~/.claude/` (different from the repo's; session logs and cache excluded); the initial commit message.

The plan is the contract for Stage 4. Nothing executes that isn't in the plan.

### Stage 4: Confirm

Present the plan to Rock via `AskUserQuestion`. Single question, three options:

- **Proceed**: execute the plan as written
- **Modify**: explain what to change in the next message; Stage 3 re-runs the affected portions, the plan updates, this stage re-asks
- **Abort**: stop the entire phase

The question wording references the plan file by path and instructs Rock to read it before answering. Every §Files to classify entry must be visible in the plan file; Rock reviews them there.

If Rock chooses "Modify," collect his modifications, update the plan file, re-present. Loop until "Proceed" or "Abort."

If "Abort," stop the entire phase. Document the abort reason in the execution log.

### Stage 5: Execute

Execute the plan file by file. After each destructive action, append a log entry to `phase-outputs/POST-MAC-4-EXECUTION.md` with the action, the path, the result, and a checksum where applicable.

Stop on any error. Errors are not retried automatically; surface to Rock for direction.

Critical execution constraints:

- The plaintext Hetzner API token NEVER carries forward in clear. The new mcp.json uses env-var indirection.
- `skipDangerousModePermissionPrompt` is removed from the new settings.json (or explicitly set to `false`). Q9 settled this.
- The 56 dangling symlinks under `commands/zerg/` are not recreated.
- Files in §Files to preserve are NOT modified during execution. Not reorganized, not tidied, not "improved." Preservation means the file ends Stage 5 byte-identical to how it began (modulo the file possibly being moved if the rebuild restructures directories, in which case the file's content stays identical).
- Files in §Files to classify execute per Rock's confirmation at Stage 4. The recommended classification holds unless Rock overrode it.

### Stage 6: Verify

Post-execution, verify the rebuilt `~/.claude/` state:

- `~/.claude/CLAUDE.md` matches `mac/harness/CLAUDE.md` content (or is its explicit user-level lean form).
- `~/.claude/settings.json` parses as strict JSON. Contains no `skipDangerousModePermissionPrompt: true`.
- `~/.claude/mcp.json` contains no plaintext secret values. Env-var indirection is in place for any secret referenced.
- The previously dangling symlinks in `commands/zerg/` are gone.
- Every file in §Files to preserve is byte-identical to its pre-rebuild state. Spot-check by checksum against the backup.
- `bash /Users/klambros/harness-engineering/scripts/drift-check.sh` returns 0 (the widened drift-check from Operation 1 measures user-level too; the rebuilt user-level keeps the combined worst-case under target, or surfaces a WARN that informs follow-up trimming).
- The backup at `~/.claude.backup-<timestamp>/` is intact and verifiable.
- Run a fresh Claude Code session against any test project. Confirm the new hooks, deny rules, and skills load. Confirm the auto-mode classifier behaves per Q1's enabled-with-tightened-denies posture.

Initialize the private git repo: `cd ~/.claude && git init && git add . && git commit -m "Initial rebuild from harness-engineering Mac Phase 5"`. The `.gitignore` for this private repo excludes `projects/` (session logs), `cache/`, and `local/` per Phase 2 decisions.

Document everything in `phase-outputs/POST-MAC-4-VERIFICATION.md`.

<investigate_before_answering>
Before declaring the backup verified, compare file count, total size, and a sample of file checksums between source and backup. A `cp -a` that returned 0 but truncated for some reason is a real failure mode.

Before declaring a plaintext secret resolved by env-var indirection, confirm the indirection actually works. Set the env var, invoke the MCP server, verify it authenticates. A `${HETZNER_API_TOKEN}` literal that the runtime does not interpolate is worse than the plaintext it replaced.

Before flagging a file into §Files to classify under "orphan reference," verify the underlying retirement is real. A SuperClaude `MCP_<server>.md` whose corresponding server stays in the rebuilt mcp.json is not orphaned and should not be flagged.

Before flagging a file under "redundancy with harness CLAUDE.md," diff the content. Substantive duplication means the same instruction appears in both, not just thematic overlap.
</investigate_before_answering>

## Deliverables

- `~/.claude.backup-<timestamp>/`: full pre-rebuild backup, verified
- `~/.claude/`: rebuilt tree with the four non-negotiables resolved, classification choices applied, and personal configuration preserved
- `~/.claude/.git/`: private repo initialized, initial commit made
- `phase-outputs/POST-MAC-4-BACKUP.md`: backup manifest with verification result
- `phase-outputs/POST-MAC-4-PLAN.md`: the plan Rock confirmed at Stage 4, with the five named sections
- `phase-outputs/POST-MAC-4-EXECUTION.md`: file-by-file action log
- `phase-outputs/POST-MAC-4-VERIFICATION.md`: post-rebuild state verification
- `phase-outputs/POST-MAC-4-CONTEXT.md`: context-budget record

## Verification

Before reporting complete:

- Backup verified (file count, total size match source).
- `~/.claude/settings.json` and `~/.claude/mcp.json` parse as strict JSON.
- No plaintext secrets in `~/.claude/mcp.json`. Verify via the same secret-scan regex that pre-commit uses on the harness repo.
- Drift check (widened per Operation 1) returns 0 or WARN (not FAIL).
- A fresh Claude Code session loads cleanly. Hooks fire when expected. Deny rules block when expected.
- The private git repo at `~/.claude/.git/` exists. `cd ~/.claude && git log` shows the initial commit.
- The backup at `~/.claude.backup-<timestamp>/` is reachable and the file count matches the pre-rebuild count.
- Spot-check: pick three preserved files (one SuperClaude framework file, one plugin's config, one custom command), compare checksum against backup, confirm byte-identical.

Report the file counts (pre and post), the secret-scan result, the drift-check output, the new HEAD SHA in the private repo, the §Files to classify entries with their final dispositions, and any plugins or files retained that were not in the plan (with explanation).

## Anti-overengineering

Do not invent new framework files. Do not add a lean SuperClaude replacement beyond what `mac/harness/CLAUDE.md` already is. Preserved files (every file not listed in §Files to write new / §Files to modify / §Files to delete, plus any §Files to classify entry Rock elected to keep) carry forward unmodified; the executing session does not improve, reorganize, or clean up preserved files even when the local change feels small and helpful.

This is a rebuild from a source that already exists. Do not migrate Rock's session logs to a new format. The session log directory carries forward as-is, subject to the 90-day pruning per Q11.

Do not extend the private `~/.claude/` git repo with content that doesn't belong (history files generated post-rebuild, machine-specific paths). The initial commit captures the rebuild state; growth happens via Rock's daily use.

Do not skip the backup. Do not skip the confirmation. Do not skip the verification. Each is load-bearing.

If at any stage you find that the plan or the execution surfaces a class of change Rock did not anticipate, stop and ask. The cost of asking is lower than the cost of an unexpected `~/.claude/` state Rock has to reconstruct from backup.
