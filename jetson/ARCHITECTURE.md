# Jetson harness architecture

The Jetson AGX Orin build of the harness. This document is the operational reference for how the nine harness components from `foundation/02-architectural-principles.md` land on ARM64 Linux running JetPack-based Ubuntu. Two kinds of unresolved blocks live here:

- `<TBD-PHASE-0>` blocks are filled by the Phase 0 session against the live environment, then re-evaluated on Claude Code minor-version bumps per QC.5.
- `<NEEDS-JETSON-PORT-VALIDATION>` blocks are assertions ported from the Mac-validated build that must be verified on Jetson before being treated as fact. The marker stays until the Phase 0 or Phase 3 session confirms the assertion holds on this platform.

The document follows the SAGE nine-component decomposition (§4) and operationalizes each Quality Contract property per `foundation/00-quality-contract.md` for this platform.

## Environment baseline

| Property | Value |
|---|---|
| Operating system | Ubuntu on ARM64 (JetPack-based) |
| Ubuntu version pin | `<TBD-PHASE-0>` |
| JetPack version | `<TBD-PHASE-0>` |
| Hardware | NVIDIA Jetson AGX Orin |
| GPU | NVIDIA Ampere, on-board (CUDA capable) |
| Shell | `<TBD-PHASE-0>` (typically bash on Ubuntu) |
| Package manager | apt (system), pip and pipx (Python), npm (Node) |
| Node version | `<TBD-PHASE-0>` |
| Python version | `<TBD-PHASE-0>` |
| Claude Code version pin | `<TBD-PHASE-0>` (minor-version range per QC.5; verify ARM64 Linux binary availability) |
| Working directory | `<TBD-PHASE-0>` |
| Daily-driver harness path | `<TBD-PHASE-0>` (in-repo vs symlinked to `~/.claude/`) |
| Disk encryption | `<TBD-PHASE-0>` (LUKS typical for Ubuntu installs) |

The version pins are recorded after Phase 0 verifies what is actually installed. ARM64 Linux availability of any pinned tool is verified as part of Phase 0; tools that lack an ARM64 build trigger a recorded gap in `phase-outputs/PHASE-0-DECISIONS.md`.

## The nine harness components on Jetson

### 1. Agent loop

Owned by Claude Code itself. Configured through model selection, effort level, and session mode.

- Default model: `<TBD-PHASE-0>` (Opus or Sonnet)
- Effort level: `xhigh` for build phases, `high` for routine work
- Session mode default: `default` permission mode
- Compaction posture: continuous, no manual resets unless a model-version change makes the heuristic stale
- Claude Code ARM64 Linux availability: `<NEEDS-JETSON-PORT-VALIDATION>` (verify the installed Claude Code binary supports ARM64 Linux at the pinned version; if a build is missing or behind, record the deferred decision)

### 2. Instruction layer

Three CLAUDE.md files participate in the cached prefix.

- Repository root `CLAUDE.md` (build-time, governs work on this repo)
- `jetson/harness/CLAUDE.md` (operational, governs daily Claude Code sessions on Jetson)
- `<TBD-PHASE-0>` if a third file participates

Combined line total stays under 400 per QC.4b. The drift check in `scripts/drift-check.sh` enforces the cap across all platforms.

### 3. Tool pool

Built-in tools, custom tools, MCP-exposed tools.

Default enabled built-ins: `<TBD-PHASE-0>` (record the active set after `/context` shows the loaded tools).

ARM64 Linux availability of conditionally enabled tools: `<NEEDS-JETSON-PORT-VALIDATION>` (the 35 conditional tools per Claude_Architecture.md §6.2 may have platform-specific availability; verify each conditional that the Mac build relied on).

Custom and MCP tools land in Phase 4.

### 4. Permission layer

The deny-first, ask-by-default permission system from Claude_Architecture.md §5 applies unchanged. Platform-specific deltas:

- Permission mode default: `default` per Principle 2
- Auto-mode classifier: `<TBD-PHASE-2>` (Phase 2 interview decides; same considerations as Mac)
- Deny rules: live in `jetson/harness/rules/` (Phase 3 populates; rule pattern syntax is platform-agnostic)
- Hook gates: live in `jetson/harness/hooks/` (Phase 3 populates; shell script semantics differ from Mac on a few edges, recorded inline)
- MCP server-prefix denies: `<TBD-PHASE-0>`

Hooks enforce. CLAUDE.md advises. Principle 1 holds across platforms.

### 5. Context pipeline

- Compaction: automatic
- System reminders: used for dynamic content per QC.4b
- File references: discovered in Phase 1, recorded in `phase-outputs/INVENTORY.md`
- Context resets: not used by default
- PreCompact / PostCompact hooks: `<TBD-PHASE-0>`

### 6. Sandbox

This is the largest known platform divergence from Mac.

