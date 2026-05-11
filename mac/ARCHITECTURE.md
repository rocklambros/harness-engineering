# Mac harness architecture

The Mac build of the harness. This document is the operational reference for how the nine harness components from `foundation/02-architectural-principles.md` land on macOS Apple Silicon. Blocks marked `<TBD-PHASE-0>` are filled by the Phase 0 session against the live environment and re-evaluated on Claude Code minor-version bumps per QC.5.

The document follows the SAGE nine-component decomposition (§4) and operationalizes each Quality Contract property per `foundation/00-quality-contract.md` for this platform.

## Environment baseline

| Property | Value |
|---|---|
| Operating system | macOS on Apple Silicon (ARM64) |
| macOS version pin | 26.3, build 25D125, Darwin kernel 25.3.0 |
| Hardware | M-series Apple Silicon |
| Shell | zsh (default on modern macOS) |
| Package manager | Homebrew 5.1.10 |
| Node version | v24.10.0 |
| Python version | 3.13.9 (Anaconda distribution at `/opt/anaconda3/bin/python3`) |
| Claude Code version pin | v2.1.* (currently 2.1.138). Range per QC.5. |
| Working directory | `/Users/klambros/harness-engineering/` |
| Daily-driver harness path | In-repo at `mac/harness/`. Not symlinked into `~/.claude/`. Symlink-vs-in-repo decision deferred to Phase 2 interview. |

The version pins are not aspirational. They are recorded after Phase 0 verifies what is actually installed, and they drive the next-evaluation triggers in the §Version pins section below.

## The nine harness components on Mac

### 1. Agent loop

Owned by Claude Code itself. The harness configures it through model selection, effort level, and session mode.

