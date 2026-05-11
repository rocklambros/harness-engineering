# Phase 5 — Wire and Document (Windows) [SCAFFOLDED]

**This prompt is scaffolded, not validated.** The structure mirrors `mac/prompts/phase-5-wire-and-document.md`. Windows-specific details resolve when Rock executes the Windows build.

<role>
You are wiring the Windows harness together and producing the polished documentation. Every prior phase produced raw outputs and rationale. Phase 5 reconciles against the Quality Contract and threat model, audits each artifact for scope discipline and correctness, and produces the final form of `windows/ARCHITECTURE.md`, `windows/harness/CLAUDE.md`, and `windows/README.md`.

Phase 5 uses the Writer/Reviewer subagent pattern. The main session writes. The Reviewer subagent audits each draft. Findings get addressed before phase completion.
</role>

<effort>xhigh</effort>

<mode>default mode for writing. Reviewer subagent runs in plan mode for its audit pass.</mode>

<thinking>adaptive</thinking>

<context_budget>Run /context at start and end. Phase 5 reads every prior phase output, foundation, threat model, architecture. Reviewer subagent runs in its own context. Record in `phase-outputs/PHASE-5-CONTEXT.md`.</context_budget>

<parallel_tool_calls>
Read inputs in parallel: all of `phase-outputs/`, populated `windows/harness/settings.json`, every file in `windows/harness/hooks/`, `windows/harness/rules/`, every `SKILL.md` in `windows/harness/skills/`, every file in `windows/harness/agents/`, `windows/ARCHITECTURE.md`, `windows/harness/CLAUDE.md`, `windows/README.md`, foundation documents, `windows/evaluations/deep-eval.md`. Mac and Jetson equivalents if those have built, for delta reference.
</parallel_tool_calls>

<scope>
Apply only to:
- `windows/ARCHITECTURE.md` (writes: polished final form. Every `<TBD>` and `<NEEDS-WINDOWS-PORT-VALIDATION>` block resolved or explicitly deferred with reason.)
- `windows/harness/CLAUDE.md` (writes: polished operational form. Line count under 160, hard cap 200.)
- `windows/README.md` (writes: polished section overview. Status changes from scaffolded to validated.)
- `windows/evaluations/pre-filter.md` (writes: final state, every candidate row resolved)
- `windows/evaluations/deep-eval.md` (writes: final state, every survivor evaluated)
- `phase-outputs/PHASE-5-AUDIT.md` (writes: Reviewer findings and dispositions)
- `phase-outputs/PHASE-5-CONTEXT.md` (writes)

May modify (only if Reviewer surfaces a finding requiring it):
- Files in `windows/harness/hooks/`, `windows/harness/rules/`, `windows/harness/skills/`, `windows/harness/agents/`, or `windows/harness/settings.json`. Each modification records the finding ID and rationale.

Do not modify `foundation/`, `research/`, or `windows/prompts/`. Do not modify `CHECKPOINT.md` or `CONVERSATION_HISTORY.md`.
</scope>

## What to do

Three stages: synthesis, audit, resolution.

### Stage 1: Synthesis

Polished `windows/ARCHITECTURE.md`: every `<TBD-PHASE-0>` resolves to Phase 0 value or recorded deferred-with-reason marker. Every `<NEEDS-WINDOWS-PORT-VALIDATION>` resolves to validated outcome or a recorded gap that the next QC.5 trigger addresses. Every Phase 2 decision lands in the relevant component section. Every Phase 3 hook and rule lands in the Permission layer. Every Phase 4 skill, agent, MCP server lands in the appropriate section. Version pins table fully populated.

Polished `windows/harness/CLAUDE.md`: under 160 lines, hard cap 200. Auto-memory line filled with Phase 2's decision. Operational notes reflect the harness as it actually exists.

Polished `windows/README.md`: section status changes from scaffolded to validated. Build date recorded. Any remaining gaps from `<NEEDS-WINDOWS-PORT-VALIDATION>` markers that did not resolve are listed in a "Known gaps" section with the next-revision trigger.

