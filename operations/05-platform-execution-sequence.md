# Post-Mac 5 — Execute Jetson and Windows platform phases

<role>
You are orchestrating the execution of the Jetson and Windows platform phase sequences against their respective hardware. Each platform's phase prompts already exist at `jetson/prompts/` and `windows/prompts/`. Operations 1 through 4 closed out the Mac build, propagated Mac learnings into the platform scaffolds, and rebuilt the operational `~/.claude/`. Now the platform builds execute on real hardware.

You are not authoring new prompts. You are running the existing platform prompts in order, on the correct machine, capturing the outputs, and committing the results back to the public repo.

This prompt runs once per platform (twice total: once on Jetson, once on Windows). It is the operator's runbook, not a phase prompt itself.
</role>

<effort>xhigh during the phase prompt executions; the orchestration shell itself is low effort</effort>

<mode>follow the mode each invoked phase prompt specifies. The orchestration runs in default mode.</mode>

<thinking>adaptive</thinking>

<context_budget>Run /context at the start of each phase invocation and at the end. Each platform's sequence accumulates ~7 distinct phase outputs. The cumulative cache load reaches the same scale as the Mac build did.</context_budget>

<parallel_tool_calls>Phase prompts handle their own parallelism. The orchestration is sequential by design.</parallel_tool_calls>

<scope>
Apply to:
- The target platform's section (`jetson/` or `windows/`) — writes per each invoked phase prompt's scope
- `phase-outputs/` — phase outputs accumulate per phase
- The public repo's git state — commits and pushes after each phase

Do not modify the other platform's section. Do not modify Mac. Do not modify foundation or research.
</scope>

## What to do

Execute the seven phases in order. Each phase is its own Claude Code session against the platform's working directory. Commit each phase's output before the next phase starts.

### Pre-orchestration setup (Rock-side, not Claude-side)

Before running any phase on a target platform:

1. Clone the harness-engineering repo to the target machine at the working directory recorded in `<platform>/ARCHITECTURE.md`.
2. Pull the latest from origin/main on the target machine.
3. Open a Claude Code session at the working directory.
4. Run `bash scripts/drift-check.sh` to confirm clean state pre-execution.

The orchestration begins after these are confirmed.

### The seven-phase sequence

For each platform, in order:

**Phase pre-flight**: feed `<platform>/prompts/01-pre-flight.md` to Claude Code. Verify the deliverable (`phase-outputs/PREFLIGHT.md`). Commit with the standard template message ("phase pre-flight: pre-flight verification on <platform>") and push.

**Phase 0**: feed `<platform>/prompts/phase-0-goals.md`. Verify (`<platform>/ARCHITECTURE.md` filled, `phase-outputs/PHASE-0-DECISIONS.md` recorded). Commit and push.

**Phase 1**: feed `<platform>/prompts/phase-1-discovery.md`. Verify (`phase-outputs/INVENTORY.md`, `phase-outputs/CONFLICTS.md`). Commit and push.

**Phase 2**: feed `<platform>/prompts/phase-2-architecture.md`. The architecture interview runs. Rock answers questions. Verify (`phase-outputs/QUESTIONS.md`, `phase-outputs/ANSWERS.md`). Commit and push.

**Phase 3**: feed `<platform>/prompts/phase-3-deterministic-layer.md`. The deterministic layer lands. Verify (`<platform>/harness/hooks/`, `<platform>/harness/rules/`, `<platform>/harness/settings.json`, `phase-outputs/PHASE-3-NOTES.md`). Commit and push.

**Phase 4**: feed `<platform>/prompts/phase-4-extension-layer.md`. The extension layer lands. Verify (`<platform>/harness/skills/`, `<platform>/harness/agents/`, MCP allowlist in settings.json, `phase-outputs/PHASE-4-NOTES.md`). Commit and push.

**Phase 5**: feed `<platform>/prompts/phase-5-wire-and-document.md`. The Writer/Reviewer pattern runs. Verify (`<platform>/ARCHITECTURE.md` polished, `<platform>/harness/CLAUDE.md` polished, `<platform>/README.md` polished, `phase-outputs/PHASE-5-AUDIT.md` with all blockers resolved). Commit and push.

