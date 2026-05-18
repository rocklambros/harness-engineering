---
name: writer-reviewer
description: The two-agent documentation pattern used by Phase 5. The Writer (main session) produces documentation, the Reviewer subagent audits it against the Quality Contract and SSDF practices, and the pair iterates until the Reviewer signs off or three iterations elapse. This file documents the pattern so Phase 5 can invoke it. It does not duplicate the Reviewer, which is defined in reviewer.md.
isolation: in-process
permissionMode: plan
---

# Writer/Reviewer Pattern

## Purpose

Phase 5 produces the polished documentation set. Documentation that states a security or architecture claim is worth less if nothing checks the claim. This pattern pairs a Writer with a Reviewer so every Phase 5 artifact is audited against the Quality Contract before it lands.

This file is the pattern definition. The Reviewer agent itself is defined in `reviewer.md` in this directory. This file says how the two interact. It does not restate the Reviewer's checks.

## Roles

The Writer is the main session. It produces the Phase 5 artifacts: the polished `mac/ARCHITECTURE.md`, the updated `mac/harness/CLAUDE.md`, and the other documentation Phase 5 names. The Writer holds the full build context.

The Reviewer is the subagent defined in `reviewer.md`. It reads every changed file and audits against the Quality Contract (`foundation/00-quality-contract.md`), the threat model (`foundation/01-threat-model.md`), and the architectural principles (`foundation/02-architectural-principles.md`). It reports findings with severity and evidence. It does not edit.

## The loop

1. The Writer produces or revises the Phase 5 artifacts.
2. The Writer spawns the Reviewer (`reviewer.md`) on the changed set.
3. The Reviewer returns a finding list and a recommendation.
4. The Writer resolves every BLOCKER and HIGH finding.
5. Repeat from step 1 until the Reviewer recommends READY, or three iterations have elapsed.
6. If three iterations elapse with open BLOCKER findings, the Writer stops and surfaces the disagreement to the human. The loop does not get bypassed by attrition.

## Cache lineage

Writer and Reviewer are both Opus 4.7, same family, so they share cache per QC.4a. The Reviewer reads a Phase-5-sized batch, which is where same-family cache economy pays for the Opus cost over a Haiku reviewer. Cross-family review would lose the cache and is not used here.

## Termination and honesty

The loop terminates on Reviewer sign-off or three iterations. It does not terminate because the Writer prefers to ship. An open BLOCKER after three iterations is a human decision, recorded in the Phase 5 commit, not silently resolved. This is the same anti-attrition rule the Reviewer enforces from its side in `reviewer.md`.
