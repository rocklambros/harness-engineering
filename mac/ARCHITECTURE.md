# Mac harness architecture

The Mac build of the harness. This document is the operational reference for how the nine harness components from `foundation/02-architectural-principles.md` land on macOS Apple Silicon. The harness is built and validated; the SAGE nine-component decomposition (§4) organizes the document, and the Quality Contract from `foundation/00-quality-contract.md` operationalizes per platform.

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
| Daily-driver harness path | In-repo source of truth at `mac/harness/`. Phase 2 Q3 elected to rebuild `~/.claude/` from scratch as a post-build operational step; the harness reference under `mac/harness/` is the template for that rebuild. |

Version pins are recorded after Phase 0 verifies the live environment and drive the §Version pins section below.

## The nine harness components on Mac

### 1. Agent loop

Owned by Claude Code itself. The harness configures it through model selection, effort level, and session mode.

- Default model: `claude-opus-4-7` (Opus 4.7, 1M context). The build session runs on Opus and same-family subagents preserve cache lineage per QC.4a. Routine daily-driver work overrides at session start with `--model sonnet` when cost dominates.
- Effort level: `xhigh` for build phases, `high` for routine work.
- Session mode default: `auto` permission mode (Phase 2 Q1). The ML classifier (Hughes 2026, 0.4% false-positive rate) handles ambient approvals; Phase 3 deny rules carry the deterministic floor under it.
- Compaction posture: continuous, no manual resets unless a model-version change makes the heuristic stale.

### 2. Instruction layer

Three CLAUDE.md files participate in the cached prefix.

- `/Users/klambros/harness-engineering/CLAUDE.md` (build-time, governs work on this repo)
- `mac/harness/CLAUDE.md` (operational, governs daily Claude Code sessions; 81 lines after Phase 5 polish)
- `~/.claude/CLAUDE.md` participates automatically in every session via Claude Code's hierarchy walk. Phase 1 inventory measured ~17 lines plus a SuperClaude framework @import chain totaling ~800-900 lines. Phase 2 Q3 elected to rebuild the user-level config lean (no transitive @import chain or a deliberate small one with explicit budget); the rebuild is a post-Phase-5 operational step.

Project-hierarchy line total stays under 400 per QC.4b. The drift check in `scripts/drift-check.sh` enforces the cap. Phase 2 Q10's widening of the check to include the user-level `~/.claude/CLAUDE.md` plus its transitive `@import` chain landed 2026-05-11 (commit `920d5e7`). The widened check currently reports FAIL because the legacy SuperClaude framework chain totals 973 lines; the Q3 `~/.claude/` rebuild trims the chain and clears the gate.

### 3. Tool pool

Default enabled built-ins on Claude Code v2.1.138, observed via `/context`:

- Always loaded (9): `Agent`, `AskUserQuestion`, `Bash`, `Edit`, `Read`, `ScheduleWakeup`, `Skill`, `ToolSearch`, `Write`.
- Deferred and loaded on demand via `ToolSearch` (22): `CronCreate`, `CronDelete`, `CronList`, `EnterPlanMode`, `EnterWorktree`, `ExitPlanMode`, `ExitWorktree`, `LSP`, `ListMcpResourcesTool`, `Monitor`, `NotebookEdit`, `PushNotification`, `ReadMcpResourceTool`, `RemoteTrigger`, `TaskCreate`, `TaskGet`, `TaskList`, `TaskOutput`, `TaskStop`, `TaskUpdate`, `WebFetch`, `WebSearch`.

Per Claude_Architecture.md §6.2, `getAllBaseTools()` returns up to 54 tools; the default subset is the starting position and the harness narrows from there via deny rules and MCP allowlist.

### 4. Permission layer

The deny-first, ask-by-default permission system from Claude_Architecture.md §5 lands here. Phase 2 elected the auto-mode classifier (Q1); Phase 3 wrote the deterministic floor under it.

- **Permission mode default**: `auto`. The classifier handles ambient cases; the deny rules below catch the rest.
- **Deny rules (6, in `mac/harness/rules/`)**:
  - `bash-deny-git-push-force.md` — `git push --force`, `-f`, `--force-with-lease`. Principle 3 (reversibility) and Asset #1 (source code integrity).
  - `bash-deny-dangerously-skip-permissions.md` — bypass mode invocations. Principle 1 (hooks enforce) and Q9.
  - `bash-deny-sudo.md` — root execution. Principle 2 (least privilege).
  - `bash-deny-rm-rf-root.md` — `rm -rf /`, `~/`, `$HOME`, `/Users/`. Principle 3 (reversibility).
  - `filesystem-deny-write-secrets.md` — Write/Edit to `.env`, `secrets/`, `credentials.json`. Asset #2 (secrets).
  - `mcp-deny-server-prefix-default.md` — no pattern; documents the structural mechanism (empty `mcpServers` + Phase 4 entries = no unlisted server reaches the pool). Threat actors #6.