After Phase 5, the platform section graduates from scaffolded to validated. Update the section's README.md status line accordingly if Phase 5 did not.

### Cross-platform commit hygiene

Each phase produces its own commit. Commits follow the project template (phase/topic, Context, Decision, Why, Tradeoff). Phase outputs (`phase-outputs/`) are gitignored per the existing config; only the platform section's artifact updates land in the commit.

Branch posture: commit to `main` directly. The public repo's audit trail is the commit history, not a feature-branch model.

Push after each commit. The public repo is the canonical record.

### Handling phase failures

If any phase prompt's verification step fails (audit findings unresolved, schema errors, missing deliverables), do not proceed to the next phase. The failure remains the active phase until resolved.

Common failure modes from the Mac execution: Phase 5 audit blockers that the prompt's verification grep depends on missing deliverables (the audit log itself was a blocker on Mac). Phase 3 hook regex bugs that the executing session's verification missed. Treat each platform's Phase 5 audit with the same rigor; expect findings.

### After Windows completes

When both Jetson and Windows have executed cleanly:

1. Verify all three platform sections have their README.md status as "validated."
2. Run drift-check across the full repo. Confirm worst-case-per-session stays under target.
3. Update the root README.md if it carries platform-status language that needs refreshing.
4. The repo is now in its full-build state. Operations 1 through 5 are complete.

<investigate_before_answering>
Before claiming a phase completed, verify the phase prompt's own verification criteria pass. Phase prompts ship with explicit verification commands; run them.

Before committing, verify `git status` and review the diff. Phase outputs that should be gitignored sometimes slip in (`__pycache__/`, build artifacts, editor swap files).

Before pushing, verify the commit message follows the template. Commit hygiene is part of the public-repo audit trail.

Before declaring a platform validated, verify the section's drift-check pass and the audit log's blocker count of zero.
</investigate_before_answering>

## Deliverables

- For Jetson: 7 commits, 1 per phase, all pushed to origin/main
- For Windows: same
- Updated root README.md if platform-status language needed refreshing
- The repo in its full-build state: 3 validated platform sections, foundation unchanged, research unchanged

## Verification

Before reporting complete (per platform):

- `bash scripts/drift-check.sh` returns 0.
- `find <platform> -name 'phase-outputs' -prune -o -name '*.md' -print | xargs grep -l '<TBD'` returns no results.
- `find <platform> -name 'phase-outputs' -prune -o -name '*.md' -print | xargs grep -l '<NEEDS-PORT-VALIDATION>'` returns at most a small number of known-deferred markers (recorded in the platform's README.md "Known gaps" section).
- `grep -c 'Severity: blocker' phase-outputs/PHASE-5-AUDIT.md` returns 0 unresolved.
- `git log --oneline -7` shows 7 phase commits.
- `git status` is clean post-push.

Report the platform name, the commit SHAs, the audit finding counts by severity, and any deferred items.

## Anti-overengineering

This is an orchestration prompt, not a phase prompt. Do not author new phase prompts. Do not modify existing platform phase prompts. Do not invent new platform sections.

If a phase execution produces unexpected gaps (a tool the platform's seed evaluation rejected unexpectedly, a hook semantic that differs from Mac in ways the cross-pollination did not anticipate), record the finding in `phase-outputs/POST-MAC-5-NOTES.md` for the next revision cycle. Do not redesign the platform section mid-execution.

If both Jetson and Windows execution surfaces the same gap in the platform-section prompts (a missed deliverable, an ambiguous instruction, a verification command that doesn't work on either non-Mac platform), the gap is in the scaffold and lands as a Mac-side revision after both platforms are done. Do not fix the prompts on the fly during execution.

After Operations 1 through 5 are complete, the build sequence is done. Further changes flow through the continuous-revision model in `CHECKPOINT.md`, not through new phase prompts.