Polished evaluation worksheets: every candidate row resolved, every survivor with deep-eval paragraph including Windows-specific validation outcomes.

### Stage 2: Audit

Spawn the Reviewer subagent. The Reviewer reads the polished documents, every file in `windows/harness/`, populated `windows/harness/settings.json`, foundation documents, relevant sections of `research/Claude_Architecture.md`.

The Reviewer finds:

- **Scope drift**: artifacts produced outside what the phase prompt named without recorded rationale.
- **QC violations**: missing pinned versions, missing rationale comments, cache-prefix pollution, lines that put enforcement in CLAUDE.md instead of in a hook.
- **Threat model gaps**: threats the harness was supposed to address but does not.
- **Principle violations**: hooks-enforce-CLAUDE.md-advises misalignments, least-privilege violations, reversibility mismatches.
- **Schema or syntactic errors**: hook scripts with malformed schemas, settings.json keys that do not match Claude Code v2.1.x, deny patterns that do not parse.
- **Windows-specific finding class**: unresolved `<NEEDS-WINDOWS-PORT-VALIDATION>` markers without deferred-with-reason explanation, Windows assertions that lack actual evidence on Windows hardware, PowerShell version compatibility misalignment, WSL2 routing decisions that exceed measured latency budgets, path canonicalization inconsistency across hook scripts.

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

For each **fix now** finding, the main session edits the artifact and records the change. The cycle continues until no blocker findings remain.

**Accept residual risk** findings require rationale in both the audit log and the relevant artifact's header or commit message.

**Defer to revision** findings require a tracking entry in `REVISIONS.md` or the audit log.

Phase is complete when:

- No blocker findings remain unaddressed.
- Major findings fixed or have accepted-risk rationale.
- Minor findings fixed, deferred with tracking, or recorded as accepted.

<investigate_before_answering>
Before claiming a hook script returns a correct Zod schema, the Reviewer reads `research/Claude_Architecture.md` §5.3 and §6.

Before claiming a deny pattern matches a specific behavior, the Reviewer constructs a test input and verifies on Windows.

Before recording a finding's disposition, the Reviewer cites the foundation or research source.

Before declaring a `<NEEDS-WINDOWS-PORT-VALIDATION>` marker resolved, the Reviewer confirms actual evidence from Windows hardware exists in `phase-outputs/`. Inferred validation from Mac or Jetson is a major finding, not a resolution.
</investigate_before_answering>

## Deliverables

- Polished `windows/ARCHITECTURE.md`.
- Polished `windows/harness/CLAUDE.md`.
- Polished `windows/README.md`.
- Final `windows/evaluations/pre-filter.md` and `windows/evaluations/deep-eval.md`.
- `phase-outputs/PHASE-5-AUDIT.md`.
- `phase-outputs/PHASE-5-CONTEXT.md`.
- Any Phase 3 or Phase 4 artifact modified in response to a finding.

## Verification

Before reporting complete:

- No `<TBD>` markers in the three polished documents.
- `<NEEDS-WINDOWS-PORT-VALIDATION>` markers either all resolved, or each remaining marker has a "Known gaps" entry in `windows/README.md`.
- `windows/harness/CLAUDE.md` at most 200 lines.
- Drift check returns 0.
- `windows/harness/settings.json` parses.
- No unaddressed blocker findings.
- PowerShell hooks: PSScriptAnalyzer-clean. Python hooks: SAST-clean. WSL2-bash hooks: shellcheck-clean.

Report line counts, audit finding count by severity, deferred-to-revision items, remaining validation markers.

## Anti-overengineering

Phase 5 polishes. It does not redesign. Structural issues surfaced in audit go to `REVISIONS.md` as known gaps.

The Reviewer subagent is not permission to add work. The audit verifies what was built, not expands it.

The polished documentation does not add information not produced in prior phases.

When the build completes and audit clears, the Windows section graduates from scaffolded to validated. The first commit log entry records the build sequence as complete and the harness as operational on Windows.
