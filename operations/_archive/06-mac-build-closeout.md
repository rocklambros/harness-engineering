# Post-Mac 6 — Mac build closeout: documentation deliverables and behavioral verification

## Operational preconditions (read before invoking)

Open a fresh Claude Code session before running this prompt. Run from `/Users/klambros/harness-engineering/` as the working directory. The rebuilt `~/.claude/` from Operation 4 is the active configuration this session loads.

This is the longest single prompt in the operations sequence. Realistic execution time is 60-90 minutes. The work is staged so each major deliverable commits independently; if the session hits context pressure between stages, the next stage can resume in a new session against the committed state. Do not try to compress the work into one pass at the cost of quality.

<role>
You are producing the documentation closeout for the Mac build. Four artifacts: a CHECKPOINT.md state update (local only), a rewritten README.md (the repo's front door), a new HARNESS_GUIDE.md (the user manual a novice can read), and a deep rewrite of JOURNEY.ipynb (the educational narrative that tells the build's story). Plus an operator runbook for Rock to behaviorally verify the rebuilt `~/.claude/` in a separate test session.

The voice across the three external-facing artifacts is calibrated to audience:

- README.md: pragmatic. The reader has 90 seconds. Tell them what this is, who it's for, where to read next.
- HARNESS_GUIDE.md: educational, like explaining the harness over coffee to a sharp colleague who has never used Claude Code. Define terms before using them. Show examples. Explain why, not just what. Plain English educational, never corporate-course "embark on your learning journey" educational. The model is Julia Evans zines, not enterprise wiki documentation.
- JOURNEY.ipynb: first-person, Rock's exec voice, narrative with story arc. Tells what happened, what surprised, what turned on a tradeoff, what would be different next time. The model is a builder's retrospective written for other builders, not a corporate post-mortem.

All three apply Rock's writing rules: no em dashes, no semicolons, no sentences starting with conjunctions, no AI filler, no corporate slop. Plain words. Active voice. American English.
</role>

<effort>xhigh</effort>

<mode>default mode throughout. No plan mode required because the prompt structure is the plan.</mode>

<thinking>adaptive</thinking>

<context_budget>Run /context at start, after Stage 1, after Stage 3, after Stage 4, and at end. The reading load is substantial; HARNESS_GUIDE and JOURNEY both pull from every phase output and every harness artifact. Record state in `phase-outputs/POST-MAC-6-CONTEXT.md`.</context_budget>

<parallel_tool_calls>
Initial parallel read: `CHECKPOINT.md`, `README.md`, `JOURNEY.ipynb`, `foundation/00-quality-contract.md`, `foundation/01-threat-model.md`, `foundation/02-architectural-principles.md`, `foundation/03-seed-evaluation-methodology.md`, `foundation/04-research-references.md`, `mac/README.md`, `mac/ARCHITECTURE.md`, `mac/harness/CLAUDE.md`, `mac/harness/settings.json`.

After Stage 0, parallel-read every file in `mac/harness/hooks/`, `mac/harness/rules/`, `mac/harness/skills/`, `mac/harness/agents/`, plus every file in `phase-outputs/` that doesn't end in `-CONTEXT.md` (those are budget records, not content).
</parallel_tool_calls>

<scope>
Apply to:
- `CHECKPOINT.md` (writes; gitignored so no commit)
- `README.md` (writes; commit)
- `HARNESS_GUIDE.md` (writes; new file; commit)
- `JOURNEY.ipynb` (writes; commit)
- `phase-outputs/POST-MAC-6-CONTEXT.md` (writes)
- `phase-outputs/POST-MAC-6-NOTES.md` (writes: what was authored, what was deferred, every editorial choice that mattered)
- `phase-outputs/POST-MAC-6-VERIFICATION-PROTOCOL.md` (writes: the runbook Rock executes in a separate fresh Claude Code session)

Do not modify any file in `mac/harness/`, `jetson/`, `windows/`, `foundation/`, `research/`, `scripts/`, or `operations/`. Those are settled.

Do not modify `LICENSE`, `SECURITY.md`, `.gitignore`, `.pre-commit-config.yaml`. Settled.
</scope>

## What to do

Six stages. Each stage has its own deliverable. Stages 1 through 4 each end with a commit before the next stage starts. The order matters: CHECKPOINT first (so subsequent docs can cite it), then README (the front door anchors the reader's expectations), then HARNESS_GUIDE (the deep teaching artifact), then JOURNEY (the narrative companion).

### Stage 0: Read and verify state

Read the parallel-read manifest above. Build a working understanding of:

- What's already in `README.md` (likely a Batch 1 placeholder).
- What's already in `JOURNEY.ipynb` (six phase cells in "not yet started" state, per Rock's earlier observation).
- What the Quality Contract actually says (foundation/00, the five properties).
- What the threat model actually covers (foundation/01, T1-T6).
- What the architectural principles enforce (foundation/02).
- What each Mac harness artifact does (hooks, rules, skills, agents, settings.json).
- What the phase outputs record about decisions and findings.

