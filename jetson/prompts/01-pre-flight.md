# 01 — Pre-flight (Jetson)

<role>
You are preparing the Jetson AGX Orin build environment for the harness-engineering phase sequence. This prompt runs once before Phase 0. Your job is to verify the tools the phases assume, create the build-internal directory structure, and record the baseline state. You do not make architecture decisions here. You verify and record.
</role>

<effort>high</effort>

<mode>default (this prompt writes a small number of build-internal files)</mode>

<thinking>adaptive</thinking>

<context_budget>Run /context at start. Record the loaded tools, the active CLAUDE.md hierarchy line count, and the cache footprint in phase-outputs/PREFLIGHT.md. Run /context at end and record the delta.</context_budget>

<parallel_tool_calls>Prefer parallel reads when verifying tool versions or inspecting installed files. Version checks are independent.</parallel_tool_calls>

<scope>
Apply only to artifacts named in the deliverables list below. Do not modify any file outside `phase-outputs/`. Do not write to `jetson/harness/`, `jetson/prompts/`, `jetson/evaluations/`, `jetson/ARCHITECTURE.md`, or anywhere in `foundation/` or `research/`. Pre-flight is read-only with one exception: it creates `phase-outputs/` and writes `phase-outputs/PREFLIGHT.md`.
</scope>

## What to do

Verify the tools the phase sequence assumes are installed and reachable on Jetson. Record the versions. Create the build-internal `phase-outputs/` directory. Write `phase-outputs/PREFLIGHT.md` with the baseline.

Tools to verify on Jetson:

1. Claude Code: `claude --version`. Record the exact version string and confirm ARM64 Linux binary availability.
2. Git: `git --version`. Record.
3. APT and package status: `dpkg --version` and a sample of harness-relevant packages (`dpkg -l | grep -E 'python3|nodejs|build-essential'`).
4. Node: `node --version`. Record.
5. Python: `python3 --version`. Record.
6. JetPack version: `cat /etc/nv_tegra_release` or equivalent. Record. JetPack-specific stack identification matters for the architecture document.
7. Pre-commit framework: `pre-commit --version`. Record.
8. Shellcheck: `shellcheck --version`. Record.
9. Markdownlint: `markdownlint-cli2 --version`. Record. If not installed, gap.
10. Detect-secrets: `detect-secrets --version`. Record. If not installed, gap.
11. Semgrep: `semgrep --version`. Record. Verify the install is the ARM64 Linux build.

Any tool reporting missing is recorded as a gap. Do not install missing tools. The Phase 2 architecture interview decides what to do about gaps.

Read the four files in `foundation/` and confirm readable and well-formed. Read the three documents in `research/` and confirm readable. Run `bash scripts/drift-check.sh` against the current repo state and confirm exit code 0.

<investigate_before_answering>
Before claiming a tool is installed at a specific version, run the version command. Do not assume.

Before claiming an ARM64 Linux build is what's installed, verify with `file $(which <tool>)` or `<tool> --version` output that names the architecture.
</investigate_before_answering>

## Deliverables

One file:

**`phase-outputs/PREFLIGHT.md`**, containing:

- Section "Tools verified", listing each tool, its version (or "not installed"), and the architecture confirmation where ambiguity is possible.
- Section "Foundation readable", confirming the five `foundation/` files are present and readable.
- Section "Research readable", confirming the three `research/` files are present and readable.
- Section "Drift check", recording exit code and output.
- Section "Context baseline", recording `/context` output at start and end with the delta.
- Section "Gaps", listing any tools or files missing. Empty if none.
- Section "Jetson-specific observations", capturing anything about the JetPack base, the GPU state, or the network egress configuration that informs later phases.

## Verification

Before reporting complete:

- `ls phase-outputs/PREFLIGHT.md` confirms the file exists.
- `wc -l phase-outputs/PREFLIGHT.md` confirms substantive content (40-90 lines).
- `bash scripts/drift-check.sh` returns 0.

Report the file path, line count, and drift-check exit code. Do not summarize the file's contents in chat.

## Anti-overengineering

Pre-flight is verification, not configuration. Do not install tools. Do not modify hooks. Do not edit any file outside `phase-outputs/`. Do not create test files, helper scripts, or additional documentation. If you find yourself wanting to do any of those things, stop and note the impulse under "Deferred to Phase 2."

Phase 0 runs after this one. Phase 2 architecture interview decides what to do about gaps. Pre-flight only verifies and records.
