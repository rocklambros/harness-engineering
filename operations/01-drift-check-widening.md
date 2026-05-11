# Post-Mac 1 — Verify and widen drift-check to include user-level CLAUDE.md hierarchy

<role>
You are closing out a deliverable that Phase 2 Q10 elected but no phase prompt explicitly named: widening `scripts/drift-check.sh` so the worst-case-per-session calculation includes the user-level `~/.claude/CLAUDE.md` and its `@import` chain. Phase 5 audit did not flag this as a missed deliverable. Either Phase 3 quietly handled it, or it sat in the same implied-but-not-named bucket as JOURNEY. Your job is to verify which, and to land the widening if it has not landed.
</role>

<effort>high</effort>

<mode>plan mode to read and verify. Switch to default mode only if the widening is needed.</mode>

<thinking>adaptive</thinking>

<context_budget>Run /context at start and end. Phase reads two files (the current drift-check script and `phase-outputs/ANSWERS.md`) plus a small probe of `~/.claude/CLAUDE.md`. Cache load is light. Record state in `phase-outputs/POST-MAC-1-CONTEXT.md`.</context_budget>

<parallel_tool_calls>Read `scripts/drift-check.sh`, `phase-outputs/ANSWERS.md` Q10 section, and `~/.claude/CLAUDE.md` in parallel at start.</parallel_tool_calls>

<scope>
Apply only to:
- `scripts/drift-check.sh` (writes only if widening needed)
- `phase-outputs/POST-MAC-1-CONTEXT.md` (writes)
- `phase-outputs/POST-MAC-1-NOTES.md` (writes: verification outcome and any changes made)

Do not modify any other file. The widening either lands here or it does not; no adjacent edits.
</scope>

## What to do

Read `scripts/drift-check.sh`. Determine whether it already walks the user-level CLAUDE.md and its `@import` chain into the worst-case-per-session sum. The current expectation per Phase 2 Q10: combined worst-case = root project CLAUDE.md + max(platform harness CLAUDE.md) + user-level `~/.claude/CLAUDE.md` + transitive `@import` chain from user-level.

Three possible outcomes:

1. **Already widened**: drift-check.sh contains logic that reads `~/.claude/CLAUDE.md` and walks its `@import` chain. Verify the implementation matches the Q10 directive. Run the script and confirm the reported numbers include the user-level. Record outcome.

2. **Partially widened**: script reads `~/.claude/CLAUDE.md` line count but does not resolve `@import` transitively. Complete the widening. Add transitive `@import` resolution (parse `@<path>` lines from the user-level file, follow each, sum lines, recurse).

3. **Not widened**: script is still project-only. Implement the full widening.

Whatever you find, document it in `phase-outputs/POST-MAC-1-NOTES.md` with the evidence (line number references in drift-check.sh) and the action taken.

<investigate_before_answering>
Before claiming the script is already widened, read its actual contents and run it. Memory of what I told Rock the script does is not evidence of what's on disk.

Before implementing transitive `@import` resolution, read at least three lines of `~/.claude/CLAUDE.md` to confirm the `@import` syntax matches expectations. Different versions of Claude Code have used slightly different import directives.

Before recording the widening as complete, run the script and capture the output. The output's per-session breakdown should now show a user-level line.
</investigate_before_answering>

## Implementation guidance if widening is needed

The current script computes worst-case per platform as `root + platform_lines + harness_lines`. Extend the formula to `root + platform_lines + harness_lines + user_level_total`, where `user_level_total` is `lines(~/.claude/CLAUDE.md) + sum(lines of every transitively imported file)`.

Transitive `@import` resolution: parse each line for `@<path>` markers. Resolve relative paths against the importing file's directory. Read the imported file. Recurse. Cycle detection: keep a visited set; skip already-visited paths.

Bash shellcheck-clean. Same shebang and error handling as the current script.

Optionally: print the user-level chain as part of the per-platform session breakdown, so the WARN and FAIL outputs name which user-level files contributed.

## Deliverables

- `scripts/drift-check.sh`: widened if needed, untouched if already widened
- `phase-outputs/POST-MAC-1-NOTES.md`: verification outcome with evidence and action taken
- `phase-outputs/POST-MAC-1-CONTEXT.md`: context-budget record

## Verification

Before reporting complete:

- `bash scripts/drift-check.sh` returns 0 and the output includes a user-level component in the per-session breakdown.
- The reported worst-case-per-session number includes the user-level lines (verifiable by manually summing `wc -l ~/.claude/CLAUDE.md` plus the project numbers).
- Shellcheck clean on the modified script.
- `chmod +x scripts/drift-check.sh` if the rewrite reset mode bits.

Report the script's modification status, the new worst-case-per-session number, and whether it falls under the 250 target or between target and 400 cap.

## Anti-overengineering

This is a focused completion of a Phase 2 commitment, not a redesign of drift-check. Do not add new check classes. Do not refactor the existing logic. Do not extend the poison-pattern regex set. Just close the widening commitment.

If the script is already widened and working, leave it alone. The note documenting that finding is the deliverable.