Verify the rebuilt `~/.claude/` on-disk state. Run these checks and record results in `phase-outputs/POST-MAC-6-CONTEXT.md`:

- `python3 -c "import json; json.load(open(os.path.expanduser('~/.claude/settings.json')))"` parses.
- `grep -v '^\s*$' ~/.claude/settings.json | grep -i 'skipDangerousModePermissionPrompt'` returns nothing (Q9 removal verified).
- `bash scripts/drift-check.sh` returns 0 or WARN (not FAIL).
- `ls -la ~/.claude/CLAUDE.md ~/.claude/hooks/ ~/.claude/skills/ ~/.claude/agents/` confirms the rebuilt deliverables exist.
- `cd ~/.claude && git log --oneline -1 && cd -` confirms the private git repo is initialized.

If any check fails, stop and surface to Rock before continuing. The documentation should not advertise a state that doesn't exist.

### Stage 1: Update CHECKPOINT.md

`CHECKPOINT.md` is gitignored; no commit. The update reflects post-build, post-rebuild state for Rock's own working reference.

Read the current CHECKPOINT. Rewrite the sections that have drifted:

- **Build state**: Mac is no longer "validated, build pending" or "Phase 5 executed." It is now "validated, rebuilt, operating." Operations 1, 3, 4 complete. Operation 2 deferred (now superseded by Operation 6 which rewrites JOURNEY in greater depth). Operation 5 deferred to per-platform execution Rock handles separately.
- **Jetson/Windows state**: "scaffolded with Mac cross-pollination applied (Operation 3), awaiting platform execution per Operation 5 runbook."
- **Documentation state**: Operation 6 produced README.md rewrite, HARNESS_GUIDE.md (new), JOURNEY.ipynb deep rewrite. Repo is now in its public-facing documented state.
- **Open items**: Jetson and Windows phase execution; ongoing operational use generating revision items; the residual-risk findings from Phase 5 (F09, F10, F11) carrying their post-launch reconsideration triggers.

Keep locked decisions section as-is unless an actual decision has changed. Add a "Build sequence completed" subsection naming the dates the phases ran and the operations landed.

Save. No commit (gitignored).

### Stage 2: Rewrite README.md

Target length: 180-250 lines. The reader has 90 seconds. Optimize for "I get what this is, I know whether it's relevant to me, I know where to read next."

Required sections, in order:

**Heading and one-paragraph what-this-is.** What this repo contains in two sentences. Frame it as a reference, not a clone-and-run template. Name the three platforms (Mac, Jetson AGX Orin, Windows) and the current validation state (Mac validated, Jetson and Windows scaffolded). One sentence on what "harness engineering" means as a discipline.

**Who this is for.** Three audiences in three short paragraphs: people building their own Claude Code harness who want a worked reference; people evaluating Claude Code's security model and want to see what hardening looks like in practice; people interested in the harness-engineering discipline itself as a software-engineering practice. Be honest that this is not a turnkey product.

**The Quality Contract in two sentences.** Name the five properties (QC.1 Security, QC.2 Tight code, QC.3 Comment the why, QC.4a Cache discipline, QC.4b Context window discipline, QC.5 Versioning) and what they collectively enforce. Point to `foundation/00-quality-contract.md` for detail.

**Where to read next.** This is the most important section. A small table or short prose map showing which document answers which reader question:

- "What is a Claude Code harness and how does this one work?" → `HARNESS_GUIDE.md`
- "Why did the author build it this way?" → `JOURNEY.ipynb`
- "What are the design principles?" → `foundation/`
- "What does the Mac-specific harness look like?" → `mac/`
- "What's the underlying research?" → `research/`

**Quick start.** Three or four steps for a reader who wants to evaluate using this harness on their own machine. Clone the repo. Read README, HARNESS_GUIDE, and the relevant platform README in that order. Adapt rather than copy. Do not symlink mac/harness/ over the reader's `~/.claude/` without first going through HARNESS_GUIDE's adaptation section.

**What this repo is not.** One short paragraph. Not a CLI tool. Not a product. Not seeking PRs that change locked decisions. Personal-specific is the value; reading it teaches a discipline, copying it wholesale does not.

**License, security, contact.** Brief. MIT, link to SECURITY.md for vulnerability reporting, repo URL.

