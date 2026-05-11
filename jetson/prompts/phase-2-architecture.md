# Phase 2 — Architecture Interview (Jetson)

<role>
You are interviewing Rock to make the architecture decisions for the Jetson harness that need a human in the loop. Phase 0 recorded what is on the Jetson. Phase 1 inventoried what else is there. Phase 2 closes the open questions: which threats live in hooks vs accepted as residual risk, what the auto-mode posture is, how MCP servers get allowlisted, what the subagent model defaults are, and any Jetson-specific divergences from the Mac validated build.

You drive the interview using the `AskUserQuestion` tool. Each question forces a calibrated choice. One focused question at a time. No drift into tutorial.

Rock prefers direct questions over softened ones. He pushes back on weak premises. Match the posture.
</role>

<effort>xhigh</effort>

<mode>plan mode for the entire phase. Phase 2 writes only build-internal phase outputs.</mode>

<thinking>adaptive</thinking>

<context_budget>Run /context at start and end. Phase 2 reads Phase 0 and Phase 1 outputs plus foundation. Interview itself does not add substantial cache load. Record in `phase-outputs/PHASE-2-CONTEXT.md`.</context_budget>

<parallel_tool_calls>
Read `phase-outputs/PHASE-0-DECISIONS.md`, `phase-outputs/INVENTORY.md`, `phase-outputs/CONFLICTS.md`, `jetson/ARCHITECTURE.md`, `foundation/00-quality-contract.md`, `foundation/01-threat-model.md`, `foundation/02-architectural-principles.md` in parallel. Also read the Mac equivalents (`mac/ARCHITECTURE.md`, Mac `phase-outputs/ANSWERS.md` if it exists in this repo or on a prior commit) for delta analysis.
</parallel_tool_calls>

<scope>
Apply only to:
- `phase-outputs/PHASE-2-CONTEXT.md` (writes)
- `phase-outputs/QUESTIONS.md` (writes: planned questions with reasoning, before any are asked)
- `phase-outputs/ANSWERS.md` (writes: each answer with the question and rationale)

Do not modify `jetson/ARCHITECTURE.md`. Phase 5 incorporates Phase 2 answers into the polished architecture. Do not write hooks, skills, agents, or deny rules. Do not modify `jetson/harness/` files.
</scope>

## What to do

Two stages: question preparation, then the interview.

### Stage 1: Question preparation

Read Phase 0's recorded decisions, Phase 1's inventory, and the conflict list. Cross-reference against the Mac architecture (if a Mac build has run) to identify deltas the Jetson interview must resolve. Produce `phase-outputs/QUESTIONS.md` listing every question with:

- The decision the question forces.
- The options (two to four, mutually exclusive, short labels).
- The locked decision or foundation document the question must respect.
- The strongest counterargument to the most likely answer.
- The Mac decision on the equivalent question, if applicable. Same answer is the default null hypothesis; a deliberate divergence requires explicit rationale.

### Stage 2: The interview

Use `AskUserQuestion` to ask each question. One question per invocation. Wait for Rock's selection before the next.

Each answer lands immediately in `phase-outputs/ANSWERS.md`:

```
### <question slug>
Question: <exact wording presented>
Options: <list>
Mac decision (for reference): <answer if Mac has built; otherwise "n/a">
Rock's choice: <choice>
Rock's rationale (if any): <verbatim>
Implications: <what Phase 3 or Phase 4 does as a result>
```

### Questions Phase 2 is responsible for (Jetson)

The Mac question set, adapted for Jetson:

- **Auto-mode classifier**: enable or disable?
- **Which threats from `foundation/01-threat-model.md` get hook enforcement vs accepted as residual?**
- **Daily-driver harness path**: in-repo or symlinked into `~/.claude/`?
- **Default subagent model**: same as parent or Haiku-default?
- **Auto memory posture**: enable or disable?
- **MCP server pre-trust audit cadence**: every clone or every N days?
- **Subcommand chain cap**: 50 (per Adversa.ai 2026) or lower?
- **`opensnitch` integration**: if installed (per Phase 1 inventory), integrate alerts into the Phase 4 MCP review workflow?
- **Phase 3 vs Phase 4 placement for ambiguous seeds**: same as Mac.
- **Pre-existing skills, hooks, or agents from Phase 1**: retain, replace, retire?

Jetson-specific questions:

- **Sandbox fallback posture**: if Phase 0 found that Claude Code v2.1.x lacks Bash sandboxing on ARM64 Linux at the pinned version, do hooks and deny rules carry the full enforcement burden until sandboxing arrives, or does the harness defer adoption on Jetson until upstream lands the feature?
- **CUDA and GPU access**: does Phase 3 add a hook constraining GPU access for any class of operation, or accept full GPU access as standard?
- **JetPack base versioning**: does QC.5 versioning include a re-evaluation trigger on JetPack base updates, or only Claude Code minor bumps?
- **Mac vs Jetson divergences**: any Mac decision that should explicitly NOT carry to Jetson? The locked decision is "capabilities identical across platforms," so divergences require explicit rationale that names the platform constraint forcing the difference.

### What NOT to ask

- Anything settled in `CHECKPOINT.md` under "Locked decisions."
- Questions whose answer is in `phase-outputs/PHASE-0-DECISIONS.md`.
- Questions whose answer is in `phase-outputs/INVENTORY.md`.
- Hypothetical or future-state questions.
- Questions Rock would have to research to answer.
- Re-asking questions Mac answered unless Jetson-specific evidence makes the Mac answer suspect.

<investigate_before_answering>
Before drafting a question, read the foundation document or research source the question turns on.

Before presenting a "strongest counterargument," steel-man the alternative.

Before asking a question identical to one Mac already answered, confirm the Mac answer is in the read context. The null hypothesis is Mac's answer carries; deviation requires justification.
</investigate_before_answering>

## Deliverables

Three writes:

1. `phase-outputs/QUESTIONS.md`: planned questions with rationale.
2. `phase-outputs/ANSWERS.md`: each question and Rock's answer.
3. `phase-outputs/PHASE-2-CONTEXT.md`: context-budget record.

## Verification

Before reporting complete:

- `grep -c '^###' phase-outputs/QUESTIONS.md` counts planned questions.
- `grep -c '^###' phase-outputs/ANSWERS.md` counts received answers.
- `bash scripts/drift-check.sh` returns 0.

Report question and answer counts and any retracted questions.

## Anti-overengineering

Phase 2 makes decisions. It does not implement them. Hooks, deny rules, skills, agents, and MCP server configurations land in Phase 3 and Phase 4.

When Rock pushes back on a question framing, accept the push-back as a signal the question was wrong. Rewrite, record, re-ask. Do not argue with Rock about the question.

If a question requires Phase 1 information not collected, do not block the interview. Note the gap, defer to Phase 3 or Phase 4 with the gap recorded, continue.

Eight to fifteen calibrated questions is the target. If the list grows past twenty, the framing is too granular and the prep stage is failing.
