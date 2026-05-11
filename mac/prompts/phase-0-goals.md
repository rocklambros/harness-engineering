# Phase 0 — Goals and Architecture

<role>
You are setting the goals for the Mac harness build and filling the platform-specific blocks in `mac/ARCHITECTURE.md`. Phase 0 records the version pins, the model and effort defaults, the sandbox posture, the persistence configuration, and the next-evaluation triggers. You make calibrated decisions and document the rationale. You do not write hooks, deny rules, skills, or agents here. Those are Phase 3 and Phase 4 deliverables.

Phase 0 is the moment to record what the environment actually is, in writing, so every subsequent phase has a stable reference. The `<TBD-PHASE-0>` blocks in `mac/ARCHITECTURE.md` are the explicit set of decisions Phase 0 owns.
</role>

<effort>xhigh</effort>

<mode>plan mode at start to read and reason. Switch to default mode only to write the updated `mac/ARCHITECTURE.md`. No other files change in Phase 0.</mode>

<thinking>adaptive</thinking>

<context_budget>Run /context at start and end. Phase 0 reads several foundation documents and the architecture reference; expect a meaningful cache prefill. Record the start and end context state in `phase-outputs/PHASE-0-CONTEXT.md`.</context_budget>

<parallel_tool_calls>
Read the foundation documents in parallel: `foundation/00-quality-contract.md`, `foundation/01-threat-model.md`, `foundation/02-architectural-principles.md`, `foundation/03-seed-evaluation-methodology.md`, `foundation/04-research-references.md`. Read `mac/README.md`, `mac/ARCHITECTURE.md`, `mac/harness/CLAUDE.md`, and `mac/harness/settings.json.template` in parallel. These reads are independent.
</parallel_tool_calls>

<scope>
Apply only to:
- `mac/ARCHITECTURE.md` (writes: fills `<TBD-PHASE-0>` blocks)
- `phase-outputs/PHASE-0-CONTEXT.md` (writes: the context-budget record)
- `phase-outputs/PHASE-0-DECISIONS.md` (writes: the rationale log)

Do not modify any file in `foundation/`, `research/`, `mac/prompts/`, `mac/harness/` (except as scoped), `mac/evaluations/`, or `mac/scripts/`. Do not create hooks, skills, agents, or deny rules. Do not pre-write Phase 1 inventory content.
</scope>

## What to do

Read the foundation documents and `mac/ARCHITECTURE.md`. For each `<TBD-PHASE-0>` block in `mac/ARCHITECTURE.md`, decide the value or leave it explicitly deferred to a later phase with a recorded reason. The decisions are calibrated, not arbitrary.

The blocks that Phase 0 fills include:

- **macOS version pin**: the exact version this build targets. Read from `sw_vers`.
- **Node and Python versions**: the versions installed; the harness pins to these unless Phase 2 elects to bump.
- **Claude Code version pin**: the minor-version range. If installed Claude Code is `v2.1.88`, the pin is `v2.1.*`. Larger or smaller ranges require a rationale block.
- **Working directory**: confirm `/Users/klambros/harness-engineering/`.
- **Daily-driver harness path**: in-repo (`mac/harness/`) vs symlinked into `~/.claude/`. The choice has cache implications because the cached prefix's stability depends on the file location being stable across sessions.
- **Default model and subagent default**: Opus vs Sonnet. The decision has cost and cache-economy consequences (QC.4a, same-family parent/subagent share cache; cross-family does not).
- **Effort levels**: `xhigh` and `high` are the working pair; record if any deviation.
- **Permission mode default**: `default` per Principle 2 (least privilege) unless a rationale block justifies a different starting point.
- **Auto-mode classifier**: enable or disable. Hughes 2026 reports 0.4% false-positive rate. Disable here is a deliberate choice that the rationale block justifies.
- **Bash sandboxing**: enable on Mac. Record any exclusion patterns. If sandboxing is not yet supported in the installed Claude Code version, record that fact and the deferred-decision rationale.
- **Persistence**: session log location and retention. Read from Claude Code's settings or documentation; if unclear, run a short session and observe.
- **Network egress monitoring**: record whether Little Snitch, LuLu, or equivalent is installed. Not required by the harness, but informs Phase 4's MCP server decisions.

For each block filled, the decision lands in `mac/ARCHITECTURE.md`. The rationale lands in `phase-outputs/PHASE-0-DECISIONS.md`, one short paragraph per decision, citing the foundation document or research source that informs the choice.

For each block deferred, record the reason in `mac/ARCHITECTURE.md` (e.g., "deferred to Phase 2 interview" with a brief reason) and in `phase-outputs/PHASE-0-DECISIONS.md`.

<investigate_before_answering>
Before recording a version pin, run the version command and capture the actual output. Do not assume from memory.

Before recording the Claude Code session log path or sandbox behavior, consult the installed Claude Code's documentation or run a short session to observe. Do not assume.

Before claiming Bash sandboxing is enabled or has specific exclusion patterns, verify against the running Claude Code's settings or behavior.
</investigate_before_answering>

## Deliverables

Three updates and writes:

1. `mac/ARCHITECTURE.md`: every `<TBD-PHASE-0>` block is either filled with a value or replaced with an explicit deferred-with-reason marker. The next-evaluation triggers in the §Version pins table are populated.
2. `phase-outputs/PHASE-0-CONTEXT.md`: the `/context` output at the start and end of this session, with the delta.
3. `phase-outputs/PHASE-0-DECISIONS.md`: one short paragraph per filled block, naming the decision and citing the source.

## Verification

Before reporting complete, run:

- `grep -c '<TBD-PHASE-0>' mac/ARCHITECTURE.md` to confirm no unaddressed blocks remain.
- `bash scripts/drift-check.sh` to confirm the cached prefix is still clean.
- `wc -l mac/ARCHITECTURE.md phase-outputs/PHASE-0-DECISIONS.md` to confirm the files have substantive content.

If any `<TBD-PHASE-0>` block remains in `mac/ARCHITECTURE.md` without an explicit deferred-with-reason marker, the phase is not complete.

Report the line counts of the three artifacts and the drift-check exit code. Do not summarize the architecture document's contents in chat.

## Anti-overengineering

Phase 0 records decisions. It does not implement them. Hooks, deny rules, skills, agents, and MCP server registrations are Phase 3 and Phase 4 deliverables. If a Phase 0 decision implies a hook or skill, record the implication in `phase-outputs/PHASE-0-DECISIONS.md` for Phase 3 or Phase 4 to act on. Do not write the hook or skill here.

The Quality Contract operationalization section of `mac/ARCHITECTURE.md` references tools (Brewfile.lock, syft, detect-secrets, semgrep) that are not yet wired. Phase 0 does not wire them. Phase 3 evaluates them and decides. The architecture document records the *intent*; Phase 3 records the implementation.

When in doubt about scope, defer to Phase 2 or Phase 3 with a recorded reason rather than acting.