Voice for README: pragmatic, plain, signposting. No motivational preamble. No "in the age of LLM-based coding assistants" framing. Start where the content starts.

Commit message:

```
docs: rewrite README.md as repo front door

Context: Mac build complete, ~/.claude/ rebuild executed. Public-facing documentation set being landed via Operation 6. README is the first artifact in that set.

Decision: Rewrite README as a 200-line front door. Optimize for 90-second comprehension. Signposts to HARNESS_GUIDE, JOURNEY, foundation, and platform READMEs.

Why: The Batch 1 README served the build phase. Now that the documentation set is taking shape, the front door needs to do front-door work: name what this is, name who it's for, point readers to the right next document.

Tradeoff: Length traded against signposting. A 500-line README would carry more detail but would compete with HARNESS_GUIDE for the same teaching job. Cleaner separation: README answers "what is this," HARNESS_GUIDE answers "how does it work."
```

Commit. Push.

### Stage 3: Author HARNESS_GUIDE.md (new file)

Target length: 1500-2500 lines. This is the deep teaching artifact. A novice who has never used Claude Code reads this and walks away understanding what a harness is, what this specific harness does, and how to think about building or adapting one.

Tone discipline. Educational means defining terms before using them, showing examples, explaining why. It does NOT mean course-marketing language ("welcome to your learning journey"), motivational asides ("you've got this!"), or filler that performs warmth without conveying information. If a sentence could appear in a course landing page, rewrite it. The model is a senior engineer explaining their work to a sharp colleague, not a vendor explaining their product to a prospect.

Required sections, in order, with notes on what goes in each:

**§1. What is a Claude Code harness.** Start by defining Claude Code (the CLI runtime, distinct from the model). Then define the harness as the configuration layer that shapes Claude Code's behavior: deny rules, hook scripts, the CLAUDE.md hierarchy, skills, agents, MCP servers, settings.json. Use a concrete example: "when you type `claude` in your terminal and start a session, several files load before you ever send a message. Those files are the harness." Cite `research/Claude_Architecture.md` for the runtime detail. Two to four pages.

**§2. Why harness engineering.** Frame the problem the discipline solves: Claude Code is powerful and trusts the user; users routinely give it access to credentials, code, and execution privileges; the default configuration is permissive; the cost of a single mistake is high. Harness engineering is the discipline of treating that configuration as a security-and-quality artifact in its own right. Cite `foundation/02-architectural-principles.md` and SAGE (`research/Harness_Engineering_for_Claude_Code_A_Systems_Architecture_Analysis.md`) for the discipline's underpinnings. One to two pages.

**§3. The five layers of a Claude Code harness.** This is the conceptual scaffolding. Each layer gets a subsection:

- **Permission layer.** Deny rules, allow rules, defaultMode (`auto` vs `default`), `additionalDirectories`. What the layer enforces, what it cannot enforce, the order of evaluation (deny first, then allow, then mode-based). Cite research/Claude_Architecture §5.
- **Hook layer.** The lifecycle events Claude Code fires (SessionStart, PreToolUse, PostToolUse, Stop, UserPromptSubmit, Notification, PreCompact, PostCompact). What each event sees. How to register a hook. The exit-code semantics (0 = allow, 2 = block with stderr). Cite research/Claude_Architecture §6.
- **Memory/cache layer.** The CLAUDE.md hierarchy (project root → platform → harness → user-level `~/.claude/CLAUDE.md`). How `@import` resolution works. Why cache stability matters (QC.4a). Why context window discipline matters (QC.4b). Cite foundation/00.
- **Extension layer.** Skills, agents, MCP servers. What each kind of extension is for. How they differ. When to use which. Cite mac/harness/skills/ and mac/harness/agents/.
- **Telemetry layer.** Session logs in `~/.claude/projects/<encoded-cwd>/<session-uuid>.jsonl`. Retention. What gets captured. Privacy implications.

Each subsection is two to three pages.

**§4. Anatomy of this harness.** A file-by-file walkthrough of `mac/harness/`. Read each file as part of Stage 0 and write a subsection explaining: what it does, when it fires or loads, what specifically it allows or blocks, why it's calibrated the way it is. Pull the rationale from `phase-outputs/PHASE-3-NOTES.md`, `phase-outputs/PHASE-4-NOTES.md`, and `phase-outputs/ANSWERS.md`.

Files to cover, each with its own subsection:

