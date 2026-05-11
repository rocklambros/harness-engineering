# Phase 0 — Goals and Architecture (Windows)

<role>
You are setting the goals for the Windows harness build and filling the platform-specific blocks in `windows/ARCHITECTURE.md`. Phase 0 records the version pins, the model and effort defaults, the sandbox posture, the persistence configuration, the WSL2 status, and the next-evaluation triggers. You make calibrated decisions and document the rationale. You do not write hooks, deny rules, skills, or agents here. Those are Phase 3 and Phase 4 deliverables.

The Windows document carries two kinds of unresolved blocks: `<TBD-PHASE-0>` (Phase 0 owns) and `<NEEDS-WINDOWS-PORT-VALIDATION>` (Phase 0 verifies any the live environment can confirm; the rest stay for Phase 3 implementation).
</role>

<effort>xhigh</effort>

<mode>plan mode at start. Switch to default mode only to write the updated `windows/ARCHITECTURE.md`. No other files change in Phase 0.</mode>

<thinking>adaptive</thinking>

<context_budget>Run /context at start and end. Phase 0 reads several foundation documents and the architecture reference. Record state in `phase-outputs/PHASE-0-CONTEXT.md`.</context_budget>

<parallel_tool_calls>
Read foundation documents in parallel: `foundation/00-quality-contract.md`, `foundation/01-threat-model.md`, `foundation/02-architectural-principles.md`, `foundation/03-seed-evaluation-methodology.md`, `foundation/04-research-references.md`. Read `windows/README.md`, `windows/ARCHITECTURE.md`, `windows/harness/CLAUDE.md`, and `windows/harness/settings.json.template` in parallel.
</parallel_tool_calls>

<scope>
Apply only to:
- `windows/ARCHITECTURE.md` (writes: fills `<TBD-PHASE-0>` blocks; resolves `<NEEDS-WINDOWS-PORT-VALIDATION>` blocks the live environment can confirm)
- `phase-outputs/PHASE-0-CONTEXT.md` (writes)
- `phase-outputs/PHASE-0-DECISIONS.md` (writes: the rationale log)

Do not modify any file in `foundation/`, `research/`, `windows/prompts/`, `windows/harness/` (except as scoped), `windows/evaluations/`, or `windows/scripts/`. Do not create hooks, skills, agents, or deny rules. Do not pre-write Phase 1 inventory content.
</scope>

## What to do

Read the foundation documents and `windows/ARCHITECTURE.md`. For each `<TBD-PHASE-0>` block, decide the value or leave it explicitly deferred. For each `<NEEDS-WINDOWS-PORT-VALIDATION>` block, verify against the live Windows environment and either confirm (replacing the marker with the confirmed fact) or document the gap (replacing the marker with a more specific deferred note for Phase 3).

The blocks Phase 0 fills:

- **Windows version pin**: `winver` or `[System.Environment]::OSVersion` plus build number.
- **Hardware baseline**: CPU, RAM, storage class.
- **Shell choice**: PowerShell 7+ preferred; record actual installed version. If only 5.1 is present, record and flag for Phase 2 (PowerShell 7+ install vs adapt scripts to 5.1).
- **WSL2 status**: availability, kernel version, default distribution, whether the harness will route shell-class hooks through WSL2.
- **Node and Python versions**: record both major versions and `py` launcher state.
- **Claude Code version pin**: minor-version range per QC.5. Verify Windows x86_64 build at the pinned version.
- **Working directory**: where the harness build runs from on Windows.
- **Daily-driver harness path**: in-repo, symlinked to `%USERPROFILE%\.claude\`, or WSL2-resident.
- **BitLocker status**: `manage-bde -status` summary.
- **Microsoft Defender state**: enabled, real-time protection state, exclusions if any.
- **AppLocker / WDAC**: whether configured.
- **PowerShell execution policy**: per scope (`MachinePolicy`, `UserPolicy`, `Process`, `CurrentUser`, `LocalMachine`).
- **Network egress monitoring**: GlassWire, simplewall, or equivalent installed.
- **Bash sandboxing on Windows**: `<NEEDS-WINDOWS-PORT-VALIDATION>` block. Verify what Claude Code's installed version supports on Windows. Fallback posture if not yet implemented.
- **Claude Code session log path on Windows**: `<NEEDS-WINDOWS-PORT-VALIDATION>` block. Run a short session and observe.

For each block filled, the decision lands in `windows/ARCHITECTURE.md`. The rationale lands in `phase-outputs/PHASE-0-DECISIONS.md`, one short paragraph per decision, citing the foundation document or research source that informs the choice.

For each block that cannot be resolved on Windows without Phase 3 implementation work, record the reason explicitly and tag it for Phase 3.

<investigate_before_answering>
Before recording a version pin, run the version command. Do not assume.

Before recording Claude Code's session log path or sandbox behavior on Windows, consult documentation and run a short session. Do not assume parity with Mac or Linux.

Before claiming Bash sandboxing on Windows has specific behavior, verify against the running Claude Code's actual behavior. Inference from Mac is not evidence.

Before claiming a tool is the Windows x86_64 build, verify by file inspection or version output naming the architecture.
</investigate_before_answering>

## Deliverables

Three updates and writes:

1. `windows/ARCHITECTURE.md`: every `<TBD-PHASE-0>` block filled or explicitly deferred with reason. Every `<NEEDS-WINDOWS-PORT-VALIDATION>` block the live environment can confirm is resolved. Remaining validation markers stay tagged for Phase 3 with a more specific note about what evidence resolves them.
2. `phase-outputs/PHASE-0-CONTEXT.md`: the `/context` output at start and end, with delta.
3. `phase-outputs/PHASE-0-DECISIONS.md`: one short paragraph per filled block, naming the decision and citing the source.

## Verification

Before reporting complete:

- No unaddressed `<TBD-PHASE-0>` blocks remain in `windows/ARCHITECTURE.md`.
- The remaining `<NEEDS-WINDOWS-PORT-VALIDATION>` markers each carry a more specific note than the scaffold version.
- The drift check returns 0 from a bash environment.
- The artifacts have substantive content (line counts reported).

Report line counts and remaining validation marker count.

## Anti-overengineering

Phase 0 records decisions. It does not implement them. Hooks, deny rules, skills, agents, and MCP server registrations are Phase 3 and Phase 4. If a Phase 0 decision implies a hook or skill, record the implication for Phase 3 or Phase 4 to act on. Do not write the hook or skill here.

The Quality Contract operationalization section references tools that are not yet wired. Phase 0 does not wire them. Phase 3 evaluates and decides.

When in doubt, defer to Phase 2 or Phase 3 with a recorded reason rather than acting.
