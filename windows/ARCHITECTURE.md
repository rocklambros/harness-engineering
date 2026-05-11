# Windows harness architecture

The Windows build of the harness. This document is the operational reference for how the nine harness components from `foundation/02-architectural-principles.md` land on Windows 11 x86_64. Two kinds of unresolved blocks:

- `<TBD-PHASE-0>` blocks are filled by the Phase 0 session against the live environment.
- `<NEEDS-WINDOWS-PORT-VALIDATION>` blocks are assertions ported from the Mac-validated build that must be verified on Windows before being treated as fact.

The document follows the SAGE nine-component decomposition (§4) and operationalizes each Quality Contract property per `foundation/00-quality-contract.md` for this platform.

## Environment baseline

| Property | Value |
|---|---|
| Operating system | Windows 11 on x86_64 |
| Windows version pin | `<TBD-PHASE-0>` (record build number) |
| Hardware | `<TBD-PHASE-0>` (CPU, RAM, storage class) |
| Shell | `<TBD-PHASE-0>` (PowerShell 7+ preferred; PowerShell 5.1 inbox if present) |
| Package manager | winget (primary), Chocolatey or Scoop (secondary if installed) |
| WSL2 availability | `<TBD-PHASE-0>` (record WSL version, default distribution, kernel) |
| Node version | `<TBD-PHASE-0>` |
| Python version | `<TBD-PHASE-0>` |
| Claude Code version pin | `<TBD-PHASE-0>` (verify Windows x86_64 build at the pinned version) |
| Working directory | `<TBD-PHASE-0>` |
| Daily-driver harness path | `<TBD-PHASE-0>` (in-repo, symlinked to `%USERPROFILE%\.claude\`, or WSL2-resident) |
| BitLocker status | `<TBD-PHASE-0>` (manage-bde -status report) |
| Microsoft Defender state | `<TBD-PHASE-0>` |
| AppLocker / WDAC | `<TBD-PHASE-0>` (record whether configured) |

The version pins are recorded after Phase 0 verifies what is actually installed. Windows x86_64 availability of any pinned tool is verified as part of Phase 0; tools that lack a native Windows build are evaluated against WSL2 fallback per the Phase 2 architecture decision.

## The nine harness components on Windows

### 1. Agent loop

Owned by Claude Code itself. Configured through model selection, effort level, and session mode.

- Default model: `<TBD-PHASE-0>` (Opus or Sonnet)
- Effort level: `xhigh` for build phases, `high` for routine work
- Session mode default: `default` permission mode
- Compaction posture: continuous, no manual resets unless a model-version change makes the heuristic stale
- Claude Code Windows availability: `<NEEDS-WINDOWS-PORT-VALIDATION>` (verify the installed Claude Code supports native Windows at the pinned version, including its hook execution model. If Claude Code runs better under WSL2 on Windows than natively at this version, Phase 2 decides the placement)

### 2. Instruction layer

Three CLAUDE.md files participate in the cached prefix.

- Repository root `CLAUDE.md` (build-time, governs work on this repo)
- `windows/harness/CLAUDE.md` (operational, governs daily Claude Code sessions on Windows)
- `<TBD-PHASE-0>` if a third file participates

Combined line total stays under 400 per QC.4b. The drift check enforces the cap across all platforms. The CRLF-vs-LF concern matters here: `scripts/drift-check.sh` counts lines, not bytes, so line-ending choice does not change the count. The `.gitattributes` discipline (LF for cached-prefix files) keeps the diff clean.

### 3. Tool pool

Built-in tools, custom tools, MCP-exposed tools.

Default enabled built-ins: `<TBD-PHASE-0>` (record after `/context` shows the loaded tools on Windows).

Windows x86_64 availability of conditionally enabled tools: `<NEEDS-WINDOWS-PORT-VALIDATION>` (the 35 conditional tools per Claude_Architecture.md §6.2 may have platform-specific availability. Bash-tool variants, shell-sandbox primitives, and POSIX-path-dependent tools are the highest risk for Windows divergence).

Custom and MCP tools land in Phase 4.

### 4. Permission layer

The deny-first, ask-by-default permission system from Claude_Architecture.md §5 applies unchanged in concept. Platform-specific deltas in the patterns:

- Permission mode default: `default` per Principle 2
- Auto-mode classifier: `<TBD-PHASE-2>`
- Deny rules: live in `windows/harness/rules/` (Phase 3 populates; patterns adapt to Windows path conventions)
- Hook gates: live in `windows/harness/hooks/` (Phase 3 populates; hook script language is `<TBD-PHASE-2>`)
- MCP server-prefix denies: `<TBD-PHASE-0>`

Hooks enforce. CLAUDE.md advises. Principle 1 holds across platforms.

### 5. Context pipeline

- Compaction: automatic
- System reminders: used for dynamic content per QC.4b
- File references: discovered in Phase 1, recorded in `phase-outputs/INVENTORY.md`
- Context resets: not used by default
- PreCompact / PostCompact hooks: `<TBD-PHASE-0>`

### 6. Sandbox

The largest known platform divergence from Mac. Windows sandbox primitives differ fundamentally.

- Bash sandboxing on Windows: `<NEEDS-WINDOWS-PORT-VALIDATION>` (Claude Code v2.1.88's sandbox implementation on Mac uses macOS-native primitives. Windows-equivalent primitives include AppContainer, Windows Sandbox, and job objects. Phase 0 verifies what's actually supported on the installed Claude Code version on Windows and what the fallback posture looks like.)
- Filesystem isolation: `<TBD-PHASE-0>`
- Network egress restrictions: `<TBD-PHASE-0>`
- AppLocker or WDAC integration: `<TBD-PHASE-0>` (whether configured at all; not the harness's responsibility but informs the threat model)
- Windows Defender Application Control: `<TBD-PHASE-0>`
- Exclusion patterns: `<TBD-PHASE-0>`

### 7. MCP integration

- MCP allowlist: managed in `windows/harness/settings.json` (Phase 4 populates)
- Default posture: deny all MCP servers not on the allowlist
- Pre-trust audit habit: same as Mac and Jetson
- Windows x86_64 availability per MCP server: `<NEEDS-WINDOWS-PORT-VALIDATION>` (each server adopted in Mac Phase 4 is verified to run on Windows before adoption here. Server-side Windows support varies by maintainer; Go binaries usually portable, Python typically works, npm sometimes hits Windows-specific issues with native modules.)

### 8. Subagent delegation

Same model as Mac and Jetson. Task tool, worktree isolation, cost-vs-cache subagent model decisions.

- Worktree isolation: enabled
- Default subagent model: `<TBD-PHASE-0>`
- When to spawn: same heuristics as Mac

### 9. Persistence

- Session log location: `<TBD-PHASE-0>` (Claude Code on Windows writes to a path that differs from Mac and Linux; Phase 0 records the actual path)
- Session log retention: `<TBD-PHASE-0>`
- Memory tools: `<NEEDS-WINDOWS-PORT-VALIDATION>` (MemPalace Windows support is a Phase 4 deep-eval question)
- Compaction interaction: session log persists across compactions

## Quality Contract operationalization

| QC | Windows implementation |
|---|---|
| QC.1 Security | winget version pins (`<TBD-PHASE-0>`). SBOM via `syft` (Phase 3 evaluates Windows x86_64 availability). Secret scan via `detect-secrets` (pre-commit, identical to Mac and Jetson). SAST via `semgrep` (Phase 3 verifies Windows build; semgrep on Windows historically required WSL but recent versions ship native binaries). |
| QC.2 Tight code | Reviewer subagent in Phase 5 audits scope. Same discipline as Mac and Jetson. |
| QC.3 Comments | Comment the why. Hook scripts in `windows/harness/hooks/` carry rationale comments. |
| QC.4a Cache (API/SDK) | Direct Anthropic API use carries explicit `"ttl": "1h"`. Same as Mac and Jetson. Documented in `windows/harness/settings.json.template`. |
| QC.4b Cache (Claude Code) | CLAUDE.md hierarchy under 400 lines total. `scripts/drift-check.sh` enforces across all platforms. CRLF-vs-LF is a line-ending question, not a line-count question; the drift check is line-ending neutral. |
| QC.5 Versioning | Claude Code pinned to `<TBD-PHASE-0>`. Re-evaluation trigger: minor bump. Same as Mac and Jetson. |

## Threat model adaptations for Windows

The threats in `foundation/01-threat-model.md` apply unchanged. Windows-specific notes:

- **UAC and Microsoft Defender**: assumed enabled. Disabled UAC or Defender is a host-OS misconfiguration the harness does not defend against.
- **BitLocker disk encryption**: assumed enabled. The harness's secret-protection posture relies on the host disk being encrypted at rest.
- **Windows Credential Manager backed by DPAPI**: used for credential storage where applicable. The harness does not write secrets to plain files in the working directory.
- **AppLocker or WDAC**: if configured, provides a code-execution control layer the harness can rely on for additional defense. If not configured, the harness's deny rules and hook scripts carry the full weight.
- **Network egress monitoring**: GlassWire or simplewall is the Windows equivalent of Little Snitch and opensnitch. `<TBD-PHASE-0>` (Phase 0 records whether one is installed).
- **Smart App Control and SmartScreen**: assumed enabled on Windows 11. Provides file-execution and download reputation checks.
- **WSL2 as a permission boundary**: if Phase 2 elects to run the harness under WSL2, the WSL2 instance is a separate filesystem and process namespace. Threats inside WSL2 do not automatically cross into native Windows, but the WSL2 filesystem is accessible from native Windows by default. The boundary is real but porous; treat it accordingly.
- **PowerShell execution policy**: `<TBD-PHASE-0>` (record current policy; the harness expects at minimum `RemoteSigned` for hook scripts to execute without bypass flags).

## Build state

- Foundation documents: written and committed (Batch 1)
- Windows section structure: scaffolded (Batch 4)
- `<TBD-PHASE-0>` blocks: filled after first Phase 0 session on Windows
- `<NEEDS-WINDOWS-PORT-VALIDATION>` blocks: resolved during Phase 0 verification and Phase 3 implementation
- Phase 1 through Phase 5: not yet executed on Windows

Each phase output lands in `phase-outputs/` (build-internal, gitignored). Phase 5 produces the final polished form of this document.

## Version pins

Filled by Phase 0. Re-evaluated on every Claude Code minor-version bump.

| Component | Pinned version | Next-evaluation trigger |
|---|---|---|
| Claude Code | `<TBD-PHASE-0>` | Minor-version bump |
| Windows | `<TBD-PHASE-0>` | Feature update release |
| PowerShell | `<TBD-PHASE-0>` | Major-version release |
| WSL2 kernel | `<TBD-PHASE-0>` (if used) | Major-version release |
| Node | `<TBD-PHASE-0>` | LTS major release |
| Python | `<TBD-PHASE-0>` | Minor-version release |
| Semgrep | `<TBD-PHASE-0>` | Security advisory or major release |
| MemPalace | `<NEEDS-WINDOWS-PORT-VALIDATION>` | Major release if adopted |
| Serena | `<NEEDS-WINDOWS-PORT-VALIDATION>` | Major release if adopted |

Additional seeds adopted in Phase 3 or Phase 4 land in this table with their pin and trigger.