- Default model: `claude-opus-4-7` (Opus 4.7, 1M context). The build session runs on Opus and same-family subagents preserve cache lineage per QC.4a. Routine daily-driver work overrides at session start with `--model sonnet` when cost dominates.
- Effort level: `xhigh` for build phases, `high` for routine work
- Session mode default: `default` permission mode
- Compaction posture: continuous, no manual resets unless a model-version change makes the heuristic stale (SAGE §5.1 recommendation 5; Rajasekaran's retrospective documents that context resets necessary on Opus 4.5 became unnecessary on 4.6)

### 2. Instruction layer

Three CLAUDE.md files participate in the cached prefix.

- `/Users/klambros/harness-engineering/CLAUDE.md` (build-time, governs work on this repo)
- `mac/harness/CLAUDE.md` (operational, governs daily Claude Code sessions)
- `~/.claude/CLAUDE.md` participates automatically in every session via Claude Code's CLAUDE.md hierarchy walk. The file is ~17 lines / ~553 tokens. The user-level SuperClaude framework (`~/.claude/FLAGS.md`, `PRINCIPLES.md`, `RULES.md`, `MODE_*.md`, `MCP_*.md`) loads alongside it at ~16.6k tokens.

Combined line total across the project hierarchy stays under 400 per QC.4b. The drift check in `scripts/drift-check.sh` enforces the cap and is scoped to the project hierarchy by design. The user-level load is acknowledged but not gated by drift-check; Phase 2 decides whether to widen the check's scope. The current build-time file is 91 lines; the operational file is sized in Phase 3 and Phase 4 as features land.

### 3. Tool pool

Built-in tools enabled by default, custom tools, MCP-exposed tools. Assembled by the Claude Code runtime at session start.

Default enabled built-ins on Claude Code v2.1.138, observed via `/context`:

- Always loaded (9): `Agent`, `AskUserQuestion`, `Bash`, `Edit`, `Read`, `ScheduleWakeup`, `Skill`, `ToolSearch`, `Write`.
- Deferred and loaded on demand via `ToolSearch` (22): `CronCreate`, `CronDelete`, `CronList`, `EnterPlanMode`, `EnterWorktree`, `ExitPlanMode`, `ExitWorktree`, `LSP`, `ListMcpResourcesTool`, `Monitor`, `NotebookEdit`, `PushNotification`, `ReadMcpResourceTool`, `RemoteTrigger`, `TaskCreate`, `TaskGet`, `TaskList`, `TaskOutput`, `TaskStop`, `TaskUpdate`, `WebFetch`, `WebSearch`.

Custom and MCP tools land in Phase 4. Each is filtered by deny rules (Phase 3 deliverable) and mode (per-session).

Per Claude_Architecture.md §6.2, the `getAllBaseTools()` enumeration returns up to 54 tools, with 19 always included and 35 conditionally based on feature flags. The default subset Phase 0 inherits from Claude Code is the starting position; the harness narrows from there.

### 4. Permission layer

The deny-first, ask-by-default permission system from Claude_Architecture.md §5 lands here.

- Permission mode default: `default` (interactive approval with deny-rule pre-filtering). Least privilege per Principle 2.
- Auto-mode classifier: disabled by default per Principle 2. Deferred to Phase 2 interview for confirmation or override. Hughes 2026's 0.4% false-positive rate is small but the threat model (cybersecurity executive, sensitive credentials, three machines with push access) favors interactive approval friction over automated approval.
- Deny rules: live in `mac/harness/rules/` (Phase 3 populates)
- Hook gates: live in `mac/harness/hooks/` (Phase 3 populates)
- MCP server-prefix denies: deferred to Phase 4. The list of denied servers depends on which servers Phase 4 adopts; the default posture is deny-all-except-allowlist.

Hooks enforce. CLAUDE.md advises. Every rule that must hold every time lives in a hook script, not in an advisory instruction. This is the load-bearing decision from `foundation/02-architectural-principles.md` Principle 1.

### 5. Context pipeline

- Compaction: automatic (Claude Code's built-in five-layer compaction per Claude_Architecture.md §7)
- System reminders: used for any dynamic content that would otherwise pollute the cached prefix, per QC.4b
- File references: discovered in Phase 1, recorded in `phase-outputs/INVENTORY.md`
- Context resets: not used by default (per SAGE §5.1 recommendation 5)
- PreCompact / PostCompact hooks: deferred to Phase 3. Hook registration is Phase 3's deliverable; Phase 0 records the intent that compaction-lifecycle hooks remain unregistered unless Phase 3's deep evaluation finds a specific failure mode worth gating.

### 6. Sandbox

Independent of the permission layer. Operates on filesystem and network isolation axes per Claude_Architecture.md §5.4.

- Bash sandboxing: deferred to Phase 3. Claude Code v2.1.138 CLI exposes no direct sandbox flag. The permission system (deny rules + interactive approval) is the primary enforcement layer per Principle 1. macOS `sandbox-exec` (`/usr/bin/sandbox-exec`) is available as an OS primitive but Claude Code's documented use of it is not visible from `claude --help`. Phase 3 verifies the `sandbox` block in `mac/harness/settings.json.template` behaviorally against the installed runtime and either enables it, removes it, or replaces it with permission-layer equivalents.
- Filesystem isolation: deferred to Phase 3, coupled with the Bash sandboxing decision. Until Phase 3, the permission layer's deny rules carry the protection — writes outside the working directory will be Phase 3's deny-rule responsibility, not a sandbox-level concern.
- Network egress restrictions: deferred to Phase 3 for sandbox-level controls and to Phase 4 for MCP-server egress posture. No OS-level egress monitor (Little Snitch, LuLu, OpenSnitch) is installed on this machine; Phase 4 evaluates whether to install one as part of MCP server posture.
- Exclusion patterns for sandbox opt-out: deferred to Phase 3. If Phase 3 enables a sandbox, the exclusion patterns will be recorded with rationale at that time.

### 7. MCP integration

Each MCP server is a permission grant. Allowlisting and pre-trust audit are the discipline.

- MCP allowlist: managed in `mac/harness/settings.json` (Phase 4 populates)
- Default posture: deny all MCP servers not on the allowlist
- Pre-trust audit habit: every cloned repository's `.claude/settings.json` and `.mcp.json` get reviewed before opening the project in Claude Code. Defense against the CVE-2025-59536 / CVE-2026-21852 class (pre-trust initialization execution).
- Network egress per MCP server: deferred to Phase 4. Per-server constraints get recorded alongside each server's allowlist entry when Phase 4 evaluates and adopts the server.

### 8. Subagent delegation

The Task tool and worktree isolation. Subagent model selection has cost and cache-economy consequences per QC.4a.

- Worktree isolation: enabled
- Default subagent model: `claude-opus-4-7` (same family as the main session default). Per QC.4a, same-family parent/subagent share cache and the cache-economy gain on a build of this size outweighs the per-invocation cost difference vs. Haiku. Per-Task invocations override to Sonnet or Haiku explicitly when the workload favors cost over cache continuity (file-scan inventory, parallelizable verification work).
- When to spawn a subagent: file-scan tasks touching more than 20 files, verification work the main session would benefit from running in parallel, and the Phase 5 Reviewer pattern. Phase 2 interview refines the policy.

### 9. Persistence

The session log is the only durable component per SAGE §4.10.

- Session log location: `~/.claude/projects/<encoded-cwd>/<session-uuid>.jsonl`. The encoded-cwd replaces `/` with `-`. For this project the directory is `~/.claude/projects/-Users-klambros-harness-engineering/`. Format is JSONL, one event per line.
- Session log retention: indefinite by default. The machine currently holds 4311 session logs across all projects; the oldest dates to 2026-03-19. A `~/.claude/.last-cleanup` marker indicates some cleanup mechanism exists but it is not aggressive. Retention policy decision deferred to Phase 2 interview — disk usage, privacy posture, and replay-value tradeoffs are personal-preference calls.
- Memory tools: MemPalace is installed and evaluates in Phase 4 against alternatives; not auto-adopted
- Compaction interaction: session log persists across compactions; harness state does not

## Quality Contract operationalization

| QC | Mac implementation |
|---|---|
| QC.1 Security | Homebrew pins via `Brewfile.lock` (deferred to Phase 3 for creation); SBOM via `syft` (Phase 3 evaluates); secret scan via `detect-secrets` (pre-commit wired in Batch 1, but the binary is currently not installed per PREFLIGHT — Phase 3 installs or substitutes); SAST via `semgrep` (installed but broken on `opentelemetry-sdk.LogData` ImportError per PREFLIGHT — Phase 3 fixes or substitutes) |
| QC.2 Tight code | Reviewer subagent in Phase 5 audits scope. No new abstractions, no new test scaffolding without explicit decision. |
| QC.3 Comments | Comment the why. Hook scripts in `mac/harness/hooks/` carry rationale comments on each deny pattern. |
| QC.4a Cache (API/SDK) | Direct Anthropic API use carries explicit `"ttl": "1h"` on cache_control. Telemetry on. Documented in `mac/harness/settings.json.template`. |
| QC.4b Cache (Claude Code) | CLAUDE.md hierarchy under 400 lines total. `scripts/drift-check.sh` enforces. `<system-reminder>` blocks carry dynamic content. |
| QC.5 Versioning | Claude Code pinned to `v2.1.*` minor-version range (currently 2.1.138). Re-evaluation trigger: minor bump (v2.2.x). |

## Threat model adaptations for Mac

The threats in `foundation/01-threat-model.md` apply unchanged. Mac-specific notes:

- **macOS Gatekeeper and code signing**: assumed enabled. Disabled Gatekeeper is a host-OS misconfiguration that the harness does not defend against.
- **FileVault disk encryption**: assumed enabled. The harness's secret-protection posture relies on the host disk being encrypted at rest.
- **Keychain**: used for credential storage where applicable. The harness does not write secrets to plain files in the working directory.
- **System Integrity Protection (SIP)**: assumed enabled. SIP is not the harness's defense layer, but the harness expects it to be active.
- **Network egress monitoring**: not installed. Verified via `/Applications/` scan (no Little Snitch, LuLu, Radio Silence, Hands Off, Murus, or OpenSnitch) and `launchctl list` (no related daemons). Not required by the harness. Phase 4 evaluates whether to install one as part of the MCP egress posture; the discipline of reviewing MCP egress in real time is easier with one but the current threat model treats the OS-level monitor as a defense-in-depth nice-to-have rather than a primary control.

## Build state

- Foundation documents: written and committed (Batch 1)
- Mac section structure: written and committed (Batch 2)
- Phase 0 blocks in this document: filled 2026-05-11. Next re-evaluation on Claude Code minor-version bump per QC.5.
- Phase 1 (discovery): not yet executed
- Phase 2 (architecture interview): not yet executed
- Phase 3 (deterministic layer): not yet executed
- Phase 4 (extension layer): not yet executed
- Phase 5 (wire and document): not yet executed

Each phase output lands in `phase-outputs/` (build-internal, gitignored). Phase 5 produces the final polished form of this document, replacing every `<TBD-PHASE-0>` with the recorded value and adding the next-evaluation triggers below.

## Version pins

Filled by Phase 0. Re-evaluated on every Claude Code minor-version bump.

| Component | Pinned version | Next-evaluation trigger |
|---|---|---|
| Claude Code | v2.1.* (currently 2.1.138) | Minor-version bump (v2.2.x) |
| macOS | 26.3 (25D125) | Major-version release (macOS 27) |
| Node | v24.10.0 | Node LTS major (v26 LTS) |
| Python | 3.13.9 | Python minor release (3.14 / 3.15) |
| Homebrew | 5.1.10 | Quarterly review (next: 2026-08-10) |
| Semgrep | deferred — installed but broken (ImportError on `opentelemetry.sdk._logs.LogData`); Phase 3 fixes or substitutes | Resolution of the broken state, then security advisory or major release |
| MemPalace | deferred to Phase 4 (installed; adoption decision pending against alternatives) | Set in Phase 4 |
| Serena | deferred to Phase 4 (installed via plugin; adoption decision pending against alternatives) | Set in Phase 4 |

Additional seeds adopted in Phase 3 or Phase 4 land in this table with their pin and trigger.
