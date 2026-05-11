# Jetson section

The Jetson AGX Orin build of the harness. ARM64 Linux on NVIDIA Jetson, running JetPack-based Ubuntu. Claude Code running from the working directory recorded in `ARCHITECTURE.md`.

This section is scaffolded, not validated. Foundation, Phase 0, Phase 1, and Phase 2 prompts are written and ready to run. Phase 3, Phase 4, and Phase 5 prompts are scaffolded with `<NEEDS-JETSON-PORT-VALIDATION>` markers where Jetson-specific behavior must be confirmed before any Mac-validated pattern is treated as portable. When Rock executes the Jetson build, validation findings replace the markers and the section graduates from scaffolded to validated.

The structural decision is deliberate. Capabilities are identical across the three platforms per locked decision 3 in `CHECKPOINT.md`. Equivalence is asserted on validated grounds for Mac and on documented expectations for Jetson and Windows. The expectations are tracked in writing so the gap between scaffolded and validated is auditable.

## What's in here

`ARCHITECTURE.md` documents the Jetson harness target. Filled draft with two kinds of unresolved blocks: `<TBD-PHASE-0>` for platform-specific values Phase 0 records when the build runs, and `<NEEDS-JETSON-PORT-VALIDATION>` for assertions ported from the Mac validation that must be verified on Jetson before being treated as fact.

`prompts/` holds the seven phase prompts. Phase 0 through Phase 2 carry the same standard header, scope discipline, and verification rigor as Mac. Phase 3 through Phase 5 carry scaffold-grade content: the structure is right, the deliverables are named, the verification commands work, but the Jetson-specific details (which sandbox mechanism Claude Code v2.1.x supports on ARM64 Linux, which SAST tools are available, which MCP servers run cleanly under JetPack) need validation when Rock ports the build.

`harness/` holds the operational artifacts. `harness/CLAUDE.md` is the daily-driver instruction file for Jetson sessions. `harness/settings.json.template` is the structural skeleton; Phase 0 and Phase 3 fill platform-specific values.

`evaluations/` holds the seed evaluation worksheets. The pre-filter table is pre-populated with the same candidate set as Mac. The architecture-support column changes per candidate based on ARM64 Linux availability.

`scripts/` is reserved for Jetson-platform-specific scripts that come out of Phase 3 or Phase 5.

## What's different from Mac

The harness's nine components and the Quality Contract apply unchanged. The platform-specific deltas land in `ARCHITECTURE.md`. Summary:

- Operating system: Ubuntu on ARM64 (JetPack-based), not macOS on Apple Silicon. Different shell defaults, different package manager (apt rather than Homebrew), different credential store (GNOME keyring or equivalent rather than Keychain), different sandbox primitives (AppArmor or SELinux, depending on distribution, rather than macOS sandbox-exec).
- Hardware acceleration: the Jetson has CUDA-capable GPU on-board. The harness does not depend on this, but local inference is an option in Phase 4 that Mac does not have at the same scale.
- Network egress monitoring: `opensnitch` on Linux is the equivalent of Little Snitch on Mac.
- Disk encryption: LUKS, not FileVault.
- System integrity: relies on Linux DAC and optional MAC layers; no SIP equivalent.

The threat model in `foundation/01-threat-model.md` is platform-agnostic. The mitigations in `harness/hooks/` and `harness/rules/` are platform-specific in their commands but identical in their intent.

## How to use this section

If you are reading this repo as a reference for building your own harness on Jetson or another ARM64 Linux target, the path is the same as the Mac section: foundation first, then this section's `ARCHITECTURE.md`, then the seven prompts in order. The `<NEEDS-JETSON-PORT-VALIDATION>` markers are honest signals about which assertions have not yet been confirmed on this platform. Treat them as live questions, not as finished documentation.

If you are running these prompts against your own Jetson, the Phase 0 prompt is the entry point. Run it first. Replace the `<TBD-PHASE-0>` blocks with the actual environment baseline. Then Phase 1 inventories your machine, Phase 2 makes the architecture decisions, and Phase 3 onward delivers the harness components with full validation. The build sequence is identical to Mac; the inputs and outputs are Jetson-specific.

## Status

Scaffolded. Phase 0 through Phase 2 ready to execute. Phase 3 through Phase 5 carry validation markers that resolve when the build runs on the actual hardware.

Build date: pending. The first execution of Phase 0 against a live Jetson stamps the section with the date and the validation results.
