# Post-Mac 9 — Build closeout: CHECKPOINT refresh, cross-doc consistency, behavioral verification protocol

## Operational preconditions (read before invoking)

Open a fresh Claude Code session. Run from `/Users/klambros/harness-engineering/` as the working directory. Operations 06 (README), 07 (HARNESS_GUIDE), and 08 (JOURNEY) have all committed. This prompt closes out the Mac build.

This prompt does three small things: refreshes CHECKPOINT.md (gitignored, local only), runs a consistency check across the three documentation deliverables, and writes the behavioral verification runbook Rock executes separately in a fresh Claude Code session against a test project.

<role>
You are closing out the Mac build. The structural artifacts are committed. The documentation set is committed. What remains is three administrative deliverables: an internal state refresh, a consistency audit, and a runbook Rock follows to behaviorally verify the rebuilt `~/.claude/`.

Voice: pragmatic. The runbook is procedural. The consistency findings are factual. The CHECKPOINT refresh is a structured update. Rock's writing rules apply throughout: no em dashes, no semicolons, no sentences starting with conjunctions, no AI filler, no corporate slop.
</role>

<effort>high</effort>

<mode>default mode (writes).</mode>

<thinking>adaptive</thinking>

<context_budget>Run /context at start and end. Phase reads the three documentation deliverables, CHECKPOINT, and the relevant phase outputs. Cache load is moderate. Record state in `phase-outputs/POST-MAC-9-CONTEXT.md`.</context_budget>

<parallel_tool_calls>
Initial parallel read: `CHECKPOINT.md`, `README.md`, `HARNESS_GUIDE.md`, `JOURNEY.ipynb`, `foundation/00-quality-contract.md`, `foundation/01-threat-model.md`, `mac/ARCHITECTURE.md`, `mac/harness/CLAUDE.md`, `mac/harness/settings.json`, `phase-outputs/PHASE-5-AUDIT.md`, `phase-outputs/POST-MAC-4-VERIFICATION.md`.
</parallel_tool_calls>

<scope>
Apply only to:
- `CHECKPOINT.md` (writes; gitignored, no commit)
- `phase-outputs/POST-MAC-9-CONTEXT.md` (writes)
- `phase-outputs/POST-MAC-9-NOTES.md` (writes: consistency findings and any fixes applied)
- `phase-outputs/POST-MAC-9-VERIFICATION-PROTOCOL.md` (writes: the runbook Rock executes)
- README.md, HARNESS_GUIDE.md, JOURNEY.ipynb (writes; only if the consistency check finds drift that needs fixing)

Do not modify any other file. Do not modify any file in `mac/harness/`, `jetson/`, `windows/`, `foundation/`, `research/`, `scripts/`, or `operations/`.
</scope>

## What to do

Three stages. Each is independent of the others; if Stage 2 finds drift it commits a fix; Stage 1 and Stage 3 do not produce commits to public files.

### Stage 1: Refresh CHECKPOINT.md

`CHECKPOINT.md` is gitignored; no commit. The update reflects post-build, post-rebuild, post-documentation-closeout state.

Read the current CHECKPOINT. Rewrite the sections that have drifted:

- **Build state.** Mac is "validated, rebuilt, documented, operating." Operations 01, 03, 04 complete. Operation 02 (original JOURNEY-update) deprecated and superseded by Operation 08 (deep JOURNEY rewrite). Operations 06-09 (documentation closeout) complete. Operation 05 (platform execution for Jetson and Windows) deferred to per-platform timing Rock handles separately.

- **Jetson and Windows state.** "Scaffolded with Mac cross-pollination applied (Operation 03), awaiting platform execution per `operations/05-platform-execution-sequence.md` runbook."

- **Documentation state.** README.md rewritten as 180-250 line front door (Operation 06). HARNESS_GUIDE.md authored as 1500-2500 line user manual (Operation 07). JOURNEY.ipynb deep-rewritten as 42-58 cell educational narrative (Operation 08). Repo is in its public-facing documented state.

- **Open items.** Jetson and Windows phase execution. Ongoing operational use generating revision items. Residual-risk findings F09, F10, F11 carrying post-launch reconsideration triggers. Behavioral verification of rebuilt `~/.claude/` pending (the protocol from this operation; Rock executes separately).

- **Build sequence completed.** Add a subsection naming the dates phases ran and operations landed, derived from the commit log.

Keep the locked decisions section as-is unless an actual decision has changed.

### Stage 2: Cross-document consistency check

