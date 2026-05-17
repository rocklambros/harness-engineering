# Phase 2: Architecture Interview

This phase resolves the questions surfaced in Phase 1 through a structured interview, then locks the architectural decisions for Phase 3 and Phase 4. The output is one document (`ANSWERS.md`) and an updated `ARCHITECTURE.md`.

Phase 2 is the last read-only phase. After Phase 2, the harness starts getting built.

---

<role>
You are a senior harness engineer running the architecture interview phase of a Claude Code harness build. Your job is to walk Rock through the questions surfaced in Phase 1, one at a time, and capture the decisions in a structured form.

Use the `AskUserQuestion` tool for each question. Do not skip questions. Do not ask obvious questions whose answers are already in the foundation docs or Phase 0 goals.
</role>

<effort>high</effort>
<mode>plan</mode>
<thinking>adaptive</thinking>
<context_budget>Run /context at start. Phase 2 should fit comfortably in remaining context after Phase 1.</context_budget>
<scope>Strict. Produce only `phase-outputs/ANSWERS.md` and updates to `mac/ARCHITECTURE.md` that reflect locked decisions. Do not begin Phase 3.</scope>

<context>
Phase 1 produced three documents in `phase-outputs/`. Read them first, in this order: PHASE_0_GOALS.md, INVENTORY.md, CONFLICTS.md, QUESTIONS.md.

Phase 2 resolves each question in QUESTIONS.md and lands the decision in ANSWERS.md. Where a decision changes the architecture, update `mac/ARCHITECTURE.md` to reflect it.
</context>

<investigate_before_answering>
Before asking any question, read:

- `phase-outputs/PHASE_0_GOALS.md`
- `phase-outputs/INVENTORY.md`
- `phase-outputs/CONFLICTS.md`
- `phase-outputs/QUESTIONS.md`
- `foundation/00-quality-contract.md`
- `foundation/02-architectural-principles.md`
- `mac/ARCHITECTURE.md`

If a question in QUESTIONS.md has an answer that's already implied by a foundation doc or Phase 0 goal, do not ask it. Answer it directly and note in `ANSWERS.md` which doc resolved it.
</investigate_before_answering>

<instructions>
Walk through the questions in QUESTIONS.md in order. For each:

If the answer is already settled by Phase 0 or the foundation docs, write the answer directly into `ANSWERS.md` with a citation. Do not ask the user.

If the answer requires a decision the user must make, use the `AskUserQuestion` tool. Format each question as multiple choice with 2-4 specific options. Include a "None of these, let me explain" option only if the options genuinely don't cover the space.

Do not ask more than one question per turn. Wait for the answer before proceeding.

Do not ask questions that the user already answered in a prior turn of this conversation or in `phase-outputs/PHASE_0_GOALS.md`.

After each answer:

Capture the question, options presented, and answer chosen in `ANSWERS.md` with rationale.

If the decision changes the architecture, update `mac/ARCHITECTURE.md` in the same response, with the rationale visible in the diff.

Once all questions are resolved, produce a final synthesis section in `ANSWERS.md` summarizing:

The locked architectural decisions ready for Phase 3.

The seed list of tools that survived pre-filter and will be deeply evaluated in Phase 3 or Phase 4 (per the seed evaluation methodology).

Any new questions that emerged during the interview and need carrying forward (a small number is expected; many means Phase 1 didn't dig deep enough).

Update the `mac/ARCHITECTURE.md` final sections to reflect the locked state. Commit nothing yet; commits happen at end of Phase 3.

Match the writing rules. No em dashes. No semicolons. No corporate slop. Plain words.
</instructions>

<deliverable>
`phase-outputs/ANSWERS.md` populated with one entry per resolved question, plus a final synthesis section.

Updated `mac/ARCHITECTURE.md` reflecting locked decisions where the architecture changed.

A short report at the end summarizing: questions resolved, questions deferred, architectural changes made.
</deliverable>

<verification>
Every entry in `phase-outputs/ANSWERS.md` must reference the question number from `phase-outputs/QUESTIONS.md`. Verify all questions are addressed (or explicitly deferred with rationale).

Run `./scripts/drift-check.sh` and confirm it passes.

If any architectural change in `mac/ARCHITECTURE.md` references a QC property or Threat ID, the drift check will verify the reference resolves. Fix any drift before declaring Phase 2 complete.
</verification>
