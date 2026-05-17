# Jetson Harness Architecture

The Jetson AGX Orin harness mirrors the Mac architecture. Same five layers. Same three-layer security stack. Same Quality Contract bindings. Where tools or paths differ, the differences are called out explicitly in this document.

If you have not read `mac/ARCHITECTURE.md`, read it first. This document is a delta, not a standalone reference.

## System context

The Jetson harness runs Claude Code against the developer's filesystem on an NVIDIA Jetson AGX Orin developer kit. The OS is Ubuntu 22.04 LTS via JetPack 6.x. CPU architecture is ARM64 (aarch64) with Tegra extensions.

External dependencies are the same as Mac: the Anthropic API for Claude Code, package managers (apt, pip, npm) for tool installation, the GitHub API for repo interactions.

Hardware differences from Mac that matter to the harness:

ARM64 instead of Apple Silicon. Most tooling has aarch64 builds, but a few don't. Where prebuilt aarch64 binaries are missing, container alternatives are documented in `evaluations/`.

The Jetson is a single-user development machine in most setups but can be configured for multi-user. The harness assumes single-user; multi-user setup is out of scope per the Mac out-of-scope decision and applies equivalently here.

Memory pressure is real on Jetson. The AGX Orin has 64GB but heavy concurrent agentic workloads (Claude Code plus a local model plus a build) can swap. Phase 1 discovery surfaces the current state of memory and swap.

CUDA/cuDNN are present and may be used by the user's projects. The harness does not depend on them. Phase 1 inventories them for context.

## The five layers (Jetson variations)

### Layer 1: Project CLAUDE.md

Identical to Mac in shape. The status section pins to the Jetson-specific JetPack version (6.x) and the validated Claude Code minor-version range. The "operational" section notes that the working directory is `/home/jetson/` (or the equivalent user home on the Jetson), not `/Users/klambros/`.

Source: `harness/CLAUDE.md` (scaffolded; identical content to Mac with the path and platform notes adjusted).

### Layer 2: settings.json

Identical to Mac with three differences:

The hook script paths point to bash scripts in `harness/hooks/`. The bash interpreter location differs (`/usr/bin/bash` on Jetson vs. `/bin/bash` symlink on Mac). The scripts use `#!/usr/bin/env bash` so the symlink difference is transparent.

The `_validated_claude_code_range` field tracks the Jetson-specific validated range. May lag the Mac range if Claude Code releases don't immediately support aarch64.

The `permissions.deny` list adds Jetson-specific patterns: `Read(/etc/nvpmodel.conf)`, `Read(/proc/nvtegra/*)`, and similar Tegra-specific sensitive paths. These are not on Mac.

### Layer 3: Deterministic rules

Same rule files as Mac with Jetson-specific additions:

`paths.deny` includes Tegra-specific sensitive paths (`/etc/nvpmodel.conf`, `~/.nvidia-jetson/`).

`commands.deny` includes Jetson-specific dangerous commands (`nvpmodel -m 0` without user confirmation, `jetson_clocks` without rationale).

`secrets.patterns` is identical (the patterns are project-specific, not platform-specific).

### Layer 4: Skills

The `security-review` skill is byte-identical to Mac. The skill content does not vary by platform because the underlying anti-patterns do not vary by platform.

Other skills may emerge from Phase 4 discovery on Jetson (e.g., CUDA-specific guidance for projects that use it). These will be Jetson-only skills if they appear, and they will be added to this section when they do.

### Layer 5: Hooks and agents

The hook scripts are byte-identical to Mac. They use `bash` with `set -euo pipefail` semantics that work the same on both platforms.

One Jetson-specific consideration: the JetPack image's Python may be older than the Mac Homebrew Python. The pinned Semgrep version must be compatible with the JetPack Python. Phase 1 verifies this. If incompatible, the hook script can use a pyenv or virtualenv to invoke a compatible Semgrep; the choice is recorded during Phase 2.

The agents (`security-reviewer.md`, `writer-reviewer.md`) are identical to Mac.

## The three-layer security stack (Jetson)

Identical composition to Mac. Each layer lives in the same place:

Pre-generation guidance: `harness/skills/security-review/`. Content identical.

Commit-time hardening: `harness/hooks/post-tool-use-semgrep.sh`. Script identical. Semgrep binary on ARM64 has the same rule-pack coverage as on Apple Silicon (verified pre-build; needs hardware re-verification per Phase 3 validation).

Post-generation validation: `.pre-commit-config.yaml` at repo root. Same configuration. Pre-commit framework runs identically on Linux ARM64.

The methodology binding (SecureForge Appendix C, R.2.1) is identical. The taxonomy binding (sec-context, R.2.2) is identical. The Quality Contract binding (QC.1) is identical.

## Cross-platform tool equivalency for Jetson

| Capability | Tool on Jetson | Same as Mac? | Notes |
| --- | --- | --- | --- |
| SAST engine | semgrep (pip install on JetPack Python) | Same package, ARM64 build | Verify on hardware |
| Secret scanning | gitleaks (apt or download aarch64 binary) | Same tool, ARM64 build | Verify on hardware |
| Shell linting | shellcheck (apt install) | Same tool | Native aarch64 build available |
| JSON tooling | jq (apt install) | Same tool | Native aarch64 build available |
| Python runtime | JetPack Python 3.10+ | Different (Homebrew on Mac) | Pin Semgrep version compatible with both |
| Package manager | apt + pip | Different (Homebrew on Mac) | Document install commands per platform |
| Pre-commit framework | pre-commit (pip install) | Same | Identical config in `.pre-commit-config.yaml` |

## Build sequence on Jetson

Same six-phase sequence as Mac. Phase boundaries map to the same Quality Contract properties and threat IDs.

Phase 0, Phase 1, Phase 2 are fully ported and ready to run. Outputs land in `phase-outputs/` (same directory structure as Mac).

Phase 3, Phase 4, Phase 5 are scaffolded with "needs validation when ported" markers. The validation work involves:

Running each phase prompt against the actual Jetson hardware.

Verifying the deliverables produced match the Mac equivalents in structure and content.

Documenting any tool-availability or path differences in this `ARCHITECTURE.md` and the relevant phase prompt.

Updating the build status in `README.md` from "Scaffolded" to "Validated."

## What this architecture explicitly does not address

CUDA-specific anti-patterns in the security-review skill. If they exist (and they probably do; CUDA C is notoriously footgun-heavy), they would be added as Jetson-specific (and shared with other CUDA-capable platforms) pattern files. Out of scope for the initial scaffolded build.

Cross-compilation from Mac to Jetson. The harness assumes the developer is at the Jetson during development, not building Jetson artifacts on a different machine. Cross-development support is out of scope.

GPU memory and resource limits for the agent itself. Claude Code does not run inference locally on the Jetson; it talks to the Anthropic API. Local-inference variants would change this analysis.

These omissions are deliberate. They keep the Jetson section focused on the parity the harness actually needs.