- `mac/harness/CLAUDE.md` itself (the advisory layer)
- `mac/harness/settings.json` (the permission and registration spine)
- Each of the six Python hooks (`PreToolUse-bash-cap-subcommands.py`, `PreToolUse-cached-prefix-write-gate.py`, `PreToolUse-external-write-gate.py`, `PreToolUse-supply-chain-bash-checks.py`, `SessionStart-audit-claude-config.py`, `Stop-prune-session-logs.py`)
- Each of the six deny rules (`bash-deny-dangerously-skip-permissions.md`, `bash-deny-git-push-force.md`, `bash-deny-rm-rf-root.md`, `bash-deny-sudo.md`, `filesystem-deny-write-secrets.md`, `mcp-deny-server-prefix-default.md`)
- Each of the two skills (`mcp-server-pre-trust-audit`, `seed-evaluation`)
- Each of the two agents (`inventory.md`, `reviewer.md`)

Per subsection: what does this file do; when does it run; what does it block, allow, or produce; what was the calibrated decision behind its specific shape; cite the phase output that records that decision. Each subsection is half a page to a page.

**§5. How to use this harness.** For a reader who wants to use this on their own machine. Cover:

- The fork-and-adapt model (not symlink-and-run). Personal-specific is the value.
- Installation paths: in-repo (read-only reference), copied into your own repo (you take ownership), or as the basis for rebuilding your own `~/.claude/` (the path Rock took, documented in `operations/04-user-claude-rebuild.md`).
- The Quality Contract as a quality bar to hold your own adaptation to.
- The drift-check script and how to extend it for your fork.
- When to deviate from this harness's defaults (most readers will need to).

One to two pages.

**§6. How to extend this harness.** For a reader who wants to add their own hooks, rules, skills, or agents. Cover:

- Adding a hook: the template, the event lifecycle, the exit-code contract, where to test it.
- Adding a deny rule: the prefix-match semantics, the empty-prefix gotcha (Phase 5 F02), how to verify the pattern fires.
- Adding a skill: the SKILL.md structure, when skills load vs when they're invoked, the trigger surface.
- Adding an agent: the agent file structure, when subagents are spawned, the cache-lineage discipline (QC.4a, same-family subagents).

Each subsection includes a minimal example. One to two pages each.

**§7. The Quality Contract in practice.** For each of the five properties (QC.1, QC.2, QC.3, QC.4a, QC.4b, QC.5), explain: what the property requires; how this harness enforces it; what a violation looks like; how to detect violations in your own fork. Cite foundation/00 and the relevant enforcement artifacts (drift-check.sh for QC.4b, pre-commit hooks for QC.1, etc.). Two to three pages.

**§8. The threat model in practice.** For each of the six threats (T1 prompt injection, T2 supply chain, T3 pre-trust initialization, T4 sub-command chain bypass, T5 cache poisoning, T6 hostile MCP server), explain: what the threat is; what the consequence is if unmitigated; how this harness mitigates it (which hook, rule, skill); what residual risk remains. Cite foundation/01 and the relevant artifacts. Two to three pages.

**§9. Operational discipline.** The recurring practices that keep the harness honest over time. Cover: drift-check (when to run, what it catches); pre-trust audit for in-repo `.claude/` directories (the SessionStart hook); session log retention (the Stop hook, the 90-day window); backup before destructive changes (the lesson from Operation 4). One to two pages.

**§10. What this harness deliberately does NOT do.** Honest scope. Not a network egress monitor (Phase 2 Q7). Not a full SBOM/SLSA pipeline. Not a substitute for OS-level hardening. Not a guarantee against novel attacks; the residual risk findings from Phase 5 (F09 SessionStart exit-2 semantics, F10 cached-prefix-write-gate scope, F11 glob dialect verification) carry post-launch reconsideration triggers. Name the cost of completeness in any direction. One page.

**§11. Glossary.** Short reference. Define every term used in the document that a Claude Code novice might not know: agent, allow rule, auto-mode classifier, cached prefix, CLAUDE.md hierarchy, deny rule, hook event, MCP, MCP server, plan mode, skill, subagent, session log, settings.json. One to two pages.

Each section is its own H2. Each subsection within is an H3. Tables, code blocks, and short examples are welcome where they aid comprehension. Avoid bulleted lists longer than seven items.

Reading-order discipline. The reader of HARNESS_GUIDE.md is sequential by default. §1 enables §2 enables §3 enables §4. §4 is the densest and longest section. §5-§10 are reference, read out of order by anyone with a specific need. §11 is the glossary.

Commit message:

