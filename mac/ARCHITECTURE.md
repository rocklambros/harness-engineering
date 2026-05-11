# Mac harness architecture

The Mac build of the harness. This document is the operational reference for how the nine harness components from `foundation/02-architectural-principles.md` land on macOS Apple Silicon. Blocks marked `<TBD-PHASE-0>` are filled by the Phase 0 session against the live environment and re-evaluated on Claude Code minor-version bumps per QC.5.

The document follows the SAGE nine-component decomposition (§4) and operationalizes each Quality Contract property per `foundation/00-quality-contract.md` for this platform.

## Environment baseline

| Property | Value |
|---|---|
| Operating system | macOS on Apple Silicon (ARM64) |
| macOS version pin | `<TBD-PHASE-0>` |
| Hardware | M-series Apple Silicon |
| Shell | zsh (default on modern macOS) |
| Package manager | Homebrew |
| Node version | `<TBD-PHASE-0>` |
| Python version | `<TBD-PHASE-0>` |
| Claude Code version pin | `<TBD-PHASE-0>` (minor-version range per QC.5) |
| Working directory | `/Users/klambros/harness-engineering/` |
| Daily-driver harness path | `<TBD-PHASE-0>` (in-repo vs symlinked to `~/.claude/`) |

The version pins are not aspirational. They are recorded after Phase 0 verifies what is actually installed, and they drive the next-evaluation triggers in the §Version pins section below.

## The nine harness components on Mac

### 1. Agent loop

Owned by Claude Code itself. The harness configures it through model selection, effort level, and session mode.

