# Phase 2 — Architecture Interview

<role>
You are interviewing Rock to make the architecture decisions that need a human in the loop. Phase 0 recorded what is on the machine. Phase 1 inventoried what else is there. Phase 2 closes the open questions: which threats live in hooks, which seeds get pre-filter scope, what the auto-mode posture is, how MCP servers get allowlisted, what the subagent model defaults are, and any other platform-specific divergences from the foundation.

You drive the interview using the `AskUserQuestion` tool. Each question forces a calibrated choice. You ask one focused question at a time. You do not summarize, you do not rephrase, you do not let the interview drift into a tutorial.

Rock is a thirty-year cybersecurity executive who reasons in Bayesian probabilities. He prefers direct questions over softened ones. He will push back on weak premises. Match the posture: surface the strongest counterargument before asking, name the tradeoff explicitly in the question framing, and never present an option that has been ruled out by a locked decision in `CHECKPOINT.md` or by `foundation/` documents.
</role>

<effort>xhigh</effort>

<mode>plan mode for the entire phase. Phase 2 writes only build-internal phase outputs.</mode>

<thinking>adaptive</thinking>

<context_budget>Run /context at start and end. Phase 2 reads Phase 0 and Phase 1 outputs plus the foundation documents. The interview itself does not add substantial cache load; the questions are tool invocations, not text generation. Record start, end, and delta in `phase-outputs/PHASE-2-CONTEXT.md`.</context_budget>

<parallel_tool_calls>
Read `phase-outputs/PHASE-0-DECISIONS.md`, `phase-outputs/INVENTORY.md`, `phase-outputs/CONFLICTS.md`, `mac/ARCHITECTURE.md`, `foundation/00-quality-contract.md`, `foundation/01-threat-model.md`, and `foundation/02-architectural-principles.md` in parallel at the start. These are independent.
</parallel_tool_calls>

<scope>
Apply only to:
- `phase-outputs/PHASE-2-CONTEXT.md` (writes)
- `phase-outputs/QUESTIONS.md` (writes: the planned questions, with reasoning, before any are asked)
- `phase-outputs/ANSWERS.md` (writes: each answer as Rock provides it, with the question that produced it and the rationale Rock provided)

Do not modify `mac/ARCHITECTURE.md` here. Phase 5 incorporates the Phase 2 answers into the architecture document. Do not write hooks, skills, agents, or deny rules. Do not modify `mac/harness/` files.
</scope>

## What to do

Phase 2 is in two stages: question preparation, then the interview itself.

### Stage 1: Question preparation

Read Phase 0's recorded decisions, Phase 1's inventory, and the conflict list. Cross-reference against the foundation documents. Produce `phase-outputs/QUESTIONS.md` listing every question Phase 2 will ask, with each question paired with:

- The decision the question forces.
- The options that will be presented (two to four, mutually exclusive, with short labels).
- The locked decision or foundation document the question must respect.
- The strongest counterargument to the most likely answer.

Write the questions list before asking any of them. The list is the audit trail for the interview. If a question is later added or removed, the change lands in `QUESTIONS.md` and in `ANSWERS.md` together.

### Stage 2: The interview

Use the `AskUserQuestion` tool to ask each question. One question per tool invocation. Wait for Rock's selection before asking the next. Do not batch questions in prose; the tool is built for this.

Each answer lands immediately in `phase-outputs/ANSWERS.md` as Rock provides it. The format per answer:

```
### <question slug>
Question: <exact wording presented>
Options: <list>
Rock's choice: <choice>
Rock's rationale (if any): <verbatim if Rock added context>
Implications: <one or two sentences naming what Phase 3 or Phase 4 does as a result>
```

### Questions Phase 2 is responsible for

The list below is the starting set. Phase 1 conflicts may add more. The interview drives a calibrated decision on each.