```
docs: add HARNESS_GUIDE.md as the educational user manual

Context: README answers "what is this." HARNESS_GUIDE answers "how does it work, how do I use it, how do I extend it." Operation 6 introduces this artifact.

Decision: 1500-2500 line user guide. Educational tone, novice-readable. Eleven sections covering: what a harness is, why harness engineering, the five layers, file-by-file anatomy of this harness, use, extension, Quality Contract in practice, threat model in practice, operational discipline, deliberate scope limits, and glossary.

Why: A reference repo without a teaching document is read by experts only. The discipline this repo demonstrates is most valuable when someone unfamiliar with Claude Code can follow the reasoning. HARNESS_GUIDE makes that possible.

Tradeoff: Length. A 2000-line document competes for the reader's attention. The mitigation is sectional readability (§1-§3 read in order; §4 reads as anatomy reference; §5-§10 read by need; §11 reads as glossary). Readers do not need to consume the whole document linearly.
```

Commit. Push.

### Stage 4: Deep rewrite of JOURNEY.ipynb

Target: 40-60 substantive cells. Educational narrative with story arc. First-person, Rock's exec voice, writing rules apply.

The current JOURNEY has 13 cells. Six of them say "not yet started" against phases that have shipped. The rewrite expands those six into a story, adds prologue and epilogue cells, and preserves the verification code cells.

Structure:

**Prologue cells (3-4 cells).**

