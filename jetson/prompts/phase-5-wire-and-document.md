# Phase 5 — Wire and Document (Jetson) [SCAFFOLDED]

**This prompt is scaffolded, not validated.** The structure mirrors `mac/prompts/phase-5-wire-and-document.md`. Jetson-specific details resolve when Rock executes the Jetson build.

<role>
You are wiring the Jetson harness together and producing the polished documentation. Every prior phase produced raw outputs and rationale. Phase 5 reconciles against the Quality Contract and threat model, audits each artifact for scope discipline and correctness, and produces the final form of `jetson/ARCHITECTURE.md`, `jetson/harness/CLAUDE.md`, and `jetson/README.md`.

Phase 5 uses the Writer/Reviewer subagent pattern. The main session writes. The Reviewer subagent audits each draft against foundation documents and threat model. Findings get addressed before phase completion.
</role>

<effort>xhigh</effort>

<mode>default mode for writing. Reviewer subagent runs in plan mode for its audit pass.</mode>

<thinking>adaptive</thinking>

<context_budget>Run /context at start and end. Phase 5 reads every prior phase output, foundation, threat model, architecture. Reviewer subagent runs in its own context. Record in `phase-outputs/PHASE-5-CONTEXT.md`.</context_budget>

<parallel_tool_calls>
Read inputs in parallel: all of `phase-outputs/`, populated `jetson/harness/settings.json`, every file in `jetson/harness/hooks/`, `jetson/harness/rules/`, every `SKILL.md` in `jetson/harness/skills/`, every file in `jetson/harness/agents/`, `jetson/ARCHITECTURE.md`, `jetson/harness/CLAUDE.md`, `jetson/README.md`, foundation documents, `jetson/evaluations/deep-eval.md`. Mac equivalents if Mac has built, for delta reference.
</parallel_tool_calls>

<scope>
Apply only to:
- `jetson/ARCHITECTURE.md` (writes: polished final form. Every `<TBD>` and `<NEEDS-JETSON-PORT-VALIDATION>` block resolved or explicitly deferred with reason.)
- `jetson/harness/CLAUDE.md` (writes: polished operational form. Line count under 160, hard cap 200.)
- `jetson/README.md` (writes: polished section overview. Status changes from scaffolded to validated.)
- `jetson/evaluations/pre-filter.md` (writes: final state, every candidate row resolved)
- `jetson/evaluations/deep-eval.md` (writes: final state, every survivor evaluated)
- `phase-outputs/PHASE-5-AUDIT.md` (writes: Reviewer findings and dispositions)
- `phase-outputs/PHASE-5-CONTEXT.md` (writes)

May modify (only if Reviewer surfaces a finding requiring it):
- Files in `jetson/harness/hooks/`, `jetson/harness/rules/`, `jetson/harness/skills/`, `jetson/harness/agents/`, or `jetson/harness/settings.json`. Each modification records the finding ID and rationale.

Do not modify `foundation/`, `research/`, or `jetson/prompts/`. Do not modify `CHECKPOINT.md` or `CONVERSATION_HISTORY.md`.
</scope>

## What to do

Three stages: synthesis, audit, resolution.

### Stage 1: Synthesis

Polished `jetson/ARCHITECTURE.md`: every `<TBD-PHASE-0>` resolves to Phase 0 value or recorded deferred-with-reason marker. Every `<NEEDS-JETSON-PORT-VALIDATION>` resolves to the validated outcome or a recorded gap that the next QC.5 trigger addresses. Every Phase 2 decision lands in the relevant component section. Every Phase 3 hook and rule lands in the Permission layer. Every Phase 4 skill, agent, MCP server lands in the appropriate section. Version pins table fully populated.

Polished `jetson/harness/CLAUDE.md`: under 160 lines, hard cap 200. Auto-memory line filled with Phase 2's decision. Operational notes reflect the harness as it actually exists.

Polished `jetson/README.md`: section status changes from scaffolded to validated. Build date recorded. Any remaining gaps from `<NEEDS-JETSON-PORT-VALIDATION>` markers that did not resolve are listed in a "Known gaps" section with the next-revision trigger.

Polished evaluation worksheets: every candidate row resolved, every survivor with deep-eval paragraph including ARM64 Linux validation outcome.

### Stage 2: Audit

Spawn the Reviewer subagent. The Reviewer reads the polished documents, every file in `jetson/harness/`, populated `jetson/harness/settings.json`, foundation documents, relevant sections of `research/Claude_Architecture.md`.

The Reviewer finds:

