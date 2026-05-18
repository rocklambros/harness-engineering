# Jetson section

The Jetson AGX Orin build of the harness. ARM64 Linux on NVIDIA Jetson, running JetPack R36 (release 5.0) on Ubuntu 22.04.5 LTS. Claude Code running from the working directory recorded in `ARCHITECTURE.md`.

This section is validated. All six phases have been executed on Jetson AGX Orin hardware. The build reproduces the Mac reference harness with four documented platform divergences in the hook scripts. All enforcement surfaces pass end-to-end integration testing.

The structural decision is deliberate. Capabilities are identical across the three platforms per locked decision 3 in `CHECKPOINT.md`. Equivalence is asserted on validated grounds for both Mac and Jetson. Windows remains scaffolded pending hardware validation.

## Build status

| Phase | Status | Validation date |
| --- | --- | --- |
| Phase 0: Goals | Validated | May 18, 2026 |
| Phase 1: Discovery | Validated | May 18, 2026 |
| Phase 2: Architecture | Validated | May 18, 2026 |
| Phase 3: Deterministic layer | Validated | May 18, 2026 |
| Phase 4: Extension layer | Validated | May 18, 2026 |
| Phase 5: Wire and document | Validated | May 18, 2026 |

## Guides

[`USER_GUIDE.md`](USER_GUIDE.md) is the quickstart and daily-use guide. Start here if you want to adopt the harness on your own Jetson project.

[`HARNESS_GUIDE.md`](HARNESS_GUIDE.md) is the technical reference. Covers the five layers, the three-layer security stack, hook event coverage, and Jetson-specific considerations.

## What's in here

`ARCHITECTURE.md` documents the Jetson harness design. Platform-specific values were filled during Phase 0 and Phase 2. All validation markers have been resolved.

`prompts/` holds the seven phase prompts that produced this build. Each is a self-contained Claude Code instruction referencing the foundation docs and the Jetson `ARCHITECTURE.md`.

`harness/` holds the operational artifacts. `harness/CLAUDE.md` is the daily-driver instruction file for Jetson sessions. `harness/settings.json.template` is the Claude Code configuration with Jetson-specific deny entries. `harness/hooks/` contains four bash hooks and seven Python hooks. `harness/skills/security-review/` is fully populated with ten pattern files. `harness/agents/` has four agent definitions.

`scripts/` holds the install script (`install-harness-tools.sh`), the integration test (`integration-test.sh`), and the drift check (`drift-check.sh`).

`phase-outputs/` holds the validation documents from each phase.

`evaluations/` holds the seed evaluation worksheets.

## What's different from Mac

The harness components and the Quality Contract apply unchanged. The platform-specific deltas are documented in `ARCHITECTURE.md` and in the `HARNESS_GUIDE.md` divergence table. Summary:

Operating system: Ubuntu 22.04 on ARM64 (JetPack R36), not macOS on Apple Silicon. Different package manager (apt rather than Homebrew), different credential store, different sandbox primitives.

Hardware acceleration: the Jetson has a CUDA-capable GPU on-board. The harness does not depend on CUDA, but Semgrep scans `.cu` and `.cuh` files.

Four hook scripts have platform-specific changes (GNU stat syntax, awk version parsing fix, apt error messages, CUDA extension support). Seven Python hooks are byte-identical to Mac.

## How to use this section

If you are reading this repo as a reference for building your own harness on Jetson or another ARM64 Linux target, start with the `USER_GUIDE.md` for adoption or `HARNESS_GUIDE.md` for the technical reference. The foundation docs in `foundation/` provide the design rationale.

If you want to reproduce the build from scratch, run the phase prompts in `prompts/` in order, starting with Phase 0.