- Cell 1: "Why I built this." First-person setup. The problem (Claude Code's default permissive posture, three machines with credentials and push access, the cost of one mistake), the question (what would it take to harness Claude Code with security discipline without sacrificing the usefulness that made me adopt it), the commitment (build it in public so others can read the reasoning, not just the outputs). Anchor in concrete things: the plaintext API token found in Phase 1, the 56 dangling symlinks, the 4311 unpruned session logs. Three or four paragraphs.
- Cell 2: "What this notebook is and isn't." Not a tutorial. Not a postmortem. The notebook is the reasoning chain that produced the rest of the repo. Each phase has its own cell with a consistent structure: context (what was the goal), surprises (what didn't go as expected), tradeoffs (what turned on a decision), what I'd do differently. Where I left a `<!-- ROCK: confirm or rewrite -->` marker, the executing session was unsure and I made the call myself.
- Cell 3: "How to read this notebook alongside the repo." Pointer to README for the front door, to HARNESS_GUIDE for the user manual, to foundation/ for the principles. JOURNEY is the story; the other documents are the structure.

**Pre-flight cell (keep, refresh).** Current content is short. Add one paragraph: what the three research documents are (Liu et al. on Claude Code v2.1.88, SAGE on harness engineering as a discipline, NIST SP 800-218 on secure development). What the SAGE doc settled. Why the build was structured around shared foundation plus three platform sections.

**Phase 0 cells (4-6 cells).**

- Phase 0 context cell: what Phase 0 was for (recording the environment baseline, settling architecture decisions that drive Phase 2 questions, deciding which `<TBD-PHASE-0>` blocks settle and which defer).
- Phase 0 narrative cell: what happened. macOS 26.3, Node 24.10, Python 3.13.9, Claude Code v2.1.138, the SuperClaude framework already in place at user level adding 16.6k tokens. The cache-lineage decision (Opus parent / Opus subagent). The cost-cache tradeoff openly named.
- Phase 0 surprises cell: the user-level CLAUDE.md hierarchy was 5.7x larger than the project's. The prompt-authoring inconsistency caught by PHASE-0-DECISIONS (`settings.json.template` had TBD markers but was out of Phase 0's scope). The Anaconda Python's broken semgrep install.
- Phase 0 tradeoffs cell: Opus everywhere (cache economy) vs. mixing Sonnet for routine subagents (cost economy). Brewfile.lock vs direct pins (chose deferred to Phase 3). Network egress monitor evaluation (deferred to Phase 4, eventually skipped).
- Phase 0 retrospective cell: what I would do differently. Include the prompt-authoring inconsistency. Include the verification grep over-broadness (the `<TBD-PHASE-0>` grep counted prose references to the marker as remaining work).

**Phase 1 cells (4-6 cells, same shape).** The 44 in-repo `.claude/` directories found. The plaintext Hetzner API token. The 16-plugin enabledPlugins list. The 4311 session logs. The seed pre-filter surface. The honest surprise that Q5 (every-clone hash-gated audit) became materially more expensive than expected given the backlog. The tradeoff between cadence and friction.

**Phase 2 cells (5-7 cells).** This is the densest phase because it's where the calibrated decisions landed.

- Phase 2 context cell: the AskUserQuestion interview format, the goal of recording the decision rationale alongside each answer.
- Phase 2 narrative cell: walk through each of the 11 questions briefly with the answer chosen. Q1 (auto-mode classifier enabled), Q2a (T2 narrow + T5), Q2b (T3 SessionStart), Q3 (rebuild entire `~/.claude/`, beyond planned options), Q4-Q11 with shorter coverage.
- Phase 2 surprises cell: Q3 reframed mid-interview. Q2a needed clarification before Rock could choose; the original options forced a security-vs-friction tradeoff Rock wanted help calibrating. The agentcontrolstandard.ai future swap-in candidate surfaced through Q8.
- Phase 2 tradeoffs cell: auto-mode on (Q1) traded the 0.4% false-positive rate for daily-driver friction reduction. The 30-subcommand cap (Q6) traded operational ceiling for defense in depth below the documented 50 bypass. Rebuilding entire `~/.claude/` (Q3) traded build effort for a clean operational baseline.
- Phase 2 retrospective cell: the Q3 option set was too narrow. The right framing surfaced through Rock's clarification. Future architecture interviews should include an "other" option with structured follow-up.

**Phase 3 cells (4-6 cells).** The deterministic layer. Six hooks, six deny rules, settings.json populated. The bug surfaced by Phase 5 audit: the supply-chain hook regex (F04, F05) was structurally broken for pinned `uvx --from git+...@<ref>` and pinned `npx -y <pkg>@<version>`. Honest write-up of the bug: greedy match consumed the URL, negative lookahead scanned past the pin, ordinary pinned installs false-positived as unpinned. The two-step rewrite (regex extracts, Python validates) that fixed it. The cached-prefix-write-gate's deliberately narrow scope (Phase 2 Q2a T5).

**Phase 4 cells (3-5 cells).** The extension layer. Two skills, two agents adopted. Smaller than seed pre-filter implied. The superpowers v5.1.0 skill count was 14, not the 17 INVENTORY claimed (F08). The bias toward lean adoption with documented swap-in paths.

**Phase 5 cells (5-7 cells).** The wire-and-document phase. The Writer/Reviewer subagent pattern. 13 findings. The blocker (F01) was the audit log itself missing as a deliverable; the prompt's own verification grep depended on a file the prompt did not yet require be produced. The two regex bugs from Phase 3 caught here. The three accept-residual-risk findings (F09, F10, F11) with their named post-launch triggers. "READY with majors recorded," not READY clean.

**Operations cells (3-4 cells).**

- Why operations weren't part of the original phase plan: the Mac build's phase sequence settled the structural artifacts; operations land what those artifacts produced into the operational environment and propagate learnings.
- Operation 1: drift-check widening. Closed the Phase 2 Q10 commitment that no phase prompt named.
- Operation 3: cross-pollination into Jetson and Windows scaffolds.
- Operation 4: the destructive rebuild of `~/.claude/`. The biggest single act of the build. Default-keep posture settled through Socratic walkthrough with Rock. The four non-negotiables (plaintext secrets, skipDangerousModePermissionPrompt, dangling symlinks, expired session logs). The §Files to classify concern-flagged surface. The single confirmation gate. The byte-identical preservation discipline. What ended up keep vs. replace.

**Verification cells (keep and update).** The three existing code cells. Update the first one's command from raw line counting to `!bash scripts/drift-check.sh`. Add a fourth code cell that prints the most recent commit log scoped to mac/ (so the public reader can see the build sequence in commit form).

**Epilogue cells (3-4 cells).**

- "What I learned about Claude Code as a build target." Honest assessment. What worked (the AskUserQuestion interview format, the Writer/Reviewer pattern, the explicit cache-lineage discipline). What didn't (the Phase 5 prompt's circular verification dependency, the supply-chain hook regex assumed without testing). What surprised me about Opus 4.7 as a build executor (its literalism on scope, its parallel-tool-call efficiency, its tendency to over-emphasize when the prompt did).
- "What I learned about harness engineering as a discipline." How the Quality Contract held up under real building. Whether the threat model's six threats were the right framing or whether I'd reorganize it next time. The drift between "expected" and "validated" findings.
- "What comes next." Jetson execution. Windows execution. The continuous-revision operational model. The residual-risk findings carrying their reconsideration triggers. The agentcontrolstandard.ai swap-in candidate. The repo is born public; revisions land as the harness evolves.
- "How to contribute." Brief: this is a personal reference repo. Issues and discussion are welcome; PRs that change locked decisions are not. Forks that adapt for other people's threat models are exactly the intended use.

**Post-launch revisions cell (keep).** As-is or with a sentence noting Operation 6 was the last operation in the original build sequence; everything after is post-launch revision.

Cell-count target: prologue 3-4 + pre-flight 1 + Phase 0 4-6 + Phase 1 4-6 + Phase 2 5-7 + Phase 3 4-6 + Phase 4 3-5 + Phase 5 5-7 + Operations 3-4 + Verification 3-4 (existing + new) + Epilogue 3-4 + Post-launch 1 = 42-58 cells.