- **Scope drift**: artifacts produced outside what the phase prompt named without recorded rationale.
- **QC violations**: missing pinned versions, missing rationale comments, cache-prefix pollution, lines that put enforcement in CLAUDE.md instead of in a hook.
- **Threat model gaps**: threats the harness was supposed to address but does not.
- **Principle violations**: hooks-enforce-CLAUDE.md-advises misalignments, least-privilege violations, reversibility mismatches.
- **Schema or syntactic errors**: hook scripts with malformed schemas, settings.json keys that do not match Claude Code v2.1.x, deny patterns that do not parse.
- **Jetson-specific finding class**: unresolved `<NEEDS-JETSON-PORT-VALIDATION>` markers without a deferred-with-reason explanation, ARM64 Linux assertions that lack actual evidence on Jetson hardware, BSD-vs-GNU coreutils misalignment in shipped scripts.

Each finding lands in `phase-outputs/PHASE-5-AUDIT.md`:

```
### F<NN>: <one-line summary>
Severity: blocker | major | minor
Artifact: <path>
Evidence: <quote or specific line>
Citation: <foundation or research source>
Disposition: <fix now | accept residual risk with rationale | defer to revision>
```

### Stage 3: Resolution

For each **fix now** finding, the main session edits the artifact and records the change in the audit log. The cycle continues until no blocker findings remain.

**Accept residual risk** findings require rationale in both the audit log and the relevant artifact's header or commit message.

**Defer to revision** findings require a tracking entry in `REVISIONS.md` if it exists, or in the audit log as the temporary record.

Phase is complete when:

- No blocker findings remain unaddressed.
- Major findings fixed or have an accepted-risk rationale.
- Minor findings fixed, deferred with tracking, or recorded as accepted.

<investigate_before_answering>
Before claiming a hook script returns a correct Zod schema, the Reviewer reads `research/Claude_Architecture.md` §5.3 and §6.

Before claiming a deny pattern matches a specific behavior, the Reviewer constructs a test input and verifies. Pattern matching is empirical.

Before recording a finding's disposition, the Reviewer cites the foundation or research source.

Before declaring a `<NEEDS-JETSON-PORT-VALIDATION>` marker resolved, the Reviewer confirms actual evidence from Jetson hardware exists in `phase-outputs/`. Inferred validation from Mac is a major finding, not a resolution.
</investigate_before_answering>

## Deliverables

- Polished `jetson/ARCHITECTURE.md`.
- Polished `jetson/harness/CLAUDE.md`.
- Polished `jetson/README.md`.
- Final `jetson/evaluations/pre-filter.md` and `jetson/evaluations/deep-eval.md`.
- `phase-outputs/PHASE-5-AUDIT.md`.
- `phase-outputs/PHASE-5-CONTEXT.md`.
- Any Phase 3 or Phase 4 artifact modified in response to a finding.

## Verification

Before reporting complete:

- `grep -c '<TBD' jetson/ARCHITECTURE.md jetson/harness/CLAUDE.md jetson/README.md` returns 0 across all three.
- `grep -c '<NEEDS-JETSON-PORT-VALIDATION>' jetson/ARCHITECTURE.md jetson/harness/CLAUDE.md jetson/README.md` returns 0 across all three, or every remaining marker has a "Known gaps" entry in `jetson/README.md` with the next-revision trigger.
- `wc -l jetson/harness/CLAUDE.md` returns at most 200.
- `bash scripts/drift-check.sh` returns 0.
- `python3 -c "import json; json.load(open('jetson/harness/settings.json'))"` parses.
- `grep -c 'Severity: blocker' phase-outputs/PHASE-5-AUDIT.md` returns 0 for unaddressed blockers.
- For every hook script: shellcheck-clean.
- For every skill with an executable body: SAST-clean.

Report line counts, audit finding count by severity, deferred-to-revision items, remaining validation markers.

## Anti-overengineering

Phase 5 polishes. It does not redesign. Structural issues surfaced in the audit go to `REVISIONS.md` as known gaps. The Jetson build does not get rewritten in Phase 5; the build either passes audit or surfaces redesign work as a known gap.

The Reviewer subagent is not permission to add work. The audit's purpose is to verify what was built, not to expand it. Findings that propose new capability are rejected as out of scope unless they address a threat or QC property already on the board.

The polished documentation does not add information not produced in prior phases. Phase 5 reconciles, reorganizes, removes redundancy. It does not invent.

When the build completes and the audit clears, the Jetson section graduates from scaffolded to validated. The first commit log entry records the build sequence as complete and the harness as operational on Jetson.
