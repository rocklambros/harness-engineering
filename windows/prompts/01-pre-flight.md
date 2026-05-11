# 01 — Pre-flight (Windows)

<role>
You are preparing the Windows 11 build environment for the harness-engineering phase sequence. This prompt runs once before Phase 0. Your job is to verify the tools the phases assume, create the build-internal directory structure, and record the baseline state. You do not make architecture decisions here. You verify and record.
</role>

<effort>high</effort>

<mode>default (this prompt writes a small number of build-internal files)</mode>

<thinking>adaptive</thinking>

<context_budget>Run /context at start. Record the loaded tools, the active CLAUDE.md hierarchy line count, and the cache footprint in phase-outputs/PREFLIGHT.md. Run /context at end and record the delta.</context_budget>

<parallel_tool_calls>Prefer parallel reads when verifying tool versions or inspecting installed files. Version checks are independent.</parallel_tool_calls>

<scope>
Apply only to artifacts named in the deliverables list below. Do not modify any file outside `phase-outputs/`. Do not write to `windows/harness/`, `windows/prompts/`, `windows/evaluations/`, `windows/ARCHITECTURE.md`, or anywhere in `foundation/` or `research/`. Pre-flight is read-only with one exception: it creates `phase-outputs/` and writes `phase-outputs/PREFLIGHT.md`.
</scope>

## What to do

Verify the tools the phase sequence assumes are installed and reachable on Windows. Record the versions. Create the build-internal `phase-outputs/` directory. Write `phase-outputs/PREFLIGHT.md` with the baseline.

Tools to verify on Windows:

1. Claude Code: `claude --version`. Record the exact version string and confirm Windows x86_64 binary.
2. Git: `git --version`. Record. Confirm whether it ships with Git Bash (needed for the root drift-check.sh invocation).
3. PowerShell: `$PSVersionTable`. Record the version. Identify whether the active shell is 5.1 inbox or 7+.
4. winget: `winget --version`. Record.
5. Chocolatey or Scoop if installed: record presence and version. If not installed, do not flag as a gap; winget is the primary.
6. WSL2 availability: `wsl --status` and `wsl --list --verbose`. Record default distribution and kernel.
7. Node: `node --version`. Record.
8. Python: `python --version` and `py --version` if py launcher is installed. Record both.
9. Pre-commit framework: `pre-commit --version`. Record.
10. PSScriptAnalyzer: `Get-Module -ListAvailable PSScriptAnalyzer`. Record.
11. Shellcheck (only if WSL2 is in scope): `wsl -- shellcheck --version`. Record.
12. Markdownlint: `markdownlint-cli2 --version`. Record. If not installed, gap.
13. Detect-secrets: `detect-secrets --version`. Record. If not installed, gap.
14. Semgrep: `semgrep --version`. Record. Verify Windows-native build vs WSL2 invocation.
15. PowerShell execution policy: `Get-ExecutionPolicy -List`. Record per scope.
16. BitLocker status: `manage-bde -status` (requires elevation; if unavailable, note and skip).
17. Microsoft Defender state: `Get-MpComputerStatus` summary. Record.

Any tool reporting missing is recorded as a gap. Do not install missing tools. The Phase 2 architecture interview decides what to do about gaps.

Read the four files in `foundation/` and confirm readable and well-formed. Read the three documents in `research/` and confirm readable. Run the drift check from a bash environment (Git Bash, WSL2 bash, or equivalent): `bash scripts/drift-check.sh` against the current repo state and confirm exit code 0.

<investigate_before_answering>
Before claiming a tool is installed at a specific version, run the version command. Do not assume.

Before claiming a Windows x86_64 build is what's installed, verify by file inspection (e.g., `Get-ItemProperty` on the executable) or version output that names the architecture.

Before claiming WSL2 is available, confirm with `wsl --status`. WSL1 vs WSL2 has implications for hook routing.
</investigate_before_answering>

## Deliverables

One file:

**`phase-outputs/PREFLIGHT.md`**, containing:

- Section "Tools verified", listing each tool, its version (or "not installed"), and the architecture confirmation where ambiguity is possible.
- Section "PowerShell context", recording version, execution policy per scope, and any execution-context concerns.
- Section "WSL2 context", recording availability, kernel, default distribution, and any tools available only via WSL2 routing.
- Section "Foundation readable", confirming the five `foundation/` files present and readable.
- Section "Research readable", confirming the three `research/` files present and readable.
- Section "Drift check", recording exit code and output (note the bash environment used to invoke).
- Section "Context baseline", recording `/context` at start and end with delta.
- Section "Gaps", listing missing tools or files. Empty if none.
- Section "Windows-specific observations", capturing BitLocker state, Defender state, AppLocker presence, network egress monitor presence, and anything else that informs later phases.

## Verification

Before reporting complete:

- The PREFLIGHT.md file exists at the recorded path.
- Line count is substantive (typically 50-100 lines depending on output verbosity).
- The bash drift-check invocation returned 0.

Report the file path, line count, drift-check exit code. Do not summarize file contents in chat.

## Anti-overengineering

Pre-flight is verification, not configuration. Do not install tools. Do not modify hooks. Do not edit files outside `phase-outputs/`. Do not create test files, helper scripts, or additional documentation. If you find yourself wanting to do any of those things, stop and note the impulse under "Deferred to Phase 2."

Phase 0 runs after this one. Phase 2 architecture interview decides what to do about gaps. Pre-flight only verifies and records.