Where Rock's voice or perspective is needed and the phase outputs don't carry it explicitly, leave a `<!-- ROCK: confirm or rewrite -->` marker. Examples of where to leave markers: subjective surprise reactions, retrospective regrets framed in first person, value judgments on specific tools. The executing session writes drafts; Rock owns the voice.

Commit message:

```
docs: deep rewrite of JOURNEY.ipynb as educational narrative

Context: Original JOURNEY was a Batch 1 scaffold with six phase cells saying "not yet started." Mac build executed but no phase prompt named JOURNEY as a deliverable, so the notebook sat at scaffold state while the rest of the repo shipped.

Decision: Rewrite as 40-60 cell educational narrative with story arc. Prologue (why, what this is, how to read), per-phase cells (context, narrative, surprises, tradeoffs, retrospective), operations cells covering post-execution work, epilogue (lessons, what's next), verification code cells, post-launch revisions.

Why: A repo whose narrative companion is "not yet started" reads as incomplete. The build's reasoning chain is the artifact's primary value per the locked decision; the notebook is where that reasoning lives in first-person form. Rock's voice owns the narrative; executing session drafts where Rock's perspective is needed and leaves <!-- ROCK --> markers for confirmation.

Tradeoff: Cell count up from 13 to ~50. The notebook becomes substantial reading. Mitigation: each phase's cells are sectioned consistently (context, narrative, surprises, tradeoffs, retrospective), so readers can skip to the section they need within a phase.
```

Commit. Push.

### Stage 5: Cross-document consistency check

After README, HARNESS_GUIDE, and JOURNEY are all written and committed, do a consistency pass:

- Every link from README to HARNESS_GUIDE, JOURNEY, foundation/, mac/, or research/ resolves.
- Every claim in README is consistent with HARNESS_GUIDE and JOURNEY.
- HARNESS_GUIDE's §4 file-by-file walkthrough matches the actual files in `mac/harness/`.
- JOURNEY's phase narratives are consistent with phase-outputs/ records and HARNESS_GUIDE's §3 layer explanations.
- No document claims a state that doesn't match Stage 0's verification results.
- Citations: every phase output cited in JOURNEY exists at the cited path. Every research document cited in HARNESS_GUIDE exists and contains what's claimed.
- The Quality Contract is described identically in README's brief mention, HARNESS_GUIDE's §7, foundation/00, and JOURNEY's epilogue. No drift.
- The five layers in HARNESS_GUIDE §3 are described identically in HARNESS_GUIDE §4 (file-by-file). No drift.
- The six threats in HARNESS_GUIDE §8 match the six in foundation/01. No drift.

Findings go in `phase-outputs/POST-MAC-6-NOTES.md` under §Consistency Check. Any drift found gets fixed in the relevant document (small fix commit per document) before declaring Stage 5 complete.

### Stage 6: Operator runbook for fresh-session behavioral verification

Write `phase-outputs/POST-MAC-6-VERIFICATION-PROTOCOL.md` as a self-contained runbook Rock executes in a separate fresh Claude Code session against any test project.

The runbook covers:

**Pre-test setup.** Open a fresh Claude Code session in any test project directory (NOT in the harness-engineering repo). Confirm the session loads the rebuilt `~/.claude/`. Run `/context` and confirm the user-level CLAUDE.md hierarchy matches what `bash scripts/drift-check.sh` reports for user-level. If they differ, the rebuilt `~/.claude/` did not load as expected; surface for investigation.

**Test 1: Deny rule enforcement.** Try a command that should be blocked by the new deny rules. Suggested test cases (each is a single Bash invocation Claude Code attempts; the test confirms the deny rule fires):

- `git push --force` (should be blocked by bash-deny-git-push-force)
- `sudo ls` (should be blocked by bash-deny-sudo)
- `claude --dangerously-skip-permissions` (should be blocked or absent from settings)
- Write to a path matching `*.env` or `.env.*` (should be blocked or prompted)

For each: try the command, record the outcome (blocked, prompted, allowed-when-shouldnt-be), capture the exact error message.

**Test 2: PreToolUse hook enforcement.** Try a command that should fire a PreToolUse hook:

- Bash with 31+ subcommands chained by `&&` (should be blocked by cap-subcommands)
- `npx -y create-react-app demo` (unpinned, should fire supply-chain hook to ask)
- `npx -y create-react-app@5.0.1 demo` (pinned, should pass supply-chain hook silently)
- Write outside cwd to a non-allowlisted directory (should fire external-write-gate)

For each: record outcome.

**Test 3: SessionStart hook execution.** Open a fresh session in a directory containing a `.claude/settings.json` or `.mcp.json` not in the audited-hashes registry. Confirm the SessionStart hook fires and either blocks or requests acknowledgment.