- **Hooks (6, in `mac/harness/hooks/`, all Python)**:
  - `PreToolUse-bash-cap-subcommands.py` — denies Bash chains over 30 subcommands. Phase 2 Q6, defense in depth below the Adversa.ai 2026 documented 50 threshold.
  - `PreToolUse-external-write-gate.py` — asks confirmation on Write/Edit/MultiEdit/NotebookEdit outside cwd. Principle 3.
  - `PreToolUse-supply-chain-bash-checks.py` — asks on `npx -y`, `uvx --from git+` without ref, `@latest`, unpinned `pip install`, `curl|sh`. Phase 2 Q2a T2.
  - `PreToolUse-cached-prefix-write-gate.py` — asks on writes to CLAUDE.md hierarchy, `foundation/`, user-level @import targets. Phase 2 Q2a T5 (implemented as PreToolUse rather than PostToolUse because the intent is gating).
  - `SessionStart-audit-claude-config.py` — blocks session if in-repo `.claude/settings.json` / `.claude/settings.local.json` / `.mcp.json` has sha256 absent from `~/.claude/audited-hashes.json`. Phase 2 Q2b T3 + Q5 every-clone cadence.
  - `Stop-prune-session-logs.py` — deletes `~/.claude/projects/*.jsonl` older than 90 days with 24h marker guard. Phase 2 Q11.
- **MCP server-prefix denies**: managed structurally via `mcpServers` allowlist rather than a blanket deny pattern (deny-first ordering would override Phase 4 allows). See `mac/harness/rules/mcp-deny-server-prefix-default.md` for the design.

Hooks enforce. CLAUDE.md advises. Every rule that must hold every time lives in a hook script, not in an advisory instruction. This is the load-bearing decision from `foundation/02-architectural-principles.md` Principle 1.

### 5. Context pipeline

