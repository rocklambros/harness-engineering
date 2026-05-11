# Phase 5 — Wire and Document

<role>
You are wiring the Mac harness together and producing the polished documentation. Every prior phase produced raw outputs and rationale notes. Phase 5 reconciles those outputs against the Quality Contract and the threat model, audits each artifact for scope discipline and correctness, and produces the final form of `mac/ARCHITECTURE.md`, `mac/harness/CLAUDE.md`, and `mac/README.md`.

Phase 5 uses the Writer/Reviewer subagent pattern. The main session writes; the Reviewer subagent audits each draft against the foundation documents and the threat model. Findings get addressed before the phase completes. The Reviewer is defined in `mac/harness/agents/reviewer.md` from Phase 4.
</role>

<effort>xhigh</effort>

<mode>default mode for writing. The Reviewer subagent runs in plan mode for its audit pass.</mode>

<thinking>adaptive</thinking>

<context_budget>Run /context at start and end. Phase 5 reads every prior phase output, the foundation, the threat model, and the architecture document. The reads are substantial. Reviewer subagent runs in its own context, so the main session does not pay the audit's read cost directly. Record start, end, and delta in `phase-outputs/PHASE-5-CONTEXT.md`.</context_budget>

<parallel_tool_calls>
Read inputs in parallel at the start: all of `phase-outputs/`, the populated `mac/harness/settings.json`, every file in `mac/harness/hooks/`, every file in `mac/harness/rules/`, every `SKILL.md` in `mac/harness/skills/`, every file in `mac/harness/agents/`, `mac/ARCHITECTURE.md`, `mac/harness/CLAUDE.md`, `mac/README.md`, the foundation documents, and `mac/evaluations/deep-eval.md`. These are independent.
</parallel_tool_calls>