- Default model: `<TBD-PHASE-0>` (Phase 0 picks Opus or Sonnet based on workload mix)
- Effort level: `xhigh` for build phases, `high` for routine work
- Session mode default: `default` permission mode
- Compaction posture: continuous, no manual resets unless a model-version change makes the heuristic stale (SAGE §5.1 recommendation 5; Rajasekaran's retrospective documents that context resets necessary on Opus 4.5 became unnecessary on 4.6)

### 2. Instruction layer

Three CLAUDE.md files participate in the cached prefix.

- `/Users/klambros/harness-engineering/CLAUDE.md` (build-time, governs work on this repo)
- `mac/harness/CLAUDE.md` (operational, governs daily Claude Code sessions)
- `<TBD-PHASE-0>` if a third file participates (e.g., `~/.claude/CLAUDE.md` if Rock symlinks)

Combined line total stays under 400 per QC.4b. The drift check in `scripts/drift-check.sh` enforces the cap. The current build-time file is 91 lines; the operational file is sized in Phase 3 and Phase 4 as features land.

### 3. Tool pool

Built-in tools enabled by default, custom tools, MCP-exposed tools. Assembled by the Claude Code runtime at session start.

Default enabled built-ins: `<TBD-PHASE-0>` (Phase 0 records the active set after `/context` shows the loaded tools).

Custom and MCP tools land in Phase 4. Each is filtered by deny rules (Phase 3 deliverable) and mode (per-session).

Per Claude_Architecture.md §6.2, the `getAllBaseTools()` enumeration returns up to 54 tools, with 19 always included and 35 conditionally based on feature flags. The default subset Phase 0 inherits from Claude Code is the starting position; the harness narrows from there.

### 4. Permission layer

The deny-first, ask-by-default permission system from Claude_Architecture.md §5 lands here.

- Permission mode default: `default` (interactive approval with deny-rule pre-filtering). Least privilege per Principle 2.
- Auto-mode classifier: `<TBD-PHASE-0>` (Phase 2 interview decides whether to enable; Hughes 2026 reports 0.4% false-positive rate)
- Deny rules: live in `mac/harness/rules/` (Phase 3 populates)
- Hook gates: live in `mac/harness/hooks/` (Phase 3 populates)
- MCP server-prefix denies: `<TBD-PHASE-0>` (Phase 4 records which servers are allowlisted)

Hooks enforce. CLAUDE.md advises. Every rule that must hold every time lives in a hook script, not in an advisory instruction. This is the load-bearing decision from `foundation/02-architectural-principles.md` Principle 1.

### 5. Context pipeline

- Compaction: automatic (Claude Code's built-in five-layer compaction per Claude_Architecture.md §7)
- System reminders: used for any dynamic content that would otherwise pollute the cached prefix, per QC.4b
- File references: discovered in Phase 1, recorded in `phase-outputs/INVENTORY.md`
- Context resets: not used by default (per SAGE §5.1 recommendation 5)
- PreCompact / PostCompact hooks: `<TBD-PHASE-0>` (Phase 3 decides whether to register)

### 6. Sandbox

Independent of the permission layer. Operates on filesystem and network isolation axes per Claude_Architecture.md §5.4.

- Bash sandboxing: `<TBD-PHASE-0>` (Phase 0 enables and verifies on Mac)
- Filesystem isolation: `<TBD-PHASE-0>` (which directories are write-protected at the sandbox level)
- Network egress restrictions: `<TBD-PHASE-0>` (curl/network calls require explicit approval)
- Exclusion patterns for sandbox opt-out: `<TBD-PHASE-0>` (Phase 3 records any)

### 7. MCP integration

Each MCP server is a permission grant. Allowlisting and pre-trust audit are the discipline.

- MCP allowlist: managed in `mac/harness/settings.json` (Phase 4 populates)
- Default posture: deny all MCP servers not on the allowlist
- Pre-trust audit habit: every cloned repository's `.claude/settings.json` and `.mcp.json` get reviewed before opening the project in Claude Code. Defense against the CVE-2025-59536 / CVE-2026-21852 class (pre-trust initialization execution).
- Network egress per MCP server: `<TBD-PHASE-0>` (Phase 4 records per-server constraints)

### 8. Subagent delegation

The Task tool and worktree isolation. Subagent model selection has cost and cache-economy consequences per QC.4a.

- Worktree isolation: enabled
- Default subagent model: `<TBD-PHASE-0>` (Phase 0 picks; Opus subagents cost more but share cache with parent if also Opus; Haiku subagents cost less but break Opus cache lineage)
- When to spawn a subagent: file-scan tasks touching more than 20 files, verification work the main session would benefit from running in parallel, and the Phase 5 Reviewer pattern. Phase 2 interview refines the policy.

### 9. Persistence

The session log is the only durable component per SAGE §4.10.

- Session log location: `<TBD-PHASE-0>` (Phase 0 records the path Claude Code writes to on this platform)
- Session log retention: `<TBD-PHASE-0>`
- Memory tools: MemPalace is installed and evaluates in Phase 4 against alternatives; not auto-adopted
- Compaction interaction: session log persists across compactions; harness state does not

## Quality Contract operationalization

| QC | Mac implementation |
|---|---|
| QC.1 Security | Homebrew pins via `Brewfile.lock` (`<TBD-PHASE-0>`); SBOM via `syft` (Phase 3 evaluates); secret scan via `detect-secrets` (pre-commit, wired in Batch 1); SAST via `semgrep` (already installed, Phase 3 deep-evaluates) |
| QC.2 Tight code | Reviewer subagent in Phase 5 audits scope. No new abstractions, no new test scaffolding without explicit decision. |
| QC.3 Comments | Comment the why. Hook scripts in `mac/harness/hooks/` carry rationale comments on each deny pattern. |
| QC.4a Cache (API/SDK) | Direct Anthropic API use carries explicit `"ttl": "1h"` on cache_control. Telemetry on. Documented in `mac/harness/settings.json.template`. |
| QC.4b Cache (Claude Code) | CLAUDE.md hierarchy under 400 lines total. `scripts/drift-check.sh` enforces. `<system-reminder>` blocks carry dynamic content. |
| QC.5 Versioning | Claude Code pinned to `<TBD-PHASE-0>` minor-version range. Re-evaluation trigger: minor bump. |

## Threat model adaptations for Mac

The threats in `foundation/01-threat-model.md` apply unchanged. Mac-specific notes:

- **macOS Gatekeeper and code signing**: assumed enabled. Disabled Gatekeeper is a host-OS misconfiguration that the harness does not defend against.
- **FileVault disk encryption**: assumed enabled. The harness's secret-protection posture relies on the host disk being encrypted at rest.
- **Keychain**: used for credential storage where applicable. The harness does not write secrets to plain files in the working directory.
- **System Integrity Protection (SIP)**: assumed enabled. SIP is not the harness's defense layer, but the harness expects it to be active.
- **Network egress monitoring**: Little Snitch, LuLu, or equivalent is `<TBD-PHASE-0>` (Phase 0 records whether one is installed). Not required by the harness, but the discipline of reviewing MCP egress in real time is easier with one.

## Build state

- Foundation documents: written and committed (Batch 1)
- Mac section structure: written and committed (Batch 2)
- `<TBD-PHASE-0>` blocks in this document: filled after first Phase 0 session
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
| Claude Code | `<TBD-PHASE-0>` | Minor-version bump |
| macOS | `<TBD-PHASE-0>` | Major-version release |
| Node | `<TBD-PHASE-0>` | LTS major release |
| Python | `<TBD-PHASE-0>` | Minor-version release |
| Homebrew | `<TBD-PHASE-0>` | Quarterly review |
| Semgrep | `<TBD-PHASE-0>` | Security advisory or major release |
| MemPalace | `<TBD-PHASE-0>` | Major release |
| Serena | `<TBD-PHASE-0>` | Major release |

Additional seeds adopted in Phase 3 or Phase 4 land in this table with their pin and trigger.