- Bash sandboxing on ARM64 Linux: `<NEEDS-JETSON-PORT-VALIDATION>` (Claude Code v2.1.88's sandbox implementation on Mac uses macOS-native primitives. The Linux equivalent uses different mechanisms. Phase 0 verifies what's actually supported on the installed Claude Code version on ARM64 Linux and what the fallback posture looks like if sandboxing is not yet implemented for this platform-architecture pair.)
- Filesystem isolation: `<TBD-PHASE-0>`
- Network egress restrictions: `<TBD-PHASE-0>`
- AppArmor or SELinux integration: `<TBD-PHASE-0>` (whichever the JetPack base provides; not the harness's responsibility but informs the threat model)
- Exclusion patterns: `<TBD-PHASE-0>`

### 7. MCP integration

- MCP allowlist: managed in `jetson/harness/settings.json` (Phase 4 populates)
- Default posture: deny all MCP servers not on the allowlist
- Pre-trust audit habit: same as Mac. Every cloned repository's `.claude/settings.json` and `.mcp.json` reviewed before opening in Claude Code.
- ARM64 Linux availability per MCP server: `<NEEDS-JETSON-PORT-VALIDATION>` (each server adopted in Mac Phase 4 is verified to run on ARM64 Linux before adoption here. Server-side ARM64 support varies by maintainer.)

### 8. Subagent delegation

Same model as Mac. Task tool, worktree isolation, cost-vs-cache subagent model decisions.

- Worktree isolation: enabled
- Default subagent model: `<TBD-PHASE-0>`
- When to spawn: same heuristics as Mac

### 9. Persistence

- Session log location: `<TBD-PHASE-0>` (Claude Code on Linux writes to a path that may differ from Mac; Phase 0 records the actual path)
- Session log retention: `<TBD-PHASE-0>`
- Memory tools: `<NEEDS-JETSON-PORT-VALIDATION>` (MemPalace ARM64 Linux support is a Phase 4 deep-eval question)
- Compaction interaction: session log persists across compactions

## Quality Contract operationalization

| QC | Jetson implementation |
|---|---|
| QC.1 Security | apt pins via `apt-mark hold` or pinned `.deb` versions (`<TBD-PHASE-0>`). SBOM via `syft` (Phase 3 evaluates ARM64 Linux availability). Secret scan via `detect-secrets` (pre-commit, identical to Mac). SAST via `semgrep` (Phase 3 verifies ARM64 Linux build). |
| QC.2 Tight code | Reviewer subagent in Phase 5 audits scope. Same discipline as Mac. |
| QC.3 Comments | Comment the why. Hook scripts in `jetson/harness/hooks/` carry rationale comments. |
| QC.4a Cache (API/SDK) | Direct Anthropic API use carries explicit `"ttl": "1h"`. Same as Mac. Documented in `jetson/harness/settings.json.template`. |
| QC.4b Cache (Claude Code) | CLAUDE.md hierarchy under 400 lines total. `scripts/drift-check.sh` enforces across all platforms. |
| QC.5 Versioning | Claude Code pinned to `<TBD-PHASE-0>`. Re-evaluation trigger: minor bump. Same as Mac. |

## Threat model adaptations for Jetson

The threats in `foundation/01-threat-model.md` apply unchanged. Jetson-specific notes:

- **AppArmor or SELinux**: depends on the JetPack base. Linux MAC layers are not the harness's defense, but the harness expects whichever is configured to be active.
- **LUKS disk encryption**: assumed enabled. The harness's secret-protection posture relies on the host disk being encrypted at rest.
- **GNOME keyring or equivalent**: used for credential storage where applicable. The harness does not write secrets to plain files in the working directory.
- **No SIP equivalent**: Linux relies on standard DAC permissions and the optional MAC layer. Root access is structurally available; the discipline is to not use it for harness operations.
- **Network egress monitoring**: `opensnitch` is the Linux equivalent of Little Snitch and LuLu on Mac. `<TBD-PHASE-0>` (Phase 0 records whether one is installed).
- **CUDA and GPU access**: the Jetson's GPU is accessible to processes the harness invokes. Phase 3 decides whether hook scripts should constrain GPU access for any class of operation (typically not required for the harness's threat model, but the option exists).
- **JetPack-specific services**: the JetPack base ships with NVIDIA-specific services (nvargus-daemon, etc.). The harness does not interact with these. Phase 1 inventory records what's running so unexpected services are visible.

## Build state

- Foundation documents: written and committed (Batch 1)
- Jetson section structure: scaffolded (Batch 3)
- `<TBD-PHASE-0>` blocks: filled after first Phase 0 session on Jetson
- `<NEEDS-JETSON-PORT-VALIDATION>` blocks: resolved during Phase 0 verification and Phase 3 implementation
- Phase 1 through Phase 5: not yet executed on Jetson

Each phase output lands in `phase-outputs/` (build-internal, gitignored). Phase 5 produces the final polished form of this document, replacing every unresolved marker with the recorded value and adding the next-evaluation triggers below.

## Version pins

Filled by Phase 0. Re-evaluated on every Claude Code minor-version bump.

| Component | Pinned version | Next-evaluation trigger |
|---|---|---|
| Claude Code | `<TBD-PHASE-0>` | Minor-version bump |
| Ubuntu (JetPack base) | `<TBD-PHASE-0>` | Major-version release |
| JetPack | `<TBD-PHASE-0>` | Major-version release |
| Node | `<TBD-PHASE-0>` | LTS major release |
| Python | `<TBD-PHASE-0>` | Minor-version release |
| Semgrep | `<TBD-PHASE-0>` | Security advisory or major release |
| MemPalace | `<NEEDS-JETSON-PORT-VALIDATION>` | Major release if adopted |
| Serena | `<NEEDS-JETSON-PORT-VALIDATION>` | Major release if adopted |

Additional seeds adopted in Phase 3 or Phase 4 land in this table with their pin and trigger.
