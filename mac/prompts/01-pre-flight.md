# 01 — Pre-flight

<role>
You are preparing the Mac build environment for the harness-engineering phase sequence. This prompt runs once before Phase 0. Your job is to verify the tools the phases assume, create the build-internal directory structure the phases write to, and record the baseline state Phase 0 amends from. You do not make architecture decisions here. You verify and record.
</role>

<effort>high</effort>

<mode>default (this prompt writes a small number of build-internal files; not enough to warrant plan mode)</mode>

<thinking>adaptive</thinking>

<context_budget>Run /context at start. Record the loaded tools, the active CLAUDE.md hierarchy line count, and the cache footprint in phase-outputs/PREFLIGHT.md. Run /context at end and record the delta.</context_budget>

<parallel_tool_calls>Prefer parallel reads when verifying tool versions or inspecting installed files. The version checks are independent.</parallel_tool_calls>

<scope>
Apply only to artifacts named in the deliverables list below. Do not modify any file outside `phase-outputs/`. Do not write to `mac/harness/`, `mac/prompts/`, `mac/evaluations/`, `mac/ARCHITECTURE.md`, or anywhere in `foundation/` or `research/`. The pre-flight is read-only with one exception: it creates `phase-outputs/` and writes `phase-outputs/PREFLIGHT.md`.
</scope>

## What to do

Verify the tools the phase sequence assumes are installed and reachable. Record the versions. Create the build-internal `phase-outputs/` directory. Write `phase-outputs/PREFLIGHT.md` with the baseline.

The tools to verify are:

1. Claude Code itself: `claude --version` (or equivalent). Record the exact version string.
2. Git: `git --version`. Record.
3. Homebrew: `brew --version`. Record.
4. Node: `node --version`. Record.
5. Python: `python3 --version`. Record.
6. Pre-commit framework: `pre-commit --version`. Record.
7. Shellcheck: `shellcheck --version`. Record.
8. Markdownlint: `markdownlint-cli2 --version`. Record. If not installed, note as a gap.
9. Detect-secrets: `detect-secrets --version`. Record. If not installed, note as a gap.
10. Semgrep: `semgrep --version`. Record.

Any tool reporting missing is recorded as a gap. Do not install missing tools. The Phase 2 architecture interview decides what to do about gaps.

Read the four files in `foundation/` and confirm they are readable and well-formed. Read the three documents in `research/` and confirm they are readable. Run `bash scripts/drift-check.sh` against the current repo state and confirm it returns exit code 0.

<investigate_before_answering>
Before claiming a tool is installed at a specific version, run the version command and capture its actual output. Do not assume.
</investigate_before_answering>

## Deliverables

One file:

**`phase-outputs/PREFLIGHT.md`**, containing:

- Section "Tools verified", listing each tool, its version (or "not installed"), and any path notes.
- Section "Foundation readable", confirming the five `foundation/` files are present and readable.
- Section "Research readable", confirming the three `research/` files are present and readable.
- Section "Drift check", recording the exit code and output of `bash scripts/drift-check.sh`.
- Section "Context baseline", recording the `/context` output at the start of this prompt run and at the end, with the delta.
- Section "Gaps", listing any tools or files that were missing. Empty section if none.

## Verification

Before reporting complete, run:

- `ls phase-outputs/PREFLIGHT.md` to confirm the file exists.
- `wc -l phase-outputs/PREFLIGHT.md` to confirm it has substantive content (typically 40-80 lines depending on output verbosity).
- `bash scripts/drift-check.sh` one more time to confirm the drift check still passes after the file was written.

Report the file path, its line count, and the drift-check exit code. Do not summarize the file's contents in chat; the file is the artifact.

## Anti-overengineering

The pre-flight is verification, not configuration. Do not install tools. Do not modify hooks. Do not edit any file outside `phase-outputs/`. Do not create test files, helper scripts, or additional documentation. If you find yourself wanting to do any of those things, stop and note the impulse in `phase-outputs/PREFLIGHT.md` under a "Deferred to Phase 2" subsection.

The Phase 0 prompt runs after this one. The Phase 2 architecture interview decides what to do about gaps. Pre-flight only verifies and records.
