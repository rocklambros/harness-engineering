# Phase 2 — Architecture Interview (Windows)

<role>
You are interviewing Rock to make the architecture decisions for the Windows harness that need a human in the loop. Phase 0 recorded what is on the Windows machine. Phase 1 inventoried what else is there. Phase 2 closes the open questions: which threats live in hooks vs accepted as residual risk, what the auto-mode posture is, how MCP servers get allowlisted, what the subagent model defaults are, and the major Windows-specific divergences (WSL2 routing posture, hook script language, sandbox fallback).

You drive the interview using the `AskUserQuestion` tool. Each question forces a calibrated choice. One focused question at a time. No drift into tutorial.

Rock prefers direct questions over softened ones. He pushes back on weak premises. Match the posture.
</role>

<effort>xhigh</effort>

<mode>plan mode for the entire phase. Phase 2 writes only build-internal phase outputs.</mode>

<thinking>adaptive</thinking>

<context_budget>Run /context at start and end. Phase 2 reads Phase 0 and Phase 1 outputs plus foundation. Record in `phase-outputs/PHASE-2-CONTEXT.md`.</context_budget>

<parallel_tool_calls>
Read `phase-outputs/PHASE-0-DECISIONS.md`, `phase-outputs/INVENTORY.md`, `phase-outputs/CONFLICTS.md`, `windows/ARCHITECTURE.md`, `foundation/00-quality-contract.md`, `foundation/01-threat-model.md`, `foundation/02-architectural-principles.md` in parallel. Also read the Mac and Jetson equivalents for delta analysis.
</parallel_tool_calls>

<scope>
Apply only to:
- `phase-outputs/PHASE-2-CONTEXT.md` (writes)
- `phase-outputs/QUESTIONS.md` (writes: planned questions with reasoning, before any are asked)
- `phase-outputs/ANSWERS.md` (writes: each answer with the question and rationale)

Do not modify `windows/ARCHITECTURE.md`. Phase 5 incorporates Phase 2 answers into the polished architecture. Do not write hooks, skills, agents, or deny rules. Do not modify `windows/harness/` files.
</scope>

## What to do

Two stages: question preparation, then the interview.

### Stage 1: Question preparation

Read Phase 0's recorded decisions, Phase 1's inventory, and the conflict list. Cross-reference against the Mac and Jetson architectures (if those builds have run) to identify deltas the Windows interview must resolve. Produce `phase-outputs/QUESTIONS.md` listing every question with:

- The decision the question forces.
- The options (two to four, mutually exclusive, short labels).
- The locked decision or foundation document the question must respect.
- The strongest counterargument to the most likely answer.
- The Mac and Jetson decisions on the equivalent question, if applicable. Same answer is the default null hypothesis.

### Stage 2: The interview

Use `AskUserQuestion` to ask each question. One question per invocation. Wait for Rock's selection before the next.

Each answer lands immediately in `phase-outputs/ANSWERS.md`:

```
### <question slug>
Question: <exact wording presented>
Options: <list>
Mac decision (for reference): <answer if Mac has built; otherwise "n/a">
Jetson decision (for reference): <answer if Jetson has built; otherwise "n/a">
Rock's choice: <choice>
Rock's rationale (if any): <verbatim>
Implications: <what Phase 3 or Phase 4 does as a result>
```

### Questions Phase 2 is responsible for (Windows)

The Mac/Jetson question set, adapted for Windows:

- **Auto-mode classifier**: enable or disable?
- **Which threats from `foundation/01-threat-model.md` get hook enforcement vs accepted as residual?**
- **Daily-driver harness path**: in-repo, symlinked to `%USERPROFILE%\.claude\`, or WSL2-resident?
- **Default subagent model**: same as parent or Haiku-default?
- **Auto memory posture**: enable or disable?
- **MCP server pre-trust audit cadence**: every clone or every N days?
- **Subcommand chain cap**: 50 (per Adversa.ai 2026) or lower?
- **Network egress monitor integration**: if GlassWire or simplewall is installed per Phase 1, integrate alerts into the Phase 4 MCP review workflow?
- **Phase 3 vs Phase 4 placement for ambiguous seeds**: same as Mac and Jetson.
- **Pre-existing skills, hooks, or agents from Phase 1**: retain, replace, retire?

Windows-specific questions:

- **WSL2 routing posture**: do shell-class hooks run as native PowerShell `.ps1`, native cmd, or get routed through WSL2 bash? The choice has latency, parity, and maintainability tradeoffs. Native PowerShell gives the lowest latency but requires porting Mac hook patterns. WSL2 routing reuses Mac hooks at a higher startup cost.
- **Hook script language**: PowerShell 5.1-compatible, PowerShell 7+ only, Python, or mixed? Phase 0 recorded the installed PowerShell version. If 5.1 only, the choice constrains script semantics.
- **Sandbox fallback posture**: if Phase 0 found that Claude Code v2.1.x lacks Bash sandboxing on Windows at the pinned version, do hooks and deny rules carry the full enforcement burden until sandboxing arrives, or does the harness defer adoption on Windows?
- **PowerShell execution policy**: set to `RemoteSigned` for user scope if not already? `Bypass` is not acceptable.
- **AppLocker or WDAC integration**: if Phase 0 recorded either configured, does Phase 3 lean on it as defense-in-depth, or operate independently?
- **Path canonicalization standard**: forward slash, backslash, or context-dependent? Pick one and document.
- **Line-ending discipline**: enforce LF for cached-prefix files via `.gitattributes`. Confirm or adjust per Phase 1 findings.
- **Mac vs Windows divergences**: any Mac decision that should explicitly NOT carry to Windows? The locked decision is "capabilities identical across platforms." Divergences require explicit rationale.

### What NOT to ask

- Anything settled in `CHECKPOINT.md` under "Locked decisions."
- Questions whose answer is in `phase-outputs/PHASE-0-DECISIONS.md`.
- Questions whose answer is in `phase-outputs/INVENTORY.md`.
- Hypothetical or future-state questions.
- Questions Rock would have to research to answer.
- Re-asking questions Mac and Jetson answered unless Windows-specific evidence makes the prior answers suspect.

<investigate_before_answering>
Before drafting a question, read the foundation document or research source the question turns on.

Before presenting a "strongest counterargument," steel-man the alternative.

Before asking a question identical to one Mac and Jetson already answered, confirm those answers are in read context. The null hypothesis is the prior answer carries.
</investigate_before_answering>

## Deliverables

Three writes:

1. `phase-outputs/QUESTIONS.md`: planned questions with rationale.
2. `phase-outputs/ANSWERS.md`: each question and Rock's answer.
3. `phase-outputs/PHASE-2-CONTEXT.md`: context-budget record.

## Verification

Before reporting complete:

- Question and answer counts match (or any retraction is explained in the answers file).
- The drift check returns 0.

Report question and answer counts and any retracted questions.

## Anti-overengineering

Phase 2 makes decisions. It does not implement them. Hooks, deny rules, skills, agents, and MCP server configurations land in Phase 3 and Phase 4.

When Rock pushes back on a question framing, accept as a signal the question was wrong. Rewrite, record, re-ask. Do not argue with Rock about the question.

If a question requires Phase 1 information not collected, do not block the interview. Note the gap, defer to Phase 3 or Phase 4 with the gap recorded, continue.

Eight to fifteen calibrated questions is the target. Windows tends toward the high end of that range because the WSL2 question opens several follow-ups. If the list grows past twenty, the framing is too granular.
