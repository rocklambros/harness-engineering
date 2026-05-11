---
name: seed-evaluation
description: Use when asked whether to adopt a tool, library, plugin, skill collection, agent definition, hook library, or any external project as part of the Claude Code harness. Applies the foundation/03 two-stage methodology (pre-filter then deep-eval), produces a binary integrate / integrate-with-constraints / reject decision, and prevents evaluation theater by rejecting rubric scoring.
---

# Seed Evaluation

## When this fires

The skill activates when the conversation proposes adopting any external project into the harness:

- "Should we add X library / plugin / skill?"
- "I found this repo, can we use it?"
- "Let's evaluate Y as a replacement for Z."
- "Has anyone integrated A with Claude Code?"

The skill does NOT fire for routine tool use of already-adopted dependencies, nor for one-off invocations that do not produce a persistent harness change.

## Two stages

### Stage 1: Pre-filter (target 30 seconds per candidate)

Three questions. Any "no" rejects.

1. **License**: Compatible with this repo's MIT and with the candidate's intended use?
2. **Architecture support**: Works on Mac (Apple Silicon), Jetson AGX Orin (ARM64 Linux), and Windows (x86_64)? Where it does not, is the gap acceptable for this component, or is a per-platform equivalent required?
3. **Maintainership**: Commit in the last 90 days, and issue tracker shows real responses?

Output: one sentence of rationale per rejected candidate. Survivors move to Stage 2.

The 30-second target is real. If pre-filter on a candidate takes 10 minutes, the question framing is failing. Tighten the question, not the time budget.

### Stage 2: Deep evaluation (integration, not scoring)

Survivors get wired into a sandboxed session and exercised against three workloads:

1. **Nominal task**: A task the candidate is supposed to do well. Measures expected-case quality.
2. **Edge case**: A task that exercises the failure mode the threat model worries about. Measures resilience.
3. **No-op interaction**: The cost of having the candidate installed and idle. Measures cache footprint, startup latency, tool pool inflation.

Output per candidate in `mac/evaluations/deep-eval.md`:

```
### <candidate>
Stage 2 entry: Phase <N>
Date evaluated: YYYY-MM-DD
Decision: integrate / integrate-with-constraints / reject

Nominal task: <one paragraph>
Edge case: <one paragraph>
No-op cost: <one paragraph>

Constraints (if integrate-with-constraints):
- <constraint, with the hook or deny rule that enforces it>

Rationale: <one paragraph naming the failure mode prevented and the alternatives rejected>

Drift trigger: <upstream major version | security advisory | periodic review>
Version pin: <semver>
```

## What is not in the methodology

**No rubric scoring.** Rubric scoring on harness seeds is mostly noise. The qualities that matter (cache behavior, interaction with the permission system, prompt injection resilience, drift over upgrades) do not score cleanly on a 1-to-5 scale.

**No exhaustive matrix.** A 15-column matrix comparing 20 seeds across every dimension is the visible artifact of evaluation theater. The output is a short narrative per survivor.

**No vendor pitch trust.** A vendor's claim that their product "works with Claude Code" is data, not evidence. Stage 2 integration is the evidence.

## When the decision is ambiguous

Prefer rejection. The post-launch revision cadence is the appeal mechanism for rejected candidates. A rejected candidate can come back when the signals change. An adopted candidate that turns out wrong costs revisions to remove.

## Adoption produces three artifacts (same commit)

1. The wiring change (config, MCP server registration, skill copy, hook script).
2. The rationale: commit message under "Why" or in the phase output. Names the failure mode the seed prevents and the alternative seeds rejected.
3. The drift trigger: line in `mac/ARCHITECTURE.md` (and equivalents) recording the seed's version pin and the next re-evaluation trigger.

Adoption is the start of a maintenance commitment, not the end of an evaluation.

## Related artifacts

- Foundation: `foundation/03-seed-evaluation-methodology.md` (the authoritative methodology)
- Foundation: `foundation/02-architectural-principles.md` Principle 4 (stress every component against the current model)
- Worksheet: `mac/evaluations/pre-filter.md` (Stage 1 log)
- Worksheet: `mac/evaluations/deep-eval.md` (Stage 2 log)
- Related skill: `mcp-server-pre-trust-audit` (the same discipline applied specifically to MCP servers)
- Owner: harness-engineering (Phase 4, 2026-05-11)
