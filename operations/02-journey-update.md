# Post-Mac 2 — Update JOURNEY.ipynb with the Mac build narrative

<role>
You are updating `JOURNEY.ipynb` to reflect the Mac build that just executed. The notebook is the narrative companion to the structural documentation. It sat at "not yet started" through Phase 0 to Phase 5 because no phase prompt named it as a deliverable. Now the build is done and the notebook needs to catch up.

Voice: first-person, Rock's exec voice, his writing rules. No em dashes, no semicolons, no sentences starting with conjunctions, no AI filler, no corporate slop. The notebook is external-facing material per Rock's directive on prose cleanup.

You are drafting, not finalizing. Rock will review each cell and correct in his own voice. The Mac build's surprises and tradeoffs are most accurate when Rock confirms which ones actually surprised him.
</role>

<effort>xhigh</effort>

<mode>default mode (writes JOURNEY.ipynb).</mode>

<thinking>adaptive</thinking>

<context_budget>Run /context at start and end. Phase reads the entire `phase-outputs/` directory, the polished mac/ artifacts, and the current JOURNEY.ipynb. Cache load is non-trivial because the audit log is rich source material. Record state in `phase-outputs/POST-MAC-2-CONTEXT.md`.</context_budget>

<parallel_tool_calls>
Read in parallel at start: `JOURNEY.ipynb`, `phase-outputs/PREFLIGHT.md`, `phase-outputs/PHASE-0-DECISIONS.md`, `phase-outputs/INVENTORY.md`, `phase-outputs/CONFLICTS.md`, `phase-outputs/QUESTIONS.md`, `phase-outputs/ANSWERS.md`, `phase-outputs/PHASE-3-NOTES.md`, `phase-outputs/PHASE-4-NOTES.md`, `phase-outputs/PHASE-5-AUDIT.md`, `mac/README.md`, `mac/ARCHITECTURE.md`, `mac/harness/CLAUDE.md`.
</parallel_tool_calls>

<scope>
Apply only to:
- `JOURNEY.ipynb` (writes)
- `phase-outputs/POST-MAC-2-CONTEXT.md` (writes)
- `phase-outputs/POST-MAC-2-NOTES.md` (writes: what went into JOURNEY and what was left to Rock to fill)

Do not modify any other file. JOURNEY is the only artifact.
</scope>

## What to do

The notebook has nine cells before this update:

1. Markdown — the JOURNEY header (keep, no change)
2. Markdown — Pre-flight, status complete (keep, no change)
3. Markdown — Phase 0, status not yet started (REPLACE)
4. Markdown — Phase 1, status not yet started (REPLACE)
5. Markdown — Phase 2, status not yet started (REPLACE)
6. Markdown — Phase 3, status not yet started (REPLACE)
7. Markdown — Phase 4, status not yet started (REPLACE)
8. Markdown — Phase 5, status not yet started (REPLACE)
9. Markdown — Verification cell header (keep)
10-12. Code — three verification commands (UPDATE: the first is now redundant with drift-check; the second is still right; the third stays)
13. Markdown — Post-launch revisions (keep, no change)

For each phase cell, the template from the Pre-flight cell prescribes the shape:

- **What I did**: one paragraph naming the concrete output of the phase. Pull from the phase output files and the mac/ artifacts.
- **Surprises**: one paragraph naming what the executing session encountered that the prompt did not anticipate. This is where the audit findings, the Phase 2 question reframings, and the regex bugs live.
- **Tradeoffs that mattered**: one paragraph naming the decisions that turned on a tradeoff, not the decisions that were obvious. The auto-mode-classifier choice, the subcommand cap at 30, the `~/.claude/` rebuild option-4 decision, the Opus-subagent cache-economy choice all qualify.
- **What I would do differently**: one paragraph. This is the most useful cell for future readers. Pull from PHASE-5-AUDIT findings that became "fix now" and from the prompt-authoring inconsistency PHASE-0-DECISIONS surfaced.

Where Rock's perspective is needed and the phase outputs don't carry it directly, leave a `<!-- ROCK: confirm or rewrite -->` marker inline rather than inventing. Examples of where to leave markers: subjective surprise reactions, retrospective regrets, judgments on specific tool quality.

<investigate_before_answering>
Before claiming a specific phase produced a specific artifact, read the phase output file directly. The audit log records findings but the synthesis lives in the artifact files.

Before recording a "surprise," cite the specific file and line where the surprise is documented. Surprises pulled from your own assumptions are not evidence.

Before writing "what I would do differently," tie each item to a specific Phase 5 audit finding or PHASE-0-DECISIONS scope inconsistency. Speculation without an audit trail does not belong in JOURNEY.
</investigate_before_answering>

## Specific content per phase cell