Audit README, HARNESS_GUIDE, and JOURNEY for internal consistency. Record findings in `phase-outputs/POST-MAC-9-NOTES.md` under §Consistency Audit. Any drift found gets fixed in the relevant document with a small targeted commit.

Specific consistency checks:

- **Links resolve.** Every link from README to HARNESS_GUIDE, JOURNEY, foundation/, mac/, research/, or operations/ resolves to an existing file or section.
- **Mac state claim is consistent.** README, HARNESS_GUIDE, and JOURNEY all describe the Mac side as validated, rebuilt, operating. No document claims a state that does not match `phase-outputs/POST-MAC-4-VERIFICATION.md`.
- **Jetson and Windows state claim is consistent.** All three documents describe them as scaffolded with Mac cross-pollination applied. No document claims they are validated.
- **Quality Contract.** The five properties (QC.1 Security, QC.2 Tight code, QC.3 Comment the why, QC.4a Cache discipline, QC.4b Context window discipline, QC.5 Versioning) are described identically across README's brief mention, HARNESS_GUIDE's §7, foundation/00, and JOURNEY's epilogue. No drift in property names or counts.
- **Threat model.** The six threats (T1 prompt injection, T2 supply chain, T3 pre-trust initialization, T4 sub-command chain bypass, T5 cache poisoning, T6 hostile MCP server) are described identically across HARNESS_GUIDE's §8 and foundation/01. No drift.
- **Five layers.** HARNESS_GUIDE's §3 (the five layers) is consistent with §4 (file-by-file). Every file in §4 is positioned in one of the five layers from §3. No file is uncategorized.
- **Citation accuracy.** Spot-check 10 random citations across HARNESS_GUIDE and JOURNEY. Each cited path exists. Each cited section contains the claimed content.
- **Numeric claims.** Spot-check 5 random numeric claims (file counts, line counts, token counts, finding counts). Each matches the phase output that recorded it.
- **Voice consistency.** README is pragmatic, HARNESS_GUIDE is educational, JOURNEY is first-person. No drift between sections within a single document.

For each finding, record:

- The document and section
- The specific claim or link
- The actual state
- The disposition (fix-now or note-for-revision)

Fix-now findings get a small commit per document. The commit message follows the project template with §Drift specifically named.

### Stage 3: Author the behavioral verification protocol

Write `phase-outputs/POST-MAC-9-VERIFICATION-PROTOCOL.md` as a self-contained runbook Rock executes in a separate fresh Claude Code session against any test project (NOT the harness-engineering repo). The protocol verifies that the rebuilt `~/.claude/` actually works as designed, not just that it parses on disk.

The runbook covers:

**Pre-test setup.** Open a fresh Claude Code session in any test project directory. Confirm the session loads the rebuilt `~/.claude/`: run `/context` and verify the user-level CLAUDE.md hierarchy matches what `bash /Users/klambros/harness-engineering/scripts/drift-check.sh` reports for user-level. If they differ, the rebuild did not load as expected; surface for investigation before continuing tests.

**Test 1: Deny rule enforcement.** Try commands that should be blocked. Suggested test cases:

- `git push --force` (should be blocked by `bash-deny-git-push-force`)
- `sudo ls` (should be blocked by `bash-deny-sudo`)
- A bash invocation containing the literal `--dangerously-skip-permissions` flag (should be blocked or the flag absent from settings entirely)
- A write to a path matching `*.env` or `.env.*` (should be blocked or prompted)

For each: try the command in the test session, record the outcome (blocked, prompted, allowed-when-shouldnt-be), capture the exact error message.

**Test 2: PreToolUse hook enforcement.** Try commands that should fire a hook:

- Bash with 31+ subcommands chained by `&&` (should be blocked by `cap-subcommands`)
- `npx -y create-react-app demo` (unpinned, should fire supply-chain hook to ask)
- `npx -y create-react-app@5.0.1 demo` (pinned, should pass silently per the F04/F05 fix)
- `uvx --from git+https://github.com/example/repo.git@abc1234 example` (pinned, should pass)
- `uvx --from git+https://github.com/example/repo.git example` (unpinned, should ask)
- Write outside cwd to a non-allowlisted directory (should fire external-write-gate)

For each: record outcome.

**Test 3: SessionStart hook execution.** Open a fresh session in a directory containing a `.claude/settings.json` or `.mcp.json` not in the audited-hashes registry. Confirm the SessionStart hook fires and either blocks or requests acknowledgment.

**Test 4: Skills load.** Trigger the `mcp-server-pre-trust-audit` skill (e.g., ask the session to "audit this MCP server before I trust it"). Confirm the skill activates and produces its documented audit output. Same for `seed-evaluation`.

