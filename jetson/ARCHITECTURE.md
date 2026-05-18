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

Identical to Mac in shape. The status section pins to the Jetson-specific JetPack version (R36 release 5.0) and the validated Claude Code minor-version range (v2.1.x). The "operational" section notes that the working directory is `$HOME/github_projects/harness-engineering/` (the user's home directory on the Jetson), not `/Users/klambros/`.

Source: `harness/CLAUDE.md` (scaffolded; identical content to Mac with the path and platform notes adjusted).

### Layer 2: settings.json

Identical to Mac with three differences:

The hook script paths point to bash scripts in `harness/hooks/`. The bash interpreter location differs (`/usr/bin/bash` on Jetson vs. `/bin/bash` symlink on Mac). The scripts use `#!/usr/bin/env bash` so the symlink difference is transparent.

The `_validated_claude_code_range` field tracks the Jetson-specific validated range. May lag the Mac range if Claude Code releases don't immediately support aarch64.

The `permissions.deny` list adds Jetson-specific patterns for Tegra-specific sensitive paths (`/proc/nvtegra/*`, `~/.nvidia-jetson/`). These are not on Mac.

### Layer 3: Deterministic rules

Same rule files as Mac with Jetson-specific additions:

`paths.deny` includes Tegra-specific sensitive paths (`/etc/nvpmodel.conf`, `~/.nvidia-jetson/`).

`commands.deny` includes Jetson-specific rules: read-only queries (`nvpmodel -q`, `jetson_clocks --show`) are allowed, state-changing invocations (`nvpmodel -m`, bare `jetson_clocks`) are blocked. Decision recorded in Phase 2 (A.4).

`secrets.patterns` is identical (the patterns are project-specific, not platform-specific).

### Layer 4: Skills

The `security-review` skill is byte-identical to Mac. The skill content does not vary by platform because the underlying anti-patterns do not vary by platform.

Other skills may emerge from Phase 4 discovery on Jetson (e.g., CUDA-specific guidance for projects that use it). These will be Jetson-only skills if they appear, and they will be added to this section when they do.

### Layer 5: Hooks and agents

The hook scripts are byte-identical to Mac. They use `bash` with `set -euo pipefail` semantics that work the same on both platforms.

Python environment on this Jetson: Anaconda Python 3.12.2 is the default `python3` on PATH, system JetPack Python is 3.10.12 at `/usr/bin/python3.10`. Semgrep 1.163.0 is installed in both environments (Phase 2, A.1). Hook scripts invoke `semgrep` via PATH, which resolves to the conda base environment. Python hooks (`PreToolUse-*.py`) run under conda Python 3.12.

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
| SAST engine | semgrep 1.163.0 (pip, both conda and system Python) | Same package, ARM64 build | Phase 2 A.1 |
| Secret scanning | gitleaks v8.21.2 (binary at /usr/local/bin/) | Same tool, ARM64 build | Phase 2 A.2 |
| Shell linting | shellcheck 0.8.0 (apt) + 0.10.0 (pre-commit managed) | Same tool, version gap documented | Phase 2 A.3 |
| JSON tooling | jq 1.6 (apt) | Same tool | Installed |
| Python runtime | Anaconda 3.12.2 (default) + system 3.10.12 | Different (Homebrew on Mac) | Phase 2 A.1 |
| Package manager | apt + pip + conda | Different (Homebrew on Mac) | Phase 2 A.1/A.2/A.3 |
| Pre-commit framework | pre-commit (pip into conda base) | Same | Phase 2 A.1 |

## Build sequence on Jetson

Same six-phase sequence as Mac. Phase boundaries map to the same Quality Contract properties and threat IDs.

All six phases are complete and validated on this Jetson (May 18, 2026). Outputs in `phase-outputs/`. Phase 2 decisions are recorded in `phase-outputs/ANSWERS.md`. Phase 3 through Phase 5 validation documents record all hardware-specific findings and platform divergences.

## What this architecture explicitly does not address

CUDA-specific anti-patterns in the security-review skill. If they exist (and they probably do; CUDA C is notoriously footgun-heavy), they would be added as Jetson-specific (and shared with other CUDA-capable platforms) pattern files. Out of scope for the initial scaffolded build.

Cross-compilation from Mac to Jetson. The harness assumes the developer is at the Jetson during development, not building Jetson artifacts on a different machine. Cross-development support is out of scope.

GPU memory and resource limits for the agent itself. Claude Code does not run inference locally on the Jetson; it talks to the Anthropic API. Local-inference variants would change this analysis.

These omissions are deliberate. They keep the Jetson section focused on the parity the harness actually needs.