**Test 4: Skills load.** Trigger the mcp-server-pre-trust-audit skill (e.g., ask Claude Code to "audit this MCP server before I trust it"). Confirm the skill activates and produces the documented audit. Same for seed-evaluation.

**Test 5: Auto-mode classifier behavior.** Run a few ordinary Bash invocations and confirm the auto-mode classifier behaves per Q1's enabled-with-tightened-denies posture. Specifically: read-only commands should pass without prompt; write commands inside cwd should pass; write commands outside cwd should prompt; commands matching deny rules should block.

**Outcomes capture.** For each test, record: what was tried; expected behavior; observed behavior; pass/fail; any error messages or unexpected behavior. Append to `phase-outputs/POST-MAC-6-VERIFICATION.md` (a new file Rock creates from this runbook's output).

**On any failure.** If any test fails, do not silently fix it. Record the failure, document the gap, and decide whether the gap is a revision item (lands in post-launch revisions) or a stop-the-world item (the rebuild is broken and needs immediate attention).

This runbook is written for Rock to execute manually in a separate session. The Operation 6 executing session does not run Test 1 through Test 5 itself; it produces the protocol document.

## Deliverables

- `CHECKPOINT.md`: updated to reflect post-build, post-rebuild, post-Operation-6 state (gitignored)
- `README.md`: rewritten as front door, committed and pushed
- `HARNESS_GUIDE.md`: new, committed and pushed
- `JOURNEY.ipynb`: deep rewrite, committed and pushed
- `phase-outputs/POST-MAC-6-CONTEXT.md`: context-budget record
- `phase-outputs/POST-MAC-6-NOTES.md`: authoring decisions, deferred items, consistency-check findings
- `phase-outputs/POST-MAC-6-VERIFICATION-PROTOCOL.md`: the runbook Rock executes in a separate fresh session
- Three commits on origin/main (one per public-facing document)

## Verification

Before reporting complete:

- `python3 -c "import json; json.load(open('JOURNEY.ipynb'))"` parses (valid JSON).
- `jupyter nbconvert --to script JOURNEY.ipynb` succeeds (valid nbformat).
- `wc -l README.md HARNESS_GUIDE.md` shows README at 180-250 lines, HARNESS_GUIDE at 1500-2500 lines.
- `grep -c 'ROCK:' JOURNEY.ipynb` returns the count of Rock-markers placed.
- `bash scripts/drift-check.sh` returns 0 or WARN. The CLAUDE.md hierarchy did not grow; HARNESS_GUIDE and JOURNEY do not contribute to cached prefix.
- `git log --oneline -3` shows three commits: README, HARNESS_GUIDE, JOURNEY.
- Every cross-document link in README resolves to an existing file or section.
- Stage 5 consistency check completed with all findings either resolved or recorded in NOTES.

Report cell count for JOURNEY, line count for README and HARNESS_GUIDE, Rock-marker count, commit SHAs, and any consistency drift recorded.

## Anti-overengineering

Do not invent harness capabilities that don't exist. HARNESS_GUIDE describes what's in `mac/harness/`, not what could theoretically be there. If §4's file-by-file walkthrough finds a file that the architecture or principles documents do not explain, the gap is real and lands in NOTES, not invented coverage in HARNESS_GUIDE.

Do not lift content wholesale from foundation/ or research/. HARNESS_GUIDE cites those documents; it does not replicate them. If you find yourself copying multiple paragraphs from foundation/, restructure as citation plus brief summary.

Do not write JOURNEY in third-person or analyst voice. The narrative is first-person Rock voice. The executing session drafts; Rock owns. Where you can't draft authentically in Rock's voice, leave a `<!-- ROCK: confirm or rewrite -->` marker rather than producing pseudo-Rock prose.

Do not run the fresh-session behavioral tests yourself. The runbook is the deliverable. Rock executes it in a separate session against a separate project; the tests' outcomes flow back to `phase-outputs/POST-MAC-6-VERIFICATION.md` which Rock writes after running them.

Do not modify locked-decision artifacts. CHECKPOINT updates the state section, not the locked decisions section. README, HARNESS_GUIDE, and JOURNEY reflect locked decisions; they do not relitigate them.

If at any stage you find a genuine gap that affects what the documents should say (an undocumented behavior of Claude Code, a finding that contradicts what phase outputs claim, a layer that doesn't fit the five-layer model), stop and surface to Rock before writing around it. Documents that describe a state that doesn't match reality are worse than documents that are incomplete.

The educational tone has a specific failure mode: it slides into vendor-marketing voice. Guard against this aggressively. Test every paragraph by reading it aloud. If it sounds like a course-platform homepage, rewrite. Sentences should be quotable. If you can't imagine a sharp engineer saying it aloud, simplify.
