# Post-Mac 8 — Deep rewrite of JOURNEY.ipynb as educational narrative

## Operational preconditions (read before invoking)

Open a fresh Claude Code session. Run from `/Users/klambros/harness-engineering/` as the working directory. Operations 06 (README) and 07 (HARNESS_GUIDE) have committed. This prompt assumes the on-disk verification from Operation 06 passed.

This prompt rewrites a Jupyter notebook, which is JSON-formatted. Edits require care to preserve nbformat validity.

<role>
You are deep-rewriting `JOURNEY.ipynb` as the educational narrative companion to the structural documentation. JOURNEY tells the story of how the harness got built: what was tried, what worked, what surprised, what would be different next time.

Voice: first-person, Rock's exec voice. Bayesian framing where appropriate (treating beliefs as updateable, naming probabilities rather than certainties when the evidence merits it). Rock's writing rules apply: no em dashes, no semicolons, no sentences starting with conjunctions, no AI filler, no corporate slop. Plain words. Active voice. American English.

You are drafting. Rock owns the final voice. Where you cannot write authentically as Rock from the evidence available, leave a `<!-- ROCK: confirm or rewrite -->` marker rather than producing pseudo-Rock prose. Examples of where to leave markers: subjective surprise reactions, retrospective regrets framed in first person, value judgments on specific tools or vendors. The phase outputs record decisions and findings; Rock's voice records how he felt about them.

The model is a builder's retrospective written for other builders. Not a corporate post-mortem. Not a sales narrative. Not a polished case study. Honest about what didn't work alongside what did.
</role>

<effort>xhigh</effort>

<mode>default mode (writes the notebook).</mode>

<thinking>adaptive</thinking>

<context_budget>Run /context at start, after the prologue and pre-flight, after Phase 0-2 cells, after Phase 3-5 cells, after operations cells, and at end. The phase outputs are the primary source material. Record state in `phase-outputs/POST-MAC-8-CONTEXT.md`.</context_budget>

<parallel_tool_calls>
Initial parallel read: `JOURNEY.ipynb` (current state), `phase-outputs/PREFLIGHT.md`, `phase-outputs/PHASE-0-DECISIONS.md`, `phase-outputs/INVENTORY.md`, `phase-outputs/CONFLICTS.md`, `phase-outputs/QUESTIONS.md`, `phase-outputs/ANSWERS.md`, `phase-outputs/PHASE-3-NOTES.md`, `phase-outputs/PHASE-4-NOTES.md`, `phase-outputs/PHASE-5-AUDIT.md`, `phase-outputs/POST-MAC-1-NOTES.md`, `phase-outputs/POST-MAC-3-NOTES.md`, `phase-outputs/POST-MAC-4-PLAN.md`, `phase-outputs/POST-MAC-4-VERIFICATION.md`.
</parallel_tool_calls>

<scope>
Apply only to:
- `JOURNEY.ipynb` (writes)
- `phase-outputs/POST-MAC-8-CONTEXT.md` (writes)
- `phase-outputs/POST-MAC-8-NOTES.md` (writes: cell-by-cell authoring decisions, every Rock-marker placed, every audit finding that informed a surprise or tradeoff)

Do not modify any other file.
</scope>

## What to do

Target: 42-58 substantive cells. The current notebook has 13 cells; six of them say "not yet started" against phases that have shipped. The rewrite expands those six into a story, adds prologue and epilogue cells, adds operations cells, and preserves and updates the verification code cells.

Cell-count budget by section (totals to 42-58):

- Prologue: 3-4 cells
- Pre-flight: 1 cell (refreshed)
- Phase 0: 4-6 cells
- Phase 1: 4-6 cells
- Phase 2: 5-7 cells
- Phase 3: 4-6 cells
- Phase 4: 3-5 cells
- Phase 5: 5-7 cells
- Operations: 3-4 cells
- Verification code cells: 3-4 cells (existing + new)
- Epilogue: 3-4 cells
- Post-launch revisions: 1 cell (kept)

Per-phase cells follow a consistent structure of four shapes:

- **Context cell**: what the phase was for, what the prompt asked for.
- **Narrative cell**: what happened. The concrete events.
- **Surprises cell**: what didn't go as expected. Cite specific findings or reframings.
- **Tradeoffs cell**: the decisions that turned on a tradeoff. Name the alternative not taken.
- **Retrospective cell**: what I would do differently. Tie to specific audit findings.

Not every phase needs all five; some merge. The budget is a guide, not a hard count.

### Prologue cells (3-4 cells)

**Cell 1: "Why I built this."** First-person setup. The problem (Claude Code's default permissive posture, three machines with credentials and push access, the cost of one mistake), the question (what would it take to harness Claude Code with security discipline without sacrificing the usefulness that made me adopt it), the commitment (build it in public so others can read the reasoning, not just the outputs). Anchor in concrete things: the plaintext API token found in Phase 1, the 56 dangling symlinks, the 4311 unpruned session logs. Three or four paragraphs.

**Cell 2: "What this notebook is and isn't."** Not a tutorial. Not a postmortem. The notebook is the reasoning chain that produced the rest of the repo. Each phase has its own cell with a consistent structure: context, narrative, surprises, tradeoffs, retrospective. Where I left a `<!-- ROCK: confirm or rewrite -->` marker, the executing session was unsure and Rock made the call.

**Cell 3: "How to read this notebook alongside the repo."** Pointer to README for the front door, to HARNESS_GUIDE for the user manual, to foundation/ for the principles. JOURNEY is the story; the other documents are the structure.

Optional **Cell 4: "A note on what this repo is not."** One paragraph distinguishing this from a turnkey product, a course, or a how-to.

### Pre-flight cell (1 cell, refresh existing)

Current content is short. Add one paragraph: what the three research documents are (Liu et al. on Claude Code v2.1.88, SAGE on harness engineering as a discipline, NIST SP 800-218 on secure development). What SAGE settled. Why the build was structured around shared foundation plus three platform sections.

### Phase 0 cells (4-6 cells)

- Context: what Phase 0 was for (environment baseline, decisions driving Phase 2 questions, settling which `<TBD-PHASE-0>` blocks resolve vs defer).
- Narrative: what happened. macOS 26.3, Node 24.10, Python 3.13.9, Claude Code v2.1.138, the SuperClaude framework already in place at user level adding 16.6k tokens. The cache-lineage decision (Opus parent / Opus subagent). The cost-cache tradeoff named openly.
- Surprises: the user-level CLAUDE.md hierarchy was 5.7x larger than the project's. The prompt-authoring inconsistency PHASE-0-DECISIONS caught (settings.json.template TBD markers out of Phase 0's scope). The Anaconda Python's broken semgrep install.
- Tradeoffs: Opus everywhere (cache economy) vs mixing Sonnet for routine subagents (cost economy). Brewfile.lock vs direct pins (chose deferred). Network egress monitor evaluation (deferred to Phase 4, eventually skipped).
- Retrospective: prompt-authoring inconsistency. Verification grep over-broadness (`<TBD-PHASE-0>` grep counted prose references to the marker as remaining work).

### Phase 1 cells (4-6 cells)

The 44 in-repo `.claude/` directories found. The plaintext Hetzner API token. The 16-plugin enabledPlugins list. The 4311 session logs. The seed pre-filter surface. Surprise: Q5 (every-clone hash-gated audit) became materially more expensive than expected given the backlog. Tradeoff: pre-trust audit cadence vs operational friction.

### Phase 2 cells (5-7 cells)

The densest phase because it's where the calibrated decisions landed.

- Context: the AskUserQuestion interview format, the goal of recording the rationale alongside each answer.
- Narrative: walk through the 11 questions briefly. Q1 auto-mode classifier enabled, Q2a T2+T5, Q2b T3, Q3 rebuild entire `~/.claude/` beyond planned options, Q4-Q11 shorter.
- Surprises: Q3 reframed mid-interview by Rock's clarification. Q2a needed clarification before Rock could choose; original options forced a security-vs-friction tradeoff he wanted help calibrating. The agentcontrolstandard.ai future swap-in candidate surfaced through Q8.
- Tradeoffs: auto-mode on (Q1) traded 0.4% false-positive rate for daily-driver friction reduction. 30-subcommand cap (Q6) traded operational ceiling for defense in depth below the 50-bypass class. Rebuilding entire `~/.claude/` (Q3) traded build effort for clean operational baseline.
- Retrospective: Q3 option set was too narrow. Right framing surfaced through Rock's clarification. Future architecture interviews should include an "other" option with structured follow-up.