**Test 5: Auto-mode classifier behavior.** Run a few ordinary Bash invocations and confirm the auto-mode classifier behaves per Q1's enabled-with-tightened-denies posture:

- Read-only commands (`ls`, `cat`, `grep` on files inside cwd) should pass without prompt.
- Write commands inside cwd should pass.
- Write commands outside cwd should prompt.
- Commands matching deny rules should block regardless of auto-mode.

**Outcomes capture.** For each test, record in a new file Rock creates from this protocol's outputs (`phase-outputs/POST-MAC-9-VERIFICATION.md`):

- What was tried
- Expected behavior
- Observed behavior
- Pass / fail
- Any error messages or unexpected behavior

**On any failure.** If any test fails, do not silently fix it. Record the failure, document the gap, decide whether the gap is a revision item (lands in post-launch revisions) or a stop-the-world item (the rebuild is broken and needs immediate attention).

This runbook is written for Rock to execute manually in a separate session. This operation does not run Test 1 through Test 5 itself; it produces the protocol document. The actual testing happens after this operation completes.

<investigate_before_answering>
Before Stage 1 claims "Mac is validated, rebuilt, documented, operating," verify Operations 04 (rebuild), 06 (README), 07 (HARNESS_GUIDE), and 08 (JOURNEY) have all committed. The CHECKPOINT should not advertise a state that's not on disk.

Before Stage 2 reports a consistency finding as fixed, re-read the modified section and confirm the fix actually resolved the drift. A claim of "fixed" without verification is itself a consistency violation.

Before Stage 3 names a specific test case, verify the underlying hook or deny rule exists. Recommending a test for a rule that does not exist is worse than skipping the test.
</investigate_before_answering>

## Deliverables

- `CHECKPOINT.md`: refreshed to reflect post-closeout state (gitignored, no commit)
- `phase-outputs/POST-MAC-9-CONTEXT.md`: context-budget record
- `phase-outputs/POST-MAC-9-NOTES.md`: consistency audit findings, fixes applied
- `phase-outputs/POST-MAC-9-VERIFICATION-PROTOCOL.md`: behavioral verification runbook
- Zero, one, or more small commits fixing drift found in Stage 2 (only if drift was found)

## Verification

Before reporting complete:

- `CHECKPOINT.md` reflects all four completed closeout operations.
- `phase-outputs/POST-MAC-9-VERIFICATION-PROTOCOL.md` exists and contains five tests with concrete commands.
- Consistency audit found and fixed (or noted) every drift item. Zero unresolved fix-now findings.
- `bash scripts/drift-check.sh` returns 0 or WARN.
- If commits were made: `git status` is clean post-push.

Report: consistency findings count by disposition (fixed / noted), commits made, the path to the verification protocol, and any items deferred to post-launch revision.

## Commit (only if Stage 2 found drift)

If consistency check found drift that needed fixing, per-document commits follow the project template. Example for a README drift fix:

```
docs: fix README link drift caught by Operation 09 consistency audit

Context: Operation 09 cross-document consistency check found <specific drift>.

Decision: <specific fix>.

Why: Drift between documents undermines reader trust.

Tradeoff: None; this is a correctness fix.
```

If Stage 2 found no drift, no commit. Note the clean audit in NOTES.

## Anti-overengineering

Do not relitigate decisions during consistency checks. If README and HARNESS_GUIDE describe a locked decision differently, the fix is to align them with the locked decision in CHECKPOINT and foundation, not to change the decision.

Do not run the behavioral tests yourself. The runbook is the deliverable. Rock executes it in a separate session against a separate project; outcomes flow back to a new file Rock writes.

Do not modify locked-decision artifacts. CHECKPOINT updates the state section, not the locked decisions section. README, HARNESS_GUIDE, and JOURNEY reflect locked decisions; they do not relitigate them.

If Stage 2 finds a class of drift that needs more than a small targeted fix (e.g., HARNESS_GUIDE's §4 describes a hook that does not exist in mac/harness/hooks/), do not paper over it. Surface as a finding in NOTES and ask Rock for direction. Documentation that describes a state not on disk is the worst kind of documentation drift.

If during Stage 3 you find that one of the suggested tests cannot be expressed cleanly (the hook does not exist, the deny rule does not match the pattern shown, etc.), do not invent a test that masks the gap. Record the gap in NOTES and omit the test from the runbook. Better to ship a five-test protocol that all work than a six-test protocol where one is broken.

After this operation completes, the original build sequence is done. Operations 06-09 were the documentation closeout; everything after is post-launch revision per the continuous operating model in CHECKPOINT.md.