- Compaction: automatic (Claude Code's built-in five-layer compaction per Claude_Architecture.md §7).
- System reminders: used for dynamic content that would otherwise pollute the cached prefix, per QC.4b.
- File references: discovered in Phase 1, recorded in `phase-outputs/INVENTORY.md`.
- Context resets: not used by default.
- PreCompact / PostCompact hooks: not registered. Phase 3 deep-evaluation found no failure mode that justified compaction-lifecycle gating; the default position holds.
- Cached-prefix write protection: `PreToolUse-cached-prefix-write-gate.py` gates Write/Edit against CLAUDE.md hierarchy, `foundation/`, and user-level @import targets. Cache poisoning (Threat actors #5) requires deliberate confirmation, not accidental edit.

### 6. Sandbox

Independent of the permission layer. Operates on filesystem and network isolation axes per Claude_Architecture.md §5.4.

- **Bash sandboxing**: disabled. Claude Code v2.1.138 CLI exposes no direct sandbox flag (verified by `claude --help`). The permission system (deny rules + interactive approval + auto-mode classifier) is the primary enforcement layer per Principle 1. macOS `sandbox-exec` is available as an OS primitive but the runtime's documented use of it is not visible from the CLI. Re-evaluate on Claude Code minor bump per QC.5.
- **Filesystem isolation**: covered by `PreToolUse-external-write-gate.py` rather than sandbox-level enforcement. Writes outside cwd ask for confirmation.
- **Network egress restrictions**: covered by MCP allowlist (extension layer) and per-server review (Phase 4). No OS-level egress monitor installed; Phase 2 Q7 elected to skip OS-level monitor installation. The permission layer + MCP allowlist carry the load.
- **Exclusion patterns**: not applicable while the sandbox stays disabled.

### 7. MCP integration

Each MCP server is a permission grant. Allowlisting and pre-trust audit are the discipline.

- **MCP allowlist**: managed via `enabledPlugins` (plugin-shipped servers) and `mcpServers` (direct registrations) in `mac/harness/settings.json`.
- **Phase 4 calibrated minimum**:
  - `superpowers@claude-plugins-official` v5.1.0 — skills collection (no MCP server). 14 skills + 1 SessionStart hook + 0 agents (Phase 1 INVENTORY's 17/4/1 figure double-counted; verified via direct listing of the v5.1.0 cache during Phase 5 audit).
  - `mempalace@mempalace` v3.3.2 — memory MCP server + 1 skill. 39 mempalace_* tools (deferred-load via ToolSearch).
- **`mcpServers` direct**: empty in the harness reference. Phase 5 daily-driver review expands for Rock's daily use against the rebuilt `~/.claude/settings.json` per Q3.
- **Default posture**: deny all MCP servers not on the allowlist. Unlisted servers do not reach `getAllBaseTools()` at tool pool assembly time.
- **Pre-trust audit habit**: SessionStart hook gates in-repo `.claude/`/`.mcp.json` files. Direct MCP server additions go through the `mcp-server-pre-trust-audit` skill in `mac/harness/skills/`.
- **context7 supply-chain note**: the plugin's `.mcp.json` declares `npx -y @upstash/context7-mcp` (unpinned). Phase 4 elected not to enable in the harness reference; Phase 5 daily-driver review picks between pinning the npx version, globally installing with a pin and invoking by absolute path (already at v2.1.3 on machine), or skipping.

### 8. Subagent delegation

The Agent tool and worktree isolation. Subagent model selection has cost and cache-economy consequences per QC.4a.

- **Worktree isolation**: enabled.
- **Default subagent model**: `claude-opus-4-7` (same family as the main session default). Same-family parent/subagent share cache per QC.4a; the cache-economy gain on a build of this size outweighs the per-invocation cost difference vs Haiku.
- **Custom agent definitions (2, in `mac/harness/agents/`)**:
  - `reviewer.md` — Phase 5 Writer/Reviewer pattern. Audits Phase 5 outputs against QC + threat model + principles. Returns structured findings; does not edit. Same-family Opus 4.7 cache lineage.
  - `inventory.md` — read-only discovery scan, codifies the Phase 1 role for future re-runs.
- **When to spawn**: file-scan tasks touching more than 20 files (Phase 1 inventory used this pattern), Writer/Reviewer audit (Phase 5), parallelizable verification work where the parent and subagent agree on success criteria.

### 9. Persistence

The session log is the only durable component per SAGE §4.10.

- **Session log location**: `~/.claude/projects/<encoded-cwd>/<session-uuid>.jsonl`. The encoded-cwd replaces `/` with `-`. Format is JSONL, one event per line.
- **Session log retention**: 90 days (Phase 2 Q11). The `Stop-prune-session-logs.py` hook deletes per-session JSONL files older than 90 days with a 24-hour marker guard at `~/.claude/.last-cleanup-90d`. Aggregate `~/.claude/history.jsonl` is exempt (rolling buffer).
- **Memory tools**: Phase 4 adopted MemPalace v3.3.2 alongside Claude Code's native auto-memory (Phase 2 Q4 enabled). Auto-memory carries free-form per-project memories; MemPalace carries structured drawers + wings + rooms + AAAK diaries + knowledge-graph triples for the workflows where auto-memory's free-form `.md` format does not fit.
- **Compaction interaction**: session log persists across compactions; harness state does not.

## Skills

Two skills live in `mac/harness/skills/`, written in Phase 4 to close foundation gaps the harness CLAUDE.md describes but does not operationalize:

- **`mcp-server-pre-trust-audit/`** — fires when a request mentions registering, adding, or installing an MCP server. Six-check audit: license, source review, network egress, version pin, secret handling, tool subset. Closes the gap above `~/.claude/mcp.json` that the SessionStart hook does not cover.
- **`seed-evaluation/`** — fires when a request proposes adopting any external tool, library, plugin, skill collection, agent definition, or hook library. Codifies the `foundation/03` two-stage methodology (pre-filter under 30 seconds + deep-eval through three real exercises). Replaces rubric scoring with binary integrate / integrate-with-constraints / reject decisions.

Adopted from the `superpowers@claude-plugins-official` plugin: 14 skills (brainstorming, dispatching-parallel-agents, executing-plans, finishing-a-development-branch, receiving-code-review, requesting-code-review, subagent-driven-development, systematic-debugging, test-driven-development, using-git-worktrees, using-superpowers, verification-before-completion, writing-plans, writing-skills) plus 1 SessionStart hook.

## Quality Contract operationalization

| QC | Mac implementation |
|---|---|
| QC.1 Security | Homebrew pins (post-launch operational step); SBOM via `syft` (deferred, post-launch); secret scan via `gitleaks` v8.30.0 wired in pre-commit 2026-05-11 (replaced `detect-secrets`); SAST via `semgrep` v1.162.0 installed via pipx and wired in pre-commit 2026-05-11 (the broken Anaconda install is shadowed by the pinned pre-commit-managed version, not removed); shell linting via `shellcheck` v0.11.0 wired in pre-commit. |
| QC.2 Tight code | Reviewer subagent in Phase 5 audits scope. No new abstractions, no new test scaffolding without explicit decision recorded in the phase output or commit message. |
| QC.3 Comments | Comment the why. Hook scripts and skill bodies carry rationale headers. |
| QC.4a Cache (API/SDK) | Direct API/SDK use carries explicit `"ttl": "1h"` on cache_control. Telemetry on. Documented in `mac/harness/settings.json`. |
| QC.4b Cache (Claude Code) | CLAUDE.md hierarchy under 400 lines total. Drift-check covers project hierarchy plus user-level `@import` chain (Q10 widening landed 2026-05-11). Currently FAILs at 1161 lines worst case until the Q3 `~/.claude/` rebuild trims the legacy SuperClaude framework chain. `<system-reminder>` blocks carry dynamic content. |
| QC.5 Versioning | Claude Code pinned to `v2.1.*` minor-version range (currently 2.1.138). Re-evaluation trigger: minor bump (v2.2.x). |

## Threat model adaptations for Mac

The threats in `foundation/01-threat-model.md` apply unchanged. Mac-specific notes:

- **macOS Gatekeeper and code signing**: assumed enabled. Disabled Gatekeeper is a host-OS misconfiguration the harness does not defend against.
- **FileVault disk encryption**: assumed enabled. The harness's secret-protection posture relies on the host disk being encrypted at rest.
- **Keychain**: used for credential storage where applicable. Phase 1 surfaced a HIGH-severity plaintext Hetzner Cloud API token in `~/.claude/mcp.json`; the env-var indirection (`HCLOUD_TOKEN=${env:HCLOUD_TOKEN}` backed by Keychain or 1Password CLI) is a post-Phase-5 operational step paired with the `~/.claude/` rebuild.
- **System Integrity Protection (SIP)**: assumed enabled.
- **Network egress monitoring**: not installed and not adopted. Phase 2 Q7 elected to skip; the permission layer + MCP allowlist + per-server review carry the egress defense.

## Build state

- Foundation documents: written and committed (Batch 1).
- Mac section structure: written and committed (Batch 2).
- Phase 0 (goals and architecture): complete 2026-05-11. Decisions recorded in `phase-outputs/PHASE-0-DECISIONS.md`.
- Phase 1 (discovery): complete 2026-05-11. Inventory in `phase-outputs/INVENTORY.md` (212 lines).
- Phase 2 (architecture interview): complete 2026-05-11. 12 answers in `phase-outputs/ANSWERS.md`.
- Phase 3 (deterministic layer): complete 2026-05-11. 6 hooks, 6 deny rules, populated `settings.json`, 5-candidate deep-eval.
- Phase 4 (extension layer): complete 2026-05-11. 2 skills, 2 agents, `enabledPlugins` calibrated minimum, 6-candidate deep-eval.
- Phase 5 (wire and document): complete 2026-05-11. Polished documentation, Reviewer audit pass.

Post-Phase-5 operational steps landed in their own commits: drift-check widening per Q10 (commit `920d5e7`); pre-commit rewire from `detect-secrets` to `gitleaks` plus `semgrep` clean install via pipx plus `shellcheck` install for direct verification (one combined commit; pre-commit git hooks installed at the same time).

Remaining post-Phase-5 operational steps: rebuild `~/.claude/` per Q3, bulk-acknowledge tool for the 44 in-repo `.claude/` directories Phase 1 surveyed, Hetzner Cloud token env-var indirection, audit the 13 daily-driver plugins for the rebuilt config.

## Version pins

Re-evaluated on every Claude Code minor-version bump.

| Component | Pinned version | Next-evaluation trigger |
|---|---|---|
| Claude Code | v2.1.* (currently 2.1.138) | Minor-version bump (v2.2.x) |
| macOS | 26.3 (25D125) | Major-version release (macOS 27) |
| Node | v24.10.0 | Node LTS major (v26 LTS) |
| Python | 3.13.9 | Python minor release (3.14 / 3.15) |
| Homebrew | 5.1.10 | Quarterly review (next: 2026-08-10) |
| gitleaks | 8.30.0 (binary + pre-commit hook) | Security advisory, or major release (v9) |
| trivy | 0.69.0 | Security advisory, or major release (v1.x) |
| semgrep | 1.162.0 (pipx; pre-commit hook pins the same version) | Security advisory, or major release (v2) |
| shellcheck | 0.11.0 (binary; pre-commit shellcheck-py wraps v0.10.0.1) | Security advisory, or major release (v1) |
| superpowers plugin | 5.1.0 | Plugin lastUpdated drift past 90 days, or upstream major (6.0.x) |
| MemPalace plugin | 3.3.2 | Security advisory, major release (4.0.x), or add_drawer content-corruption bug unfixed 90 days |
| Serena | deferred (user-disabled in current `~/.claude/settings.json`; revisit on specific use case) | Set when adopted |
| detect-secrets | removed 2026-05-11 (superseded by gitleaks in pre-commit) | Re-evaluation only if gitleaks coverage gap surfaces |
| cosai-oasis/project-codeguard | deferred (pre-1.0, not installed) | Codeguard 1.0 release, or agentcontrolstandard.ai ship |