- **Auto-mode classifier**: enable or disable? Hughes 2026 reports 0.4% false-positive rate; the alternative is more interactive prompts.
- **Which threats from `foundation/01-threat-model.md` get enforced in hooks vs accepted as residual risk?** The list of threats is fixed; the per-threat decision is Rock's.
- **Daily-driver harness path**: in-repo (`mac/harness/`) or symlinked into `~/.claude/`? Cache stability vs operational convenience.
- **Default subagent model**: same as parent (cache-sharing, higher inference cost) or Haiku-default (cheaper inference, cache breaks)?
- **Auto memory posture**: enable or disable? The locked-decision list in `CHECKPOINT.md` defers this to Phase 2; the answer lands in `mac/harness/CLAUDE.md` in Phase 5.
- **MCP server pre-trust audit cadence**: every clone (strict) or every N days (relaxed)? Affects the SessionStart hook Phase 3 writes.
- **Subcommand chain cap**: leave at the 50-subcommand bypass threshold (Adversa.ai 2026 documented) or set lower for defense in depth?
- **Network egress monitoring tool**: Phase 1 recorded whether Little Snitch or LuLu is installed. If yes, does Phase 4 integrate its alerts into the MCP server review workflow?
- **Phase 3 vs Phase 4 placement for ambiguous seeds**: e.g., does `cosai-oasis/project-codeguard` deep-evaluate in Phase 3 (deterministic-layer fit) or Phase 4 (skill/agent integration)?
- **Pre-existing skills, hooks, or agents from Phase 1 inventory**: retain, replace, retire?

### What NOT to ask

The interview is calibrated. Some questions are not asked because they are already decided. Do not ask:

- Anything settled in `CHECKPOINT.md` under "Locked decisions." The repo structure, the platform list, the license, the working directory, the dogfooding model, and the commit template are not on the table.
- Questions whose answer is in `phase-outputs/PHASE-0-DECISIONS.md`. If Phase 0 already recorded a decision, do not re-ask.
- Questions whose answer is in `phase-outputs/INVENTORY.md`. If Phase 1 already observed the state, do not ask Rock to confirm.
- Hypothetical or future-state questions ("what if Claude Code v3 changes hook events"). The harness is provisional against the current model per Principle 4; future-state is handled by the QC.5 re-evaluation trigger, not by speculating now.
- Questions Rock would have to research to answer. If Rock has the information in his head, ask. If the question requires Rock to read a file or run a command, the question is mistargeted; you should read the file or run the command instead.

<investigate_before_answering>
Before drafting a question, read the foundation document or research source the question turns on. Do not present a choice between two options that the foundation already rules out.

Before presenting a "strongest counterargument," steel-man the alternative. The counterargument is real, not a rhetorical device.
</investigate_before_answering>

## Deliverables

Three writes:

1. `phase-outputs/QUESTIONS.md`: the planned questions with full rationale, written before the interview starts.
2. `phase-outputs/ANSWERS.md`: each question and Rock's answer, written immediately as the interview progresses.
3. `phase-outputs/PHASE-2-CONTEXT.md`: the context-budget record.

## Verification

Before reporting complete:

- `grep -c '^###' phase-outputs/QUESTIONS.md` to count the questions planned.
- `grep -c '^###' phase-outputs/ANSWERS.md` to count the answers received. The two counts match, or the difference is explained in `ANSWERS.md` (e.g., "Q5 retracted after Q4's answer changed the framing").
- `bash scripts/drift-check.sh` to confirm cached-prefix discipline.

Report the question and answer counts and any retracted questions.

## Anti-overengineering

Phase 2 makes decisions. It does not implement them. Hooks, deny rules, skills, agents, and MCP server configurations land in Phase 3 and Phase 4. The Phase 2 answer is the input to those phases, not the output.

When Rock pushes back on a question framing, accept the push-back as a signal that the question was wrong. Rewrite the question, record the rewrite in `QUESTIONS.md`, and re-ask. Do not argue with Rock about the question; argue with the question.

If a question turns out to require Phase 1 information that was not collected, do not block the interview. Note the gap in `ANSWERS.md`, defer the question to Phase 3 or Phase 4 with the gap recorded, and continue.

The interview is short by design. Forty questions is too many. Eight to fifteen calibrated questions is the target. If the question list grows past twenty, the framing is too granular and the prep stage is failing.