### Phase 3 cells (4-6 cells)

Six hooks, six deny rules, settings.json populated. Surprise: the supply-chain hook regex (F04, F05) was structurally broken for pinned `uvx --from git+...@<ref>` and pinned `npx -y <pkg>@<version>`. Honest write-up: greedy match consumed URL, negative lookahead scanned past pin, ordinary pinned installs false-positived as unpinned. Two-step rewrite (regex extracts, Python validates) fixed it. The cached-prefix-write-gate's deliberately narrow scope (Q2a T5).

### Phase 4 cells (3-5 cells)

Two skills, two agents adopted. Smaller than seed pre-filter implied. Superpowers v5.1.0 skill count was 14, not the 17 INVENTORY claimed (F08). Tradeoff: lean adoption with documented swap-in paths vs broader adoption with more cache-prefix footprint.

### Phase 5 cells (5-7 cells)

The wire-and-document phase. Writer/Reviewer subagent pattern. 13 findings. Blocker F01 was the audit log itself missing as a deliverable; prompt's own verification grep depended on a file the prompt did not yet require be produced. The two regex bugs from Phase 3 caught here. Three accept-residual-risk findings (F09, F10, F11) with their named post-launch triggers. "READY with majors recorded," not READY clean.

### Operations cells (3-4 cells)

Why operations weren't part of the original phase plan: the Mac build's phase sequence settled the structural artifacts; operations land what those artifacts produced into the operational environment and propagate learnings.

- Operation 1: drift-check widening. Closed the Phase 2 Q10 commitment that no phase prompt named.
- Operation 3: cross-pollination into Jetson and Windows scaffolds.
- Operation 4: the destructive rebuild of `~/.claude/`. Biggest single act of the build. Default-keep posture settled through Socratic walkthrough with Rock. The four non-negotiables (plaintext secrets, skipDangerousModePermissionPrompt, dangling symlinks, expired session logs). §Files to classify concern-flagged surface. Single confirmation gate. Byte-identical preservation discipline.

Optional cell on Operations 06-09 (this closeout sequence) as the documentation-deliverables wave that turned the private build into a public-facing reference.

### Verification cells (3-4 cells)

Update the first existing code cell from raw `find . -name 'CLAUDE.md'` line counting to `!bash scripts/drift-check.sh`. The widened drift-check produces a more useful breakdown.

Keep the existing `!bash scripts/drift-check.sh` cell (now redundant; harmless but consider removing for cleanliness).

Keep `!wc -l foundation/*.md`.

Add a new code cell that prints the most recent commit log scoped to mac/: `!git log --oneline -20 -- mac/`. Useful for readers wanting to see the build sequence in commit form.

### Epilogue cells (3-4 cells)

**"What I learned about Claude Code as a build target."** Honest assessment. What worked (AskUserQuestion interview format, Writer/Reviewer pattern, explicit cache-lineage discipline). What didn't (Phase 5 prompt's circular verification dependency, supply-chain hook regex assumed without testing). What surprised me about Opus 4.7 as a build executor (literalism on scope, parallel-tool-call efficiency, tendency to over-emphasize when prompts did).

**"What I learned about harness engineering as a discipline."** How the Quality Contract held up under real building. Whether the threat model's six threats were the right framing or whether I'd reorganize next time. Drift between expected and validated findings.

**"What comes next."** Jetson execution. Windows execution. Continuous-revision operational model. Residual-risk findings carrying their reconsideration triggers. agentcontrolstandard.ai swap-in candidate. The repo is born public; revisions land as the harness evolves.

**"How to contribute."** Brief: this is a personal reference repo. Issues and discussion welcome; PRs that change locked decisions are not. Forks adapting for other threat models are exactly the intended use.

### Post-launch revisions cell (keep)

As-is or with a sentence noting Operations 06-09 were the last operations in the original build sequence; everything after is post-launch revision.

