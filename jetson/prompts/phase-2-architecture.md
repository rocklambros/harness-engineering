# Phase 2: Architecture Interview (Jetson)

Resolves the questions surfaced in Phase 1 and locks the architecture for Phase 3 onward. Last read-only phase. Same structure as Mac Phase 2 with Jetson-specific considerations.

---

<role>
You are a senior harness engineer running the architecture interview phase of a Claude Code harness build on Jetson AGX Orin. Your job is to walk through the questions from Phase 1 via `AskUserQuestion`, capture decisions in `ANSWERS.md`, and update `jetson/ARCHITECTURE.md` where the architecture changes.
</role>

<effort>high</effort>
<mode>plan</mode>
<thinking>adaptive</thinking>
<context_budget>Run /context at start. Phase 2 fits comfortably after Phase 1.</context_budget>
<scope>Strict. Only `phase-outputs/ANSWERS.md` and `jetson/ARCHITECTURE.md`. Do not begin Phase 3.</scope>

<context>
Phase 1 produced inventory, conflicts, and questions. Phase 2 resolves them.

The Jetson architecture must remain capability-equivalent to Mac per AP.3. Decisions that introduce Jetson-only capability gaps need an explicit rationale and flag in `ANSWERS.md` for downstream review.
</context>

<investigate_before_answering>
Read in full:

- `phase-outputs/PHASE_0_GOALS.md`
- `phase-outputs/INVENTORY.md`
- `phase-outputs/CONFLICTS.md`
- `phase-outputs/QUESTIONS.md`
- `foundation/00-quality-contract.md`
- `foundation/02-architectural-principles.md` (AP.3 in particular)
- `jetson/ARCHITECTURE.md`
- `mac/ARCHITECTURE.md` (the validated reference)
- If Mac Phase 2 outputs exist (`mac/phase-outputs/ANSWERS.md`), read them too. The Jetson decisions should reference the Mac equivalents.
</investigate_before_answering>

<instructions>
Walk through `QUESTIONS.md` in order. For each:

If the answer is settled by Phase 0, the foundation docs, or the Mac Phase 2 answers, write the answer directly into `ANSWERS.md` with citations. Do not ask the user redundantly.

If the answer requires a user decision, use `AskUserQuestion` with 2-4 specific options. One question per turn.

Capture each answer in `ANSWERS.md` with rationale. Update `jetson/ARCHITECTURE.md` where the architecture changes.

After all questions resolve, produce a synthesis section in `ANSWERS.md` covering:

Locked architectural decisions for Phase 3.

Tool install commands for the Jetson (the apt and pip invocations that Phase 3 will run).

Any deferred questions carried forward.

A Jetson-vs-Mac comparison table showing where the two diverge and why.

Match the writing rules.
</instructions>

<deliverable>
`phase-outputs/ANSWERS.md` and updated `jetson/ARCHITECTURE.md`. Short report at the end.
</deliverable>

<verification>
Every entry in `ANSWERS.md` references the originating question number.

Cross-platform divergences are explicitly justified per AP.3.

`./scripts/drift-check.sh` passes.
</verification>
