# Phase 0: Goals and Scope

This phase establishes what we're building, what success looks like, and what's out of scope. It runs before any discovery or architecture work because everything downstream depends on a shared understanding of the target.

Phase 0 is short. It produces one document. It does not write any code or configuration.

---

<role>
You are a senior harness engineer working with Rock Lambros on a public reference repository documenting how a production-grade Claude Code harness is built. Phase 0 is the goal-setting phase. Your job is to produce a concrete, verifiable statement of what the Mac harness must do and what success looks like.

Read the foundation documents before producing the goal statement. Match the writing rules in `CLAUDE.md`.
</role>

<effort>high</effort>
<mode>default</mode>
<thinking>adaptive</thinking>
<context_budget>Run /context at start. Document the delta in the phase output.</context_budget>
<parallel_tool_calls>Prefer parallel reads for independent foundation files.</parallel_tool_calls>
<scope>Strict. Produce only the Phase 0 deliverable. Do not begin any Phase 1 work.</scope>

<context>
The repo holds the build sequence for a Mac harness. Before discovery (Phase 1) or architecture interview (Phase 2), we need a shared baseline of what the harness is supposed to accomplish.

The foundation documents in `foundation/` establish the Quality Contract, threat model, and architectural principles. Phase 0 instantiates those for the specific Mac harness build.
</context>

<investigate_before_answering>
Before producing the goal statement, read these files in full:

- `foundation/00-quality-contract.md`
- `foundation/01-threat-model.md`
- `foundation/02-architectural-principles.md`
- `mac/ARCHITECTURE.md`

Do not paraphrase from memory. If you reference a Quality Contract property or a threat ID, verify it exists in the foundation docs before citing it.
</investigate_before_answering>

<instructions>
Produce a single document at `phase-outputs/PHASE_0_GOALS.md`. Create the `phase-outputs/` directory if it doesn't exist (gitignored, build-internal).

The document has four sections:

**Section 1: Goal statement.** One paragraph (3-5 sentences) describing what the Mac harness must do when complete. Concrete. Verifiable. Not aspirational. Example shape: "The Mac harness enables a Claude Code session to write code against the developer's local filesystem with X, Y, Z properties enforced deterministically and A, B, C provided as guidance."

**Section 2: Success criteria.** A numbered list of 5-10 specific tests that, when passing, mean the harness is done. Each test must be either runnable as a command or observable in a single session. Example: "Running `./mac/scripts/drift-check.sh` returns exit code 0 against the repo at HEAD." Not example: "The harness is secure." That second one is not testable.

**Section 3: Out of scope.** A short list of capabilities or concerns that are explicitly not part of the Mac build. This is the place to name what we're declining to do. Multi-user support, custom model fine-tuning, web service deployment, and similar. Be specific about what's out and why.

**Section 4: Phase boundaries.** A short paragraph for each of Phase 1 through Phase 5 stating what that phase will produce and what success looks like for that phase. These are not new commitments; they reflect what's already in `ARCHITECTURE.md`.

Match the writing rules in `CLAUDE.md`. No em dashes. No semicolons. No corporate slop. Plain words.
</instructions>

<deliverable>
`phase-outputs/PHASE_0_GOALS.md` with the four sections above.

Report at the end: a 2-3 sentence summary of what the goal statement commits to, plus any open questions that should be carried into Phase 1.
</deliverable>

<verification>
After producing the deliverable, run `wc -l phase-outputs/PHASE_0_GOALS.md` and report. The document should be 80-200 lines. Shorter means thin. Longer means scope creep.

Run `./scripts/drift-check.sh` and confirm it passes.
</verification>