<investigate_before_answering>
Before writing a "surprise" into a phase cell, cite the specific phase output and section where the surprise is recorded. Surprises pulled from your own assumptions are not evidence.

Before writing "what I would do differently" for a phase, tie each item to a specific Phase 5 audit finding or PHASE-0-DECISIONS scope inconsistency. Speculation without an audit trail does not belong in JOURNEY.

Before placing a `<!-- ROCK: confirm or rewrite -->` marker, ask whether the phase outputs actually carry the perspective. If they do, draft from them; if they don't, marker is correct.

Before any cell claims a specific number (44 in-repo directories, 4311 session logs, 16.6k tokens, etc.), verify the number against the phase output that recorded it.
</investigate_before_answering>

## Deliverables

- `JOURNEY.ipynb`: 42-58 cells, story arc, voice consistent throughout, Rock-markers where Rock's voice is needed
- `phase-outputs/POST-MAC-8-CONTEXT.md`: context-budget record
- `phase-outputs/POST-MAC-8-NOTES.md`: cell-by-cell authoring decisions, Rock-marker count, audit findings cited

## Verification

Before reporting complete:

- `python3 -c "import json; json.load(open('JOURNEY.ipynb'))"` parses (valid JSON).
- `jupyter nbconvert --to script JOURNEY.ipynb` succeeds (valid nbformat).
- Cell count is 42-58.
- Each of the six phase cells is gone from "not yet started" state; status reflects completion.
- `grep -o 'ROCK:' JOURNEY.ipynb | wc -l` returns the count of Rock-markers placed; report in NOTES.
- No em dashes, no semicolons, no sentences starting with And/But/Or/So/Nor at the start of any cell content.
- No AI-filler banned words.
- No corporate-slop banned words.
- The verification code cells point to current commands (drift-check, not the raw find).
- `bash scripts/drift-check.sh` returns 0 or WARN. The notebook does not contribute to cached prefix.

Report cell count, Rock-marker count, line count of the notebook, citation count back to phase outputs, and any voice drift caught and fixed.

## Commit

```
docs: deep rewrite of JOURNEY.ipynb as educational narrative

Context: Original JOURNEY was a Batch 1 scaffold with six phase cells saying "not yet started." Mac build executed but no phase prompt named JOURNEY as a deliverable, so the notebook sat at scaffold state while the rest of the repo shipped. Operation 08 closes the gap.

Decision: Rewrite as 42-58 cell educational narrative with story arc. Prologue (why, what this is, how to read), per-phase cells (context, narrative, surprises, tradeoffs, retrospective), operations cells covering post-execution work, epilogue (lessons, what's next), verification code cells, post-launch revisions.

Why: A repo whose narrative companion is "not yet started" reads as incomplete. The build's reasoning chain is the artifact's primary value per the locked decision; the notebook is where that reasoning lives in first-person form. Rock's voice owns the narrative; the executing session drafts where Rock's perspective is needed and leaves <!-- ROCK --> markers for confirmation.

Tradeoff: Cell count up from 13 to ~50. The notebook becomes substantial reading. Mitigation: each phase's cells are sectioned consistently (context, narrative, surprises, tradeoffs, retrospective), so readers can skip to the section they need within a phase.
```

Commit. Push.

## Anti-overengineering

Do not invent narrative. Pull from phase outputs. Where Rock's voice or perspective is needed and the phase outputs do not carry it, leave a marker.

Do not rewrite the existing JOURNEY header cell or the existing Pre-flight cell wholesale. They are anchor points. Refresh content where needed, preserve framing.

Do not write JOURNEY in third-person or analyst voice. The narrative is first-person Rock voice. Where you cannot draft authentically, marker rather than pseudo-Rock prose.

Do not produce more than four short paragraphs per markdown cell. Long cells lose readers. Break content into multiple cells if needed.

Do not skip the verification step. nbformat invalidity in a notebook is silent until someone opens it in Jupyter; the JSON parse and nbconvert checks catch it before commit.

If during authoring you find a finding the phase outputs do not record (an event that happened but was not written down), do not invent details. Flag in NOTES as a gap and either ask Rock or leave a placeholder marker. The notebook is the reasoning chain; reasoning that was never recorded should not be retroactively manufactured.
