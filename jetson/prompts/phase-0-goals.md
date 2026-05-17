# Phase 0: Goals and Scope (Jetson)

Establishes what we're building on Jetson, what success looks like, and what's out of scope. Same structure as the Mac Phase 0 prompt with Jetson-specific framing.

---

<role>
You are a senior harness engineer working on the Jetson AGX Orin variant of a Claude Code harness. Phase 0 establishes goals for the Jetson build. Your job is to produce a concrete, verifiable statement of what the Jetson harness must do.

The capability surface must match Mac per AP.3. Where the implementation differs (tool choice, install path), the differences are documented in Phase 2 and `ARCHITECTURE.md`. Phase 0 is about what the harness must achieve, not about how.
</role>

<effort>high</effort>
<mode>default</mode>
<thinking>adaptive</thinking>
<context_budget>Run /context at start. Document delta in the phase output.</context_budget>
<parallel_tool_calls>Use parallel reads for foundation and Mac reference files.</parallel_tool_calls>
<scope>Strict. Produce only the Phase 0 deliverable. Do not begin Phase 1.</scope>

<context>
The Jetson harness must achieve cross-platform parity with the validated Mac build. The Mac Phase 0 goals are in `mac/phase-outputs/PHASE_0_GOALS.md` if available, or the Mac `prompts/phase-0-goals.md` provides the template.

This Phase 0 establishes the same capability target on Jetson, plus any Jetson-specific success criteria that arise from the platform's nature (Tegra-specific paths, JetPack version constraints, ARM64 tool availability).
</context>

<investigate_before_answering>
Read these files in full before producing the goal statement:

- `foundation/00-quality-contract.md`
- `foundation/01-threat-model.md`
- `foundation/02-architectural-principles.md` (especially AP.3 cross-platform parity)
- `jetson/ARCHITECTURE.md`
- `mac/ARCHITECTURE.md` (the validated reference)
- `mac/prompts/phase-0-goals.md` (template structure)

If `mac/phase-outputs/PHASE_0_GOALS.md` exists, read it as the validated reference. The Jetson goals mirror it.
</investigate_before_answering>

<instructions>
Produce `phase-outputs/PHASE_0_GOALS.md` with these sections:

**Section 1: Goal statement.** One paragraph describing what the Jetson harness must do. Concrete, verifiable, capability-aligned with Mac.

**Section 2: Success criteria.** Numbered list of 5-10 specific runnable tests. Each test must be executable as a command on the Jetson. Examples:

`./scripts/drift-check.sh` returns exit code 0.

`mac/harness/hooks/post-tool-use-semgrep.sh` (after the Jetson port renames to `jetson/harness/hooks/post-tool-use-semgrep.sh`) runs cleanly against a synthetic SQL injection test file.

Semgrep installed on Jetson catches the same CWE-89 patterns as on Mac (specific rule set verified).

Include Jetson-specific success criteria: JetPack version compatibility verified, Tegra-specific paths covered by `rules/paths.deny`, no Mac-specific assumptions remain in the Jetson harness files.

**Section 3: Out of scope.** Same as Mac out-of-scope list plus Jetson-specific exclusions: cross-compilation from Mac, CUDA-specific anti-pattern coverage in `security-review` skill, local-inference Claude Code variants, multi-user setup.

**Section 4: Phase boundaries.** One paragraph for Phase 1 through Phase 5 stating what each produces on Jetson. The Phase 3-5 entries explicitly note "needs validation when ported."

Match the writing rules. No em dashes. No semicolons. No corporate slop.
</instructions>

<deliverable>
`phase-outputs/PHASE_0_GOALS.md` with the four sections.

A 2-3 sentence summary report at the end.
</deliverable>

<verification>
Run `wc -l phase-outputs/PHASE_0_GOALS.md` and report. Expected 80-200 lines.

Run `./scripts/drift-check.sh`. It must pass.
</verification>
