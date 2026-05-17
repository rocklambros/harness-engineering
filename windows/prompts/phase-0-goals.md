# Phase 0: Goals and Scope (Windows)

Establishes what the Windows + WSL2 harness must do. Same structure as Mac Phase 0 with Windows-specific framing around the WSL2 indirection.

---

<role>
You are a senior harness engineer working on the Windows variant of a Claude Code harness. Phase 0 establishes goals for the Windows build. The capability surface must match Mac per AP.3 even though the execution substrate (WSL2) differs.
</role>

<effort>high</effort>
<mode>default</mode>
<thinking>adaptive</thinking>
<context_budget>Run /context at start.</context_budget>
<parallel_tool_calls>Parallel reads.</parallel_tool_calls>
<scope>Strict. Phase 0 deliverable only.</scope>

<context>
The Windows harness must achieve cross-platform parity with the validated Mac build. The WSL2 indirection is an implementation detail of how, not what. The capability target is identical: same security stack, same hooks, same skills.

Mac Phase 0 outputs (if available) are the reference. Read them first.
</context>

<investigate_before_answering>
Read:

- `foundation/00-quality-contract.md`
- `foundation/01-threat-model.md`
- `foundation/02-architectural-principles.md` (especially AP.3)
- `windows/ARCHITECTURE.md`
- `mac/ARCHITECTURE.md`
- `mac/prompts/phase-0-goals.md`
- `mac/phase-outputs/PHASE_0_GOALS.md` if it exists
</investigate_before_answering>

<instructions>
Produce `phase-outputs/PHASE_0_GOALS.md` with four sections.

**Section 1: Goal statement.** What the Windows harness must do. Capability-aligned with Mac. Explicitly notes WSL2 as the execution substrate for Layers 2 and 3 of the security stack.

**Section 2: Success criteria.** 5-10 runnable tests. Examples:

`./scripts/drift-check.sh` returns 0 (runs from WSL2).

The PostToolUse Semgrep hook fires from Claude Code on Windows, runs inside WSL2, and surfaces findings in the same session.

`wsl.exe -e bash -c "semgrep --version"` returns the pinned Semgrep version.

The hook's round-trip latency is acceptable (subjective, but typically under 2 seconds cold).

Windows-specific path translation works correctly (Windows paths in payload translate to WSL2 paths in script).

**Section 3: Out of scope.** Same as Mac plus:

PowerShell-based hooks (bash via WSL2 is the chosen pattern).

Multi-WSL2-distribution support.

Native Windows tool substitutions (the WSL2 indirection is the decision).

Cross-platform development from Mac or Jetson to Windows.

**Section 4: Phase boundaries.** Phase 1-5 descriptions. Phase 3-5 note "needs validation when ported."

Match the writing rules.
</instructions>

<deliverable>
`phase-outputs/PHASE_0_GOALS.md`, 80-200 lines. Short summary report.
</deliverable>

<verification>
`./scripts/drift-check.sh` passes.
</verification>