**Phase 0**: macOS version pin recorded, Claude Code v2.1.138 pinned to v2.1.*, the third CLAUDE.md (user-level `~/.claude/CLAUDE.md`) participates automatically per Claude Code's hierarchy walk. The SuperClaude framework files added ~16.6k tokens at user level — surprise that the user-level load was 5.7x larger than the project CLAUDE.md. Tradeoff that mattered: Opus 4.7 as both main session and default subagent for cache-lineage reasons. The prompt-authoring inconsistency caught by PHASE-0-DECISIONS (settings.json.template TBD-PHASE-0 markers out of Phase 0's scope) belongs in "what I would do differently."

**Phase 1**: 44 in-repo `.claude/` directories found across the machine, plus the plaintext Hetzner API token in `~/.claude/mcp.json` (HIGH-severity), the 4311 accumulated session logs (oldest 60+ days), the 16-plugin enabledPlugins list. Surprise: the audit backlog was large enough that Q5 cadence "every clone hash-gated" became materially more expensive than expected. Tradeoff: pre-trust audit cadence vs. operational friction.

**Phase 2**: 11 calibrated questions, interview reframed by Rock on Q3 (rebuild entire `~/.claude/`, beyond the three planned options) and Q2a (asked for balance recommendation rather than picking blind). Surprise: the question-set framing on Q3 was too narrow — the right framing surfaced through Rock's clarification rather than through the prompt. Tradeoff: auto-mode classifier enabled (Q1) traded the 0.4% false-positive rate for daily-driver friction reduction.

**Phase 3**: 6 Python hooks + 6 deny rules + populated settings.json. Surprise: hook-script execution latency on the MCP-server-prefix audit added detectable friction; the PreToolUse subcommand cap at 30 (Q6) flagged itself within hours of activation when normal grep-and-pipe work exceeded it. Tradeoff: 30-subcommand cap vs. defensive 50-cap-as-floor with hook flagging. Real bug surfaced by Phase 5 audit: the supply-chain hook regex was structurally broken (F04, F05) — pinned `uvx --from git+...@<ref>` and pinned `npx -y <pkg>@<version>` both false-positived.

**Phase 4**: 2 skills (`mcp-server-pre-trust-audit`, `seed-evaluation`), 2 agents (`inventory.md`, `reviewer.md`). Surprise: the count was much smaller than seed pre-filter suggested would survive. Superpowers v5.1.0 ships 14 skills + 1 hook + 0 agents (not the 17/4/1 Phase 1 INVENTORY claimed — F08). Tradeoff: lean adoption now with documented swap-in path vs. broader adoption with more cache-prefix footprint.

**Phase 5**: 13 findings, 1 blocker (the audit log itself was the missing deliverable), 4 majors, 8 minors. 9 fix-now resolutions, 3 accept-residual-risk, 1 accept. The Reviewer subagent pattern caught both regex bugs that Phase 3's own verification missed. The build is "READY with majors recorded," not READY clean. What I would do differently: write the Phase 5 prompt so the audit log is produced as part of the first synthesis stage, not as a separate output that the prompt's own verification grep depends on.

## Verification code cells

Replace the first verification code cell (the raw `find . -name 'CLAUDE.md'` line counter) with `!bash scripts/drift-check.sh`. The widened drift-check produces a more useful per-session breakdown than the raw count.

Keep the second cell (`!bash scripts/drift-check.sh`) — now redundant with the replacement but harmless to run twice. Or remove it; cleaner.

Keep the third cell (`!wc -l foundation/*.md`).

Add a fourth cell that prints the latest commit log entries, scoped to mac/. Useful for readers wanting to see the build sequence on the public repo.

## Deliverables

- `JOURNEY.ipynb`: six phase cells updated, verification cells updated, `<!-- ROCK: confirm or rewrite -->` markers where Rock's voice is needed
- `phase-outputs/POST-MAC-2-NOTES.md`: list of every cell updated, every Rock-marker placed, every audit finding that informed which surprise or tradeoff
- `phase-outputs/POST-MAC-2-CONTEXT.md`: context-budget record

## Verification

Before reporting complete:

- `python -c "import json; json.load(open('JOURNEY.ipynb'))"` parses (notebook is valid JSON).
- `jupyter nbconvert --to script JOURNEY.ipynb` succeeds (notebook is valid nbformat).
- Each of the six phase cells has substantive content: status changed from "not yet started," all four template sections (what I did, surprises, tradeoffs, what I would do differently) filled or marked.
- `grep -c 'ROCK:' JOURNEY.ipynb` returns the count of Rock-markers placed; reported in the notes file.

Report the cell count modified, the Rock-marker count, and the notebook line count.

## Anti-overengineering

Do not invent narrative. Pull from phase outputs. Where Rock's voice or perspective is needed and the phase outputs don't carry it, leave a marker.

Do not rewrite the Pre-flight cell or the JOURNEY header. They are settled.

Do not add new phase cells beyond the six existing ones. The structure is fixed.

Do not produce more than four paragraphs per phase cell. The Pre-flight cell sets the length budget at ~3 short paragraphs; respect it.