<scope>
Apply only to:
- `mac/ARCHITECTURE.md` (writes: the polished final form; every `<TBD>` block resolved or explicitly deferred with a recorded reason)
- `mac/harness/CLAUDE.md` (writes: the polished operational form; line count under 160, hard cap 200)
- `mac/README.md` (writes: the polished section overview)
- `mac/evaluations/pre-filter.md` (writes: final state, every candidate row resolved)
- `mac/evaluations/deep-eval.md` (writes: final state, every survivor evaluated)
- `phase-outputs/PHASE-5-AUDIT.md` (writes: the Reviewer's findings and dispositions)
- `phase-outputs/PHASE-5-CONTEXT.md` (writes)

May modify, only if the Reviewer surfaces a finding the audit requires:

- Files in `mac/harness/hooks/`, `mac/harness/rules/`, `mac/harness/skills/`, `mac/harness/agents/`, or `mac/harness/settings.json`. Each modification records the finding ID from `PHASE-5-AUDIT.md` and the change rationale.

Do not modify `foundation/`, `research/`, or `mac/prompts/`. Do not modify `CHECKPOINT.md` or `CONVERSATION_HISTORY.md`.
</scope>

## What to do

Phase 5 is in three stages: synthesis, audit, then resolution.

### Stage 1: Synthesis

Produce the final form of `mac/ARCHITECTURE.md`. Every `<TBD-PHASE-0>` block resolves to the Phase 0 value or to a recorded deferred-with-reason marker. Every Phase 2 decision lands in the relevant component section. Every Phase 3 hook and rule lands in the Permission layer section. Every Phase 4 skill, agent, and MCP server lands in the appropriate section. The version pins table is fully populated.

Produce the final form of `mac/harness/CLAUDE.md`. Line count stays under 160, hard cap 200. The auto-memory line is filled with Phase 2's decision. The operational notes reflect the harness as it actually exists, not as it was scaffolded in Batch 2.

Produce the final form of `mac/README.md`. The section overview reflects the validated build. The status section records the first build sequence date and any post-build revisions.

Produce the final form of the evaluation worksheets. Every candidate row is resolved. Every survivor has a deep-eval paragraph. Rejected candidates have their rationale on the record.

### Stage 2: Audit

Spawn the Reviewer subagent defined in `mac/harness/agents/reviewer.md`. The Reviewer reads:

- The polished `mac/ARCHITECTURE.md`, `mac/harness/CLAUDE.md`, and `mac/README.md`.
- Every file in `mac/harness/hooks/`, `mac/harness/rules/`, `mac/harness/skills/`, and `mac/harness/agents/`.
- The populated `mac/harness/settings.json`.
- The foundation documents (Quality Contract, threat model, architectural principles, seed evaluation methodology).
- The relevant sections of `research/Claude_Architecture.md` (§5, §6, §8).

The Reviewer's job is to find:

- **Scope drift**: code or documentation produced outside what the phase prompt named, without a recorded rationale.
- **QC violations**: missing pinned versions, missing rationale comments, cache-prefix pollution, lines that put enforcement in CLAUDE.md instead of in a hook.
- **Threat model gaps**: threats in `foundation/01-threat-model.md` that the harness was supposed to address but does not, or addresses only advisorily.
- **Principle violations**: hooks-enforce-CLAUDE.md-advises misalignments, least-privilege violations, reversibility mismatches.
- **Schema or syntactic errors**: hook scripts that return malformed schemas, settings.json keys that do not match Claude Code v2.1.x, deny patterns that do not parse.

Each finding lands in `phase-outputs/PHASE-5-AUDIT.md` as:

```
### F<NN>: <one-line finding summary>
Severity: blocker | major | minor
Artifact: <path>
Evidence: <quote or specific line>
Citation: <foundation or research source>
Disposition: <fix now | accept residual risk with rationale | defer to revision>
```

The Reviewer returns the audit list. The main session does not edit the audit list; it acts on it.

### Stage 3: Resolution

For each finding marked **fix now**, the main session edits the relevant artifact and records the change in the audit log. The cycle continues until no blocker findings remain.

Findings marked **accept residual risk** require a rationale recorded both in the audit log and in the relevant artifact's header or commit message.

Findings marked **defer to revision** require a tracking entry in `REVISIONS.md` if that file exists, or in the audit log as the temporary record.

The phase is complete when:

- No blocker findings remain unaddressed.
- Major findings are either fixed or have an accepted-risk rationale.
- Minor findings are either fixed, deferred with a tracked entry, or recorded as accepted in the audit log.

<investigate_before_answering>
Before claiming a hook script returns a correct Zod schema, the Reviewer reads `research/Claude_Architecture.md` §5.3 and §6 and confirms the field names and types. The architecture document is authoritative.

Before claiming a deny pattern matches a specific behavior, the Reviewer constructs a test input and verifies the match. Pattern matching is empirical, not theoretical.

Before recording a finding's disposition, the Reviewer cites the foundation or research source that turned the decision. A disposition without a citation is a guess, not a finding.
</investigate_before_answering>

## Deliverables

- Polished `mac/ARCHITECTURE.md`.
- Polished `mac/harness/CLAUDE.md`.
- Polished `mac/README.md`.
- Final `mac/evaluations/pre-filter.md` and `mac/evaluations/deep-eval.md`.
- `phase-outputs/PHASE-5-AUDIT.md` with every finding and its disposition.
- `phase-outputs/PHASE-5-CONTEXT.md`.
- Any Phase 3 or Phase 4 artifact modified in response to an audit finding, with the modification's rationale recorded.

## Verification

Before reporting complete:

- `grep -c '<TBD' mac/ARCHITECTURE.md mac/harness/CLAUDE.md mac/README.md` returns 0 across all three.
- `wc -l mac/harness/CLAUDE.md` returns at most 200.
- `bash scripts/drift-check.sh` returns 0.
- `python3 -c "import json; json.load(open('mac/harness/settings.json'))"` parses cleanly.
- `grep -c 'Severity: blocker' phase-outputs/PHASE-5-AUDIT.md` returns 0 for unaddressed blockers (each one has a "Disposition: fix now" with the corresponding artifact change, or the disposition is explicitly accepted).
- For every hook script: shellcheck-clean.
- For every skill with an executable body: SAST-clean.
- The number of `<TBD>` markers across all `mac/` artifacts is 0.

Report the line counts for the three polished documents, the audit finding count broken down by severity, and any deferred-to-revision items.

## Anti-overengineering

Phase 5 polishes; it does not redesign. If the audit surfaces a structural issue that requires a redesign, the issue is a blocker finding with the disposition "defer to revision" and a tracked entry in `REVISIONS.md`. The Mac build does not get rewritten in Phase 5; the build either passes the audit or surfaces the redesign work as a known gap.

The Reviewer subagent is not a permission to add work. The audit's purpose is to verify what was built, not to expand it. Findings that propose new capability ("we should also add X") are rejected as out of scope unless they address a threat or QC property already on the board.

The polished documentation does not add information not produced in prior phases. Phase 5 reconciles, reorganizes, and removes redundancy. It does not invent.

When the build is complete and the audit clears, the Mac section is born public. Subsequent revisions land in their own commits per the project commit template. The first commit log entry for `mac/` records the build sequence as complete and the harness as operational.
