# JOURNEY

The chronological story of building this harness. What was tried, what worked, what surprised me, what I would do differently if I were starting over.

The structural documentation answers what the repo contains. This document answers how it got here.

## §0 Why I built this and how to read this

### §0.1 The problem

Claude Code arrived as a serious working tool. I adopted it across three machines (Mac, Jetson, Windows) and started giving it real work. Refactoring code. Running tests. Pushing to GitHub. Talking to MCP servers.

The default configuration trusted me to be paying attention. The runtime asks for confirmation on writes inside the working directory and lets reads through automatically. Outside of those defaults, the agent has whatever permissions the host operating system grants the user under which Claude Code runs.

I am that user, on three machines that hold my credentials. The cost of one mistake is high.

<!-- ROCK: confirm the framing here matches your actual concern. The text reads as risk-averse exec. If the actual concern is more specific (e.g., "I run multiple consulting engagements and a leak across them is reputational damage"), substitute. -->

When I ran the Phase 1 inventory subagent, the concrete shape of the problem surfaced in numbers.

44 in-repo `.claude/` directories scattered across cloned repositories. Two of them with wildcard `"*"` allow entries. Two with plaintext production credentials.

A plaintext Hetzner Cloud API token sitting in `~/.claude/mcp.json`.

56 dangling symlinks pointing at a directory that had not existed in months.

4311 session logs accumulated across 113 project directories, the oldest from March.

A 16-plugin enabled-plugins list, half of them at "version unknown."

None of those were catastrophic individually. They were the residue of fast adoption without a discipline for cleanup.

The 93%-of-prompts-get-approved finding from the Hughes 2026 paper, cited in the Liu et al. architecture analysis, made the asymmetry clear. My attention was the only thing standing between the agent and the credential store. My attention is not infinite.

### §0.2 The question

What would it take to harness Claude Code with security discipline without sacrificing the usefulness that made me adopt it.

Not "lock it down." Not "deny everything."

The question I wanted to answer was where the deterministic floor goes (rules that hold every time, regardless of my attention) and where the advisory ceiling goes (instructions that the model probabilistically follows, useful for posture but not enforcement).

The starting frame was that Claude Code is a serious build tool, not a chatbot. The harness around it should be treated as load-bearing software in its own right. Its own threat model. Its own quality contract. Its own version pins. Its own audit discipline.

### §0.3 The commitment

I committed to building it in public. Not as a polished product. As a worked example with the reasoning preserved alongside the configuration.

The locked decision in `CHECKPOINT.md` is that personal-specific is the value. My threat tolerance, my tool inventory, my workflow, my Claude Code version pin. Someone else's harness needs to reflect their decisions, not mine. The point is the discipline, not the dotfile.

The repo structure followed. Shared `foundation/` for the platform-agnostic thinking. Three platform sections (`mac/`, `jetson/`, `windows/`) for per-machine implementation. `research/` for the source documents. `operations/` for the post-Phase-5 work that landed the build into the operational environment.

The README is the front door. USER_GUIDE is the day-to-day operational reference. HARNESS_GUIDE is the design reference. This document is the story.

### §0.4 What this document is and isn't

This is a builder's retrospective written for other builders.

It is not a tutorial (that is HARNESS_GUIDE).

It is not an operational reference (USER_GUIDE).

It is not a corporate post-mortem or a sales narrative. It is the reasoning chain that produced the rest of the repo, written in first-person voice, honest about what did not work alongside what did.

Each phase has its own section with a consistent shape. Context (what the phase was for). Narrative (what happened). Surprises (what did not go as expected). Tradeoffs (the decisions that turned on a tradeoff). Retrospective (what I would do differently). Not every phase needs all five. Some merge naturally.

Where I left a `<!-- ROCK: confirm or rewrite -->` marker, the executing session was unsure how to draft authentically as me from the evidence available. The phase outputs record decisions and findings. They do not always record how I felt about them. The markers are honest signals about which sentences need my voice rather than the executing session's drafted approximation.

### §0.5 How to read this alongside the repo

`README.md` is the front door at 180 lines. Read it first if you want to know what this repo is and who it is for.

`USER_GUIDE.md` answers "what does this harness do day to day" at 1356 lines. Read it if you have the harness loaded (or are evaluating loading it) and want to know what fires when, what messages appear, how to troubleshoot.

`HARNESS_GUIDE.md` answers "how is it designed and why" at 1505 lines. Read it if you want to understand the design rationale, the file-by-file anatomy, the layer model.

`foundation/` carries the platform-agnostic thinking. The Quality Contract (`00-quality-contract.md`). The threat model (`01-threat-model.md`). The architectural principles (`02-architectural-principles.md`). The seed evaluation methodology (`03-seed-evaluation-methodology.md`). The research references (`04-research-references.md`).

This document is the story. Read it if you want to understand how the discipline played out in practice.

The phase outputs in `phase-outputs/` are the durable receipts behind every claim here. Where this document cites a finding or a decision, the phase output records the original. The narrative is the story. The phase outputs are the source.

### §0.6 What you will not find here

A few things this document does not do.

It does not summarize the foundation documents. The Quality Contract, the threat model, the architectural principles, and the seed evaluation methodology are the load-bearing thinking the rest of the repo rests on. Reading them is the prerequisite. This document assumes you have read them or will read them when you need the principle behind a decision recorded here.

It does not duplicate the research summaries. The three research documents under `research/` carry their own framing. Liu et al. on Claude Code v2.1.88 internals. The SAGE document on harness engineering as a discipline. NIST SP 800-218 on secure development. This document cites them by section when a specific fact lands here, but the documents themselves are the reference.

It does not catalog every phase output. The phase outputs in `phase-outputs/` number around 30 files. Each one records the deliverables and rationale of a phase or operation. This document cites them where the cited section informs the narrative. The full catalog would be a different document.

It does not narrate decisions that landed without surprise. Many decisions across the build went exactly as the prompt described. Those land in the phase outputs as recorded outcomes. They do not need a narrative section here. The narrative focuses on the friction, the surprise, the calibration, the tradeoff.

---

## §1 Pre-flight

Before any phase ran, I read the three research documents end-to-end.

Liu et al. on Claude Code v2.1.88 internals. The SAGE document on harness engineering as a discipline. NIST SP 800-218 on secure development. The three together set the vocabulary the rest of the build uses.

The SAGE document was the synthesis effort that settled the working definition of harness engineering as a "deterministic software envelope around a non-deterministic model." Nine identifiable components. Agent loop, instruction layer, tool pool, permission layer, context pipeline, sandbox, MCP integration, subagent delegation, persistence.

The nine-component model became the substrate for the rest of the build. Whenever I referred to a "layer" in subsequent phases, I was usually pointing at one of those nine.

The pre-flight prompt itself produced `phase-outputs/PREFLIGHT.md`.

I confirmed Claude Code v2.1.138, Node v24.10.0, Python 3.13.9 (Anaconda), Homebrew 5.1.10, macOS 26.3 on Apple Silicon. The five foundation documents were present and well-formed. The three research documents were present.

The drift check returned 188 lines worst-case across the project hierarchy. Inside the 250 target. Well inside the 400 cap.

Four tooling gaps surfaced.

shellcheck, markdownlint-cli2, and detect-secrets were not installed.

semgrep was installed but broken. An `opentelemetry-sdk` version conflict in the Anaconda environment raised an `ImportError` at load.

I deferred all four to Phase 2 for the install-or-substitute decisions.

The user-level CLAUDE.md hierarchy was 5.7x larger than the project's. The pre-flight context measurement showed 16.6k tokens loaded from the SuperClaude framework files at user level versus 2.9k tokens from the project root.

The drift-check at the time scoped only to the project hierarchy and did not see the user-level chain. That asymmetry became Phase 2 Q10's question. Should the drift check widen.

Surprises: none worth recording at this stage. The pre-build planning held up.

<!-- ROCK: confirm. The original ipynb scaffold cell said the same thing. If there was friction during pre-flight you remember (e.g., adversarial review pushback that did not land in PREFLIGHT.md), this is where to record it. -->

---

## §2 Phase 0: goals and architecture

### §2.1 Context

Phase 0 had two jobs.

First, capture the environment baseline so the rest of the build had a fixed reference point.

Second, settle which `<TBD-PHASE-0>` blocks in `mac/ARCHITECTURE.md` resolved at this phase versus deferred to Phase 2 (architecture interview), Phase 3 (deterministic layer), or Phase 4 (extension layer).

The phase output `PHASE-0-DECISIONS.md` records both.

### §2.2 Narrative

I confirmed the environment versions.

`sw_vers` returned macOS 26.3, build 25D125, Darwin 25.3.0. The pin entry in `mac/ARCHITECTURE.md` got that value. The re-evaluation trigger landed at "next macOS major release."

`node --version` returned v24.10.0. From Homebrew at `/opt/homebrew/bin/node`. The pin landed. The re-evaluation trigger: Node LTS major (v26 LTS expected in October 2026).

`python3 --version` returned 3.13.9 from `/opt/anaconda3/bin/python3`. The Anaconda distribution rather than Homebrew Python. The pin landed. The re-evaluation trigger: Python minor release.

`claude --version` returned 2.1.138. Per QC.5 the harness pins to a minor-version range. Threat-model assumption 1 (foundation/01-threat-model.md) names v2.1.x explicitly as the assumption-bearing range. The pin landed as `v2.1.*`. Re-evaluation on minor bump (v2.2.x).

`brew --version` returned 5.1.10. Recorded for completeness. Not a threat-model dependency.

The cache-lineage decision settled here. Default model `claude-opus-4-7`. Default subagent model `claude-opus-4-7`. Same family. Share cache per QC.4a.

The daily-driver workload may favor Sonnet for cost-sensitive routine work. The operational override at session start is `--model sonnet`. The build itself runs on Opus because the work is high-stakes architectural reasoning where the cost-cache tradeoff favors Opus.

I observed nine always-loaded built-in tools and twenty-two deferred tools loaded on demand via `ToolSearch`.

Always loaded: Agent, AskUserQuestion, Bash, Edit, Read, ScheduleWakeup, Skill, ToolSearch, Write.

Loaded on demand via ToolSearch: CronCreate/Delete/List, EnterPlanMode, EnterWorktree, ExitPlanMode, ExitWorktree, LSP, ListMcpResourcesTool, Monitor, NotebookEdit, PushNotification, ReadMcpResourceTool, RemoteTrigger, TaskCreate/Get/List/Output/Stop/Update, WebFetch, WebSearch.

The default subset matches the documented `getAllBaseTools()` surface from Liu et al. §6.2. Phase 3's deny rules would target the always-loaded set plus any deferred tool that gets resolved.

The auto-mode classifier decision deferred to Phase 2.

Phase 0 set the default to disabled per Principle 2 (least privilege), with the Phase 2 interview asking me to confirm or override. The 0.4% false-positive rate (Hughes 2026, cited in Liu et al. §5.3) is empirically small. The threat model worries about credentials and push access. The daily-driver friction was a tradeoff I wanted to think through deliberately.

The daily-driver harness path (in-repo, symlinked, or hybrid) deferred to Phase 2.

The `~/.claude/` tree already carried heavy personal configuration. Symlinking the harness's CLAUDE.md over it would be destructive and needed an explicit decision. Phase 2 was the right place.

Bash sandboxing deferred to Phase 3.

Claude Code v2.1.138 CLI exposes no direct sandbox toggle (verified by `claude --help`). The permission system (deny rules + interactive approval) is the primary enforcement layer per Principle 1. The macOS sandbox-exec primitive is available at `/usr/bin/sandbox-exec` but Claude Code's documented use of it is not visible from the CLI surface. Phase 3 would verify the `sandbox` block in `mac/harness/settings.json.template` behaviorally and decide between enabling, removing, or replacing with permission-layer equivalents.

Network egress per MCP server deferred to Phase 4. Per-server constraints land with each server's allowlist entry as Phase 4 adopts servers.

Session log retention deferred to Phase 2. The machine currently held 4311 session logs across all projects. Oldest from March 19. The decision involved disk usage (the harness-engineering session alone was approaching 1MB after a half-day's work), privacy posture (session logs contain conversation history including any sensitive paths or values discussed), and replay value.

### §2.3 Surprises

The user-level CLAUDE.md hierarchy was 5.7x larger than the project's.

I had been carrying the SuperClaude framework on this machine for months and had never measured it. 16.6k tokens across 15 files (FLAGS.md, PRINCIPLES.md, RULES.md, five MODE_*.md, six MCP_*.md). The project root CLAUDE.md was 2.9k tokens.

The drift check measured only the project hierarchy and gave a comfortable 188-line worst-case. The actual cached prefix was nearly six times that.

That asymmetry surprised me.

<!-- ROCK: confirm. Specifically: did the 5.7x ratio make you reconsider how much of your daily-driver behavior was being shaped by SuperClaude rather than the harness? The Phase 1 finding that surfaced the @import chain made the mechanism explicit, but the realization that "the cached prefix is mostly SuperClaude" lands here in Phase 0. -->

The Phase 0 prompt itself flagged a scope inconsistency.

The `mac/harness/settings.json.template` file carried `<TBD-PHASE-0>` markers but the Phase 0 prompt's scope block excluded `mac/harness/` from this phase's writes.

Phase 0 recorded the decisions in `mac/ARCHITECTURE.md`. Phase 3 (which owns the settings.json wiring) would propagate them.

PHASE-0-DECISIONS.md flagged this for the next prompt-authoring revision. Either Phase 0's scope should include the template, or Phase 3's prompt should explicitly say "propagate Phase 0 decisions from ARCHITECTURE.md into settings.json.template before doing anything else."

The Anaconda-installed semgrep was broken with an opentelemetry-sdk version conflict.

Phase 0 noted it and left the resolution to Phase 3 (tooling install/substitute). The broken state was a known item, not a surprise.

The `<TBD-PHASE-0>` verification grep was over-broad.

The Phase 0 prompt's verification command `grep -c '<TBD-PHASE-0>' mac/ARCHITECTURE.md` returned a non-zero count even after all the actual blocks were filled, because the convention is described in prose on lines that contain the marker as a string. The strict check needed to exclude convention-description references.

This was the first concrete instance of an audit-pattern that would recur. Published prompts encode assumptions about the world that the world later contradicts in small ways. PHASE-0-DECISIONS.md flagged the refinement for the next prompt authoring.

### §2.4 Tradeoffs

**Opus-everywhere versus mixing in Sonnet.**

Same-family cache lineage was the deciding factor. A mixed parent/subagent model selection costs cache hits on the subagent invocation. A Phase-1-sized inventory scan spawns enough subagents that the cache loss compounds noticeably.

Opus-only kept the cache lineage clean. The cost of the higher per-token Opus rate against the Sonnet rate was real but bounded. The cache-economy gain was larger over a build of this size.

**Brewfile.lock versus direct version pins.**

Deferred to Phase 3. The QC.1 PS practice group requires pinned dependencies. Brewfile.lock is one mechanism. Direct pins in CI plus conda-lock for the Anaconda half is another. Phase 3 would pick.

**Network egress monitor evaluation.**

Deferred to Phase 4 for evaluation. Phase 1 had not yet surfaced findings. Phase 4 would have the seed evaluation context to decide whether to install one.

The eventual decision was to skip the OS-level monitor (Phase 2 Q7). The MCP allowlist plus the per-server six-check audit plus the deny rules carry the egress defense. The OS-level monitor would add real-time decision burden which the 93%-approval data says is unreliable.

### §2.5 Retrospective

The prompt-authoring inconsistency (settings.json.template TBD markers out of Phase 0's scope) is the kind of thing the Reviewer subagent should catch on the prompt itself, not only on the prompt's outputs. A future revision of the build sequence should run a "do the prompts have the scope they claim" pass before phase execution.

The verification grep over-broadness is a smaller version of the same lesson. Verification commands need to be tested against the failure case (no markers remaining), not only the happy case (some markers remaining). A `grep -c` that counts prose references as remaining work is a verification command that does not verify what it claims.

I would also widen the pre-flight context measurement to include the user-level chain explicitly. Phase 0 happened to surface the 5.7x asymmetry through `/context` observation. A discipline that depends on me thinking to run `/context` is fragile. The drift-check widening that landed in Operation 1 (Post-Mac 1) closed this gap deterministically.

---

## §3 Phase 1: discovery

### §3.1 Context

Phase 1's job was discovery. What is on the machine that the harness needs to know about.

The phase ran in plan mode (read-only) with a general-purpose inventory subagent dispatched to handle the file-scan work. The synthesis happened in the main session.

The inventory discipline followed the six sections the inventory subagent's role definition specifies. User-level Claude Code configuration. In-repo `.claude/` directories. CLI tools beyond pre-flight. MCP server installations. Pre-existing skills/hooks/agents. Seed candidate status.

The subagent's report fed into `phase-outputs/INVENTORY.md` (212 lines of synthesis). A second pass produced `phase-outputs/CONFLICTS.md` for cross-checks against Phase 0.

### §3.2 Narrative

The subagent ran for ~7 minutes wall time. 154,700 tokens. 52 tool uses. Same-family Opus cache lineage with the parent kept the budget tractable.

The output landed as a structured 600-800 line markdown document with each of the six sections plus a threat-relevant aggregate.

The headline finding: 44 `.claude/` directories scattered across the homedir.

Most were minimal `settings.local.json` artifacts from course projects or one-offs. A handful were audit-critical.

The `ai_governance_toolkit` and `ai_governance_toolkit_website` repositories carried wildcard `"*"` allow entries in their `settings.json`. The website repo additionally held plaintext Neon Postgres URLs (DEV and PROD) in its `settings.local.json`.

The RCAP repo's `settings.local.json` was 40,847 bytes with 700+ entries of accumulated session-by-session permission grants. Including broad mutating commands like `Bash(/bin/bash:*)`, `Bash(rm:*)`, `Bash(terraform:*)`, plus aws/docker/openssl wildcards.

The user-level `~/.claude/mcp.json` declared one MCP server, `hetzner`, with the API token in plaintext.

The 16-plugin `enabledPlugins` list was at "version unknown" for several entries. A pin failure against QC.5 that I had not noticed.

4311 session logs across 113 project directories. The oldest from March 19.

56 dangling symlinks under `~/.claude/commands/zerg/`. Every file in the directory pointing at a path that no longer existed.

CLI tool inventory beyond pre-flight surfaced useful adjacencies.

`gitleaks` 8.30.0 was installed. Good signal for the secret-scan substitution.

`trivy` 0.69.0 installed.

`gh` 2.92.0 installed.

`jq` 1.7.1, `uv`/`uvx` 0.8.14, `docker` 28.0.1, `gpg` 2.5.18, `pyenv` 2.4.12, `pipx` 1.7.1 all installed.

The notable absences. `syft`, `grype`, `cyclonedx-cli`, `cosign`, `osv-scanner` (the SBOM/SLSA tooling I would have wanted for QC.1 alignment in a regulated environment but was not adopting at the personal-harness scale).

`shellcheck`, `markdownlint-cli2`, `detect-secrets` confirmed missing. Same as pre-flight.

Beyond `~/.claude/` and plugin trees, no Rock-authored harness fragments were found.

One MemPalace LaunchAgent ran daily at 03:00 (created by the MemPalace package, not by me). No standalone hook scripts in `~/bin/` or `~/scripts/`. No crontab entries referenced Claude.

Seed pre-filter status against the foundation/03 candidate set.

`obra/superpowers` was already installed as a plugin (v5.1.0). Adoption candidate confirmed.

`anthropics/claude-code` plugins marketplace was registered. Adoption candidate confirmed.

MemPalace was installed (v3.3.2). Adoption candidate confirmed.

Serena was installed but disabled in user settings. Deferred to Phase 4 with the user-disabled signal noted.

`affaan-m/everything-claude-code`, `disler/claude-code-hooks-mastery`, `cosai-oasis/project-codeguard` were not present anywhere on the machine. Pre-filter would re-run on each in the relevant phase.

### §3.3 Surprises

The 44 `.claude/` directories was higher than I had expected.

<!-- ROCK: confirm the surprise is real. If you had a sense that the count was that high before the inventory ran, replace with a softer phrasing. -->

The two HIGH-severity findings (Hetzner API token plaintext, Neon Postgres credentials plaintext in the website repo's settings.local.json) were both real and both predated this build.

The mechanism in both cases was the same. Claude Code accepts `Bash(DEV_DATABASE_URL=...)` permission grants and the value lands in the settings file. The fix is structural (env-var indirection plus secret-store backing), not a one-time cleanup.

The RCAP `settings.local.json` at 40,847 bytes with 700+ permission entries was the cleanest illustration of the "approve once, persist forever" failure mode I had under-appreciated.

The pattern across in-repo settings files is monotonic growth. Without a per-session reset or a periodic prune, the file accumulates everything ever approved. Phase 3's deterministic-layer work would consider whether to ship a periodic-prune hook (it did not. The threat surface is auditable per-repo and the operational discipline is to run the audit when an unfamiliar `.claude/` shape surfaces).

The Q5 (every-clone hash-gated audit) cadence became materially more expensive than I had anticipated when I drafted the question.

44 existing `.claude/` directories on the machine plus every future clone meant the audit would block every cold-start session against every cloned repo until I added the hash to the registry.

The bulk-acknowledge tool became a known gap that Phase 3 acknowledged and Operation 4 partially addressed.

### §3.4 Tradeoffs

**Pre-trust audit cadence versus operational friction.**

Q5's "every clone, hash-gated" was the strict choice. The alternative was "periodic re-audit every N days" which loosens the gate but widens the window for a hostile change to slip in.

I chose strict. The operational cost is real. The bulk-acknowledge tool is the mitigation against the legacy-clone backlog.

**Inventory subagent dispatch versus inline scanning.**

The inventory work touched 27 top-level `~/.claude/` files. 21 subdirectories. 16 plugin trees. 44 repo `.claude/` directories. Plus the CLI tool surface.

Doing it inline would have burned the parent session's context on the file reads.

The subagent dispatch kept the parent context clean for synthesis and produced a structured report I could fold into INVENTORY.md largely verbatim. The cost was the per-invocation Opus subagent fee. Same-family cache lineage made it tractable.

### §3.5 Retrospective

I would run the inventory subagent on a more aggressive cadence. Phase 1's snapshot is now over a month old. The 44-directory count and the 4311-session-log count are both monotonically growing in the absence of an active pruning cadence.

The Stop hook handles session log retention going forward. The in-repo `.claude/` count needs occasional attention. Quarterly is probably the right cadence for a personal harness. Monthly for a multi-machine setup with active development across them.

The two HIGH-severity findings (Hetzner token, Neon credentials) had accumulated over months. The discipline I would impose on a fresh fork is to run a Phase 1-style scan on day one, not only at fork time.

The CONFLICTS.md cross-check pass surfaced two clarifications (the 47-line CLAUDE.md vs the 17-line `/memory` count, the semgrep re-verification skipped) but no hard contradictions.

The discipline of reading Phase 0 against Phase 1 line-by-line caught the small drifts before they became larger. I would keep that as a standard inter-phase discipline.

---

## §4 Phase 2: architecture interview

### §4.1 Context

Phase 2 was the densest phase because it was where the calibrated decisions landed.

The format was the `AskUserQuestion` interview tool with eleven planned questions covering hook coverage, seed pre-filter scope, platform-specific divergences. The output was `phase-outputs/ANSWERS.md` with the recorded decisions and one-paragraph implications per answer.

QUESTIONS.md captured the eleven questions before any was asked. Each entry recorded the decision the question forced, the options presented, the locked context (foundation document or research source), and the strongest counter-argument I could write to the most likely answer (the "steel-man for the alternative").

The discipline was to write the steel-man before I knew what I would choose. The steel-man kept me from anchoring on the recommended option.

### §4.2 Narrative

The interview ran question by question.

**Q1 (auto-mode classifier):** Enabled.

The Phase 0 default had been Disabled per Principle 2. The Phase 2 interview asked me to confirm or override. I overrode.

The 0.4% false-positive rate is empirically small and the daily-driver workload's interactive-approval friction compounds across many sessions. The Phase 3 deny rules became the deterministic floor under the classifier rather than a substitute for it.

**Q2 split into Q2a + Q2b.**

Q2 was originally a single multiSelect for six threats. AskUserQuestion enforces a 4-option maximum, so the question was rejected at tool-call time.

T4 (the 50-subcommand bypass) was already covered by Q6 (the subcommand chain cap), so I dropped T4 from Q2 and split the remaining five threats by category. Q2a for input-side (T1, T2, T5). Q2b for execution-side (T3, T6).

**Q2a (input-side threats).**

For Q2a I asked the model for its recommendations, naming "balance between security and friction" as the framing. The model walked the per-threat cost-benefit.

T1 (prompt injection): skip the hook because content-scanning every tool return carries unbounded latency. The runtime's classifier plus the CLAUDE.md advisory plus my vigilance is the calibrated trade.

T2 (supply chain): hook, narrow to unpinned-version patterns.

T5 (cache poisoning): hook on cached-prefix writes.

I affirmed with "yes, feels right."

**Q2b (execution-side threats).**

The same exchange covered Q2b.

T3 (pre-trust init): SessionStart audit hook.

T6 (hostile MCP): defer to Phase 4 allowlist (no execution-time hook).

**Q3 (daily-driver harness path).**

The question I had not anticipated correctly. The three options I had planned (in-repo only, symlinked, hybrid) all assumed the existing `~/.claude/` would persist as personal configuration.

My answer was a fourth option. Rebuild the entire `~/.claude/` tree from scratch as a deliverable of this build, then initialize a private git repo at `~/.claude/` for change tracking.

The Q3 answer reframed Phase 5's scope (it now produced new `~/.claude/` content as deliverables) and Q4 and Q10's framing (auto-memory and drift-check both now operate against a rebuilt baseline rather than an in-place overlay).

**Q4 (auto memory):** Enable.

The cross-session memory accumulation was useful enough to keep, with the QC.4b context discipline as the guard against bloat.

**Q5 (pre-trust audit cadence):** Every clone, hash-gated.

The 44-directory backlog became a known operational item.

**Q6 (subcommand chain cap):** 30.

Below the documented 50-subcommand bypass class for defense in depth.

**Q7 (network egress monitor evaluation in Phase 4):** Skip.

The MCP allowlist plus the per-server six-check audit plus the deny rules carry the egress defense. The OS-level monitor would add real-time decision burden which the 93%-approval data says is unreliable.

**Q8 (cosai-oasis/project-codeguard placement):** Phase 3 (deterministic-layer fit).

I added a clarification that Q8 was about the CLASS of deterministic-layer security tools, not only the named candidate. agentcontrolstandard.ai surfaced as a future swap-in I am working on separately.

**Q9 (`skipDangerousModePermissionPrompt: true`):** Remove.

The setting bypassed the bypass-mode safety dialog. Removing it meant every `--dangerously-skip-permissions` invocation carries the dialog. The narrowing came later (2026-05-11, during Operation 6 closeout) when the runtime kept rewriting the key after every removal.

**Q10 (drift-check widening):** Widen.

The drift-check should measure user-level cached-prefix content too. The implication landed as Post-Mac 1 (drift-check widening) after the Phase 5 audit failed to catch the gap.

**Q11 (session log retention):** 90 days.

The Stop hook would prune older logs with a 24-hour marker guard.

### §4.3 Surprises

Q3's reframing surprised me.

<!-- ROCK: confirm. The phase-output records the rebuild decision but it was a genuine in-the-moment shift from the question I had drafted. If you had been thinking about a rebuild before the interview surfaced it, the framing here changes. -->

Q2a needed clarification before I could choose.

The original options forced a security-vs-friction tradeoff per-threat, and I wanted help calibrating where the line should be for a daily-driver workload.

The model's recommendation framing was useful. I affirmed rather than re-asked because re-asking via the tool after I had already chosen would be process theater. ANSWERS.md records the workflow deviation explicitly.

The agentcontrolstandard.ai surfacing through Q8 was a project-memory item I had not planned to introduce.

The Q8 question was about codeguard's placement. My answer mentioned the agentcontrolstandard.ai future swap as context.

The build's discipline was to record project-memory items as they surfaced (in MemPalace as a knowledge-graph fact, in the phase notes as a forward-looking entry). Phase 3 built the integration shape for the deterministic-layer security tool class so the future swap-in had a place to land.

Q5's cost surprised me as the answer landed.

I had drafted Q5 thinking of the future-clone case (every new `git clone` triggers an audit). The 44-directory legacy backlog made the operational cost much higher than the future-marginal cost.

The bulk-acknowledge tool became a known gap.

### §4.4 Tradeoffs

**Auto-mode on (Q1) traded the 0.4% false-positive rate for the daily-driver friction reduction.**

The deny rules became the deterministic floor. If the false-positive rate had been higher (1-2%), the calculation would have flipped.

**30-subcommand cap (Q6) traded operational ceiling for defense in depth.**

A higher cap (40, 50) would have produced fewer hook denials on legitimate long chains. Lower (10) would have caught more cases at the cost of friction.

30 was below the 50-subcommand bypass threshold with enough margin that the runtime's own fallback would not kick in before the harness's hook did.

**Rebuilding entire `~/.claude/` (Q3) traded build effort for clean operational baseline.**

The rebuild became the largest single act of the build (Operation 4). The alternative was an in-place overlay with all the inherited cruft preserved by default.

The rebuild let me audit and resolve the HIGH-severity findings (plaintext secrets, dangling symlinks) at the same point as landing the harness deliverables.

**Q5 every-clone-hash-gated traded operational friction for security guarantee.**

The strict cadence catches every change. A periodic cadence (weekly, monthly) would have been less friction but widened the window.

I chose strict because the cost of a hostile change slipping through the window was higher than the cost of the audit work.

**Q11 90-day retention traded replay value against privacy and disk usage.**

The alternatives were indefinite (privacy and disk-usage cost), 30 days (loses replay value for medium-horizon work), and 7 days (loses too much).

90 days is the calibrated middle. The Stop hook's 24-hour marker prevents per-session overhead.

### §4.5 Retrospective

The Q3 option set was too narrow.

I drafted three options assuming the existing `~/.claude/` would persist. The right framing surfaced through my own clarification.

Future architecture interviews should include an "other" option with structured follow-up explicitly. The AskUserQuestion tool supports "Other" as an automatic affordance, but the prompt-author discipline of writing options that span the actual decision space matters too.

Q2a needed clarification before I could choose.

The pattern (asking the model for its recommendations, then affirming) was a workflow deviation from the one-AskUserQuestion-per-question discipline. I do not regret it. The recommend-and-affirm flow produced a faster decision with better calibration.

The discipline lesson: AskUserQuestion is a tool for forcing a structured choice, but the structure can include "ask for a recommendation and affirm" when the operator wants help calibrating.

Q9's narrowing in Operation 6 (months later) is the cleaner example of a Phase 2 answer that needed adjustment after operational evidence.

The original Q9 was "remove the key." The runtime kept rewriting the key. The narrowing said "the deny rule applies to model-proposed invocations only. Operator-initiated bypass at session start is permitted. The key is the documented expected state for that case."

The discipline of revisiting answers when operational evidence contradicts them is the right pattern. The Phase 2 prompt should have said so explicitly. Instead the lesson surfaced through the operational drift.

The CONFLICTS.md cross-check pass that ran after Phase 1 was a useful audit pattern. I did not run an equivalent for Phase 2 (no inventory cross-check existed because the answers were calibrated rather than discovered).

A Phase-2-vs-Phase-1 cross-check (do the calibrated answers align with the inventory findings?) would have been a useful additional discipline. For a fork, that pass is worth running.

---

## §5 Phase 3: deterministic layer

### §5.1 Context

Phase 3 was where the deterministic floor landed. Hook scripts. Deny rules. settings.json populated. Sandbox configuration.

The Phase 2 answers determined what got built. Phase 3's job was to write the artifacts.

The phase output `PHASE-3-NOTES.md` records the per-hook and per-rule rationale plus the deviations from the Phase 3 prompt's literal scope.

### §5.2 Narrative: the six hooks

Six hook scripts, all in Python. The Phase 3 prompt permitted Python or shell. I standardized on Python because every hook parses JSON on stdin and emits JSON on stdout, and Python's `json` module is a cleaner substrate than `jq` invocations.

The shellcheck verification step became vacuously clean (no shell scripts to lint). SAST coverage on the Python files would land in Phase 5 polish after the semgrep clean install.

**`PreToolUse-bash-cap-subcommands.py`.**

Denies Bash chains over 30 subcommands. Quote-aware tokenizer counts the four chain operators outside quoted regions. Verified with two cases (3 subcommands allow, 35 subcommands deny).

The implementation tracks quote state because backslash-escaped quote sequences in malicious payloads should inflate the deny side, never the allow side.

**`PreToolUse-external-write-gate.py`.**

Asks confirmation on Write/Edit/MultiEdit/NotebookEdit targeting paths outside cwd. The Principle 3 (reversibility) enforcement.

Resolves both raw path and cwd to absolute, then uses `os.path.commonpath` for containment. Cross-drive cases (Windows) raise `ValueError`. The hook catches it and treats the path as outside cwd, which is the safe default.

**`PreToolUse-supply-chain-bash-checks.py`.**

Asks confirmation on supply-chain risk patterns. Phase 2 Q2a T2 narrow scope.

Six pattern matchers. `npx -y` unpinned. `uvx --from git+` without ref. `@latest` tags. `npm install ...@latest`. `pip install` without version constraint. `curl|sh` and `wget|bash` patterns.

Pinned installs pass freely. `pip install requests==2.32.0` allow. `pip install requests` ask. `npx -y create-react-app@5.0.1 demo` allow. `npx -y create-react-app demo` ask.

**`PreToolUse-cached-prefix-write-gate.py`.**

Asks confirmation on writes to cached-prefix files. CLAUDE.md anywhere in cwd, `foundation/` directory, user-level `@import` targets in `~/.claude/`.

The Phase 3 deviation. Implemented as PreToolUse rather than the Phase 2 prompt's suggested PostToolUse. PostToolUse fires after the write has landed, providing audit but not gating. Phase 2's intent was gating, which only PreToolUse delivers.

**`SessionStart-audit-claude-config.py`.**

Blocks session start when an in-repo `.claude/settings.json`, `.claude/settings.local.json`, or `.mcp.json` has a sha256 not in `~/.claude/audited-hashes.json`. The Q5 every-clone cadence enforcement.

Registry created lazily on first audit. The hook returns exit 2 with stderr plus an `additionalContext` block. The dual signal hedges across the version-dependence of SessionStart exit-code semantics (F09 in the Phase 5 audit).

**`Stop-prune-session-logs.py`.**

Deletes session logs older than 90 days from `~/.claude/projects/`. The Q11 retention enforcement.

24-hour guard via `~/.claude/.last-cleanup-90d` marker prevents per-session overhead. The aggregate `~/.claude/history.jsonl` is exempt (rolling buffer for cross-session aggregate).

### §5.3 Narrative: the six deny rules

Six deny rules. Five carrying patterns. One documenting the structural mechanism for MCP server denial.

**`bash-deny-git-push-force.md`.**

Three patterns: `--force`, `-f`, `--force-with-lease`.

The lease check protects only against losing intermediate commits. An unauthorized push of new history still happens. Including `--force-with-lease` in the deny set means I get the friction of removing the rule for legitimate force-push work, but I do not get a silent surprise from a corrupted-recovery flow.

**`bash-deny-dangerously-skip-permissions.md`.**

Initially two patterns (canonical + wrapped). Phase 5 audit dropped the wrapped pattern (F02. Empty-prefix syntax was unsupported in v2.1.x).

The narrowing in Operation 6 reframed the rule as model-proposed-only. Operator-initiated bypass is permitted.

**`bash-deny-sudo.md`.**

Single pattern.

The harness has no legitimate need for root. Package installs use Homebrew (no sudo). User-scope pip and npm (no sudo). Ad-hoc commands stay in the user's home and the working directory.

**`bash-deny-rm-rf-root.md`.**

Initially five patterns. Phase 5 audit dropped two as redundant (F06. The broader `Bash(rm -rf /:*)` already covers `rm -rf /Users/...` via the `:*` glob).

Three remain. `/`, `~/`, `$HOME`.

Scoped `rm -rf /path/inside/cwd/` is not blocked by these patterns and falls to interactive approval under default mode.

**`filesystem-deny-write-secrets.md`.**

Ten patterns (Write and Edit, five path globs each: `.env`, `.env.*`, `secrets/`, `.secrets/`, `credentials.json`).

The pattern dialect is documented but the exact glob behavior is not visible from `claude --help` (F11 residual risk. Runtime verification deferred to the post-launch `~/.claude/` rebuild).

**`mcp-deny-server-prefix-default.md`.**

No pattern. Documents the structural mechanism.

`mcpServers: {}` plus Phase 4's explicit allowlist entries means unlisted servers do not reach the tool pool. A blanket `mcp__*` deny would override narrower allows due to deny-first ordering.

The mechanism works because tool pool assembly happens before deny evaluation. The runtime calls `getAllBaseTools()` to assemble the pool. The pool composition is filtered by which MCP servers are registered. Deny rules then apply to the assembled pool. An unregistered MCP server's tools never enter the pool, so no deny rule ever needs to evaluate against them.

### §5.4 Surprises

The supply-chain hook regex was structurally broken for two pinned cases.

**F04.** `uvx --from git+...@<ref>` got false-positively flagged as unpinned because the regex's `\S+` was greedy and consumed the URL including the `@<ref>` pin. The negative lookahead then scanned text after the URL token and never saw the ref.

**F05.** `npx -y <pkg>@<version>` got false-positively flagged because the regex did not consider whether the package argument carried a version suffix.

The two-step rewrite (regex extracts the target token, then a Python function checks pin presence) fixed both.

The fix used per-pattern Python functions because the pinning markers differ across package managers (npm scoped names like `@scope/pkg@version`, git refs after `git+` prefix, pip constraint tokens). The single-regex-with-negative-lookahead approach was structurally inadequate. The two-step shape is the correct calibration.

The Phase 3 verification commands had not caught either bug because the test cases I had drafted did not exercise the relevant edge.

The lesson: verification commands need to be tested against the failure case (the case the hook is supposed to handle correctly), not only the happy case (the case the hook obviously handles).

F04 and F05 surfaced in Phase 5 audit only because the Reviewer subagent constructed test inputs from the rule files' own examples and exercised them against the implementation.

The cached-prefix hook's PreToolUse-vs-PostToolUse choice was a small surprise.

The Phase 2 prompt had said PostToolUse. I switched to PreToolUse during Phase 3 because PostToolUse fires after the write has landed and provides audit but not gating. The Phase 2 intent was gating.

The deviation was deliberate and recorded. The pattern of "Phase 2 says one thing, Phase 3 implementation reveals a better thing" is fine when the deviation is named.

### §5.5 Tradeoffs

**Python uniformly versus mixed Python/shell.**

Phase 3 chose Python uniformly. The cost was the loss of shellcheck coverage on the hook scripts (vacuous now). The benefit was JSON parsing cleanliness and a single-language testing surface.

**Cached-prefix hook scope (Phase 2 Q2a T5 versus broader).**

Phase 2 Q2a's T5 election scoped to cached-prefix files. CLAUDE.md hierarchy, `foundation/`, user-level `@import` targets.

The broader scope (also gating writes to `mac/harness/settings.json`, `mac/harness/hooks/`, `mac/harness/rules/`) would have caught the harness's own deterministic-layer files.

Phase 5 audit F10 noted the gap. The disposition was "accept residual risk" because git pre-commit plus branch protection plus PR review covers the deterministic-layer files at the public-repo level.

The tradeoff was conscious. Post-launch revision can extend the gate if a specific failure mode surfaces.

**Hook execution path (PreToolUse versus PostToolUse for the cached-prefix gate).**

PreToolUse asks before the write happens (gating). PostToolUse fires after the write has landed (audit). Phase 2's stated intent was gating. PreToolUse was the implementation that delivered it.

The PostToolUse audit-trail value is preserved as an option for future revisions if a specific failure mode demands it.

### §5.6 Retrospective

The supply-chain hook regex bugs are the clearest "I would do this differently" item from Phase 3.

The lesson. A regex with a negative lookahead is rarely the right shape for a pin-versus-no-pin decision. The pin marker varies per package manager. A Python function per pattern is the correct shape.

I would skip directly to the two-step pattern in a fork.

The Phase 3 verification commands need negative-test discipline.

Every hook should have at least one test case that exercises the case the hook is supposed to handle correctly (where the hook should pass) and at least one test case that exercises the case the hook is supposed to reject (where the hook should deny or ask).

The Phase 3 test cases mostly covered both. The supply-chain hook's positive test cases (pinned forms) were not exercised against the regex implementation. They were assumed. The Phase 5 audit caught the assumption.

The cached-prefix hook's narrow scope (gating cached-prefix files but not the harness's own deterministic-layer files) is the residual risk I am most likely to revisit.

F10's "accept" disposition is correct for the current threat surface. If a specific failure mode against Asset #5 surfaces, the gate extension is the natural remediation.

---

## §6 Phase 4: extension layer

### §6.1 Context

Phase 4 wrote the extension layer. Skills, agents, MCP servers. The seeds that survived Phase 3 pre-filter and the new ones evaluated for extension-layer work.

The phase output `PHASE-4-NOTES.md` records the per-skill, per-agent, per-plugin rationale.

### §6.2 Narrative

Two skills landed.

`mcp-server-pre-trust-audit` for the six-check audit before any MCP server registration (license, source review, network egress, version pin, secret handling, tool subset).

`seed-evaluation` for the foundation/03 two-stage methodology (pre-filter then deep-eval).

Both close gaps the harness's CLAUDE.md describes but does not operationalize.

Two skills considered and rejected.

`harness-engineering-workflow` (a skill that codifies the build-on-this-repo discipline) was rejected because the project root CLAUDE.md and `mac/harness/CLAUDE.md` already cover this. A skill would duplicate without adding capability.

`threat-model-update` (a skill that walks updating `foundation/01-threat-model.md` when new threats emerge) was rejected because the workflow is rare, the threat-model file itself documents how to update, and a skill firing on routing would inject context into prompts where it does not apply.

Two agents landed.

`reviewer` for the Phase 5 Writer/Reviewer pattern.

`inventory` codifying the Phase 1 role for future re-runs.

Both same-family Opus 4.7 subagents under the Opus 4.7 main session per QC.4a cache lineage.

The `enabledPlugins` calibrated minimum.

`superpowers@claude-plugins-official` v5.1.0 plus `mempalace@mempalace` v3.3.2. Two plugins. Phase 5 would expand for the daily-driver via Operation 4's rebuild.

The `mcpServers` entry stayed empty in the harness reference.

Two reasons.

First, the mempalace plugin's own `.mcp.json` registers the mempalace MCP server when the plugin is enabled. Direct registration would create a duplicate the runtime would deduplicate.

Second, the context7 plugin's `.mcp.json` invokes `npx -y @upstash/context7-mcp` (unpinned), which trips the supply-chain discipline. The plugin was not enabled in the harness reference pending Phase 5's daily-driver review where I would decide between pinning, globally installing, or skipping.

### §6.3 Surprises

The skill count was smaller than the seed pre-filter implied.

I had drafted with the expectation of 4-6 custom skills. The discipline check ("would removing this cause Claude to make a mistake the deterministic layer cannot catch") cut two of the candidates.

Two skills was the right calibration for the harness's surface area.

Superpowers v5.1.0's actual skill count was 14, not the 17 the Phase 1 INVENTORY had reported (F08).

Direct cache inspection confirmed 14 SKILL.md files. The Phase 1 subagent had double-counted (likely the v5.0.7 cache alongside v5.1.0). Cache footprint estimate revised from ~5k to ~4k tokens.

<!-- ROCK: confirm whether the surprise here is the miscount itself or something deeper about subagent verification discipline. The fix is mechanical (correct the count). The lesson is that subagent reports need spot-checks against the cache, not only synthesis. -->

The 13 currently-enabled-but-not-in-harness-reference plugins (context7, github, security-guidance, playwright, pyright-lsp, feature-dev, code-review, vercel, ralph-loop, goodmem, frontend-design, plus typescript-lsp, sentry, serena disabled) all deferred to Phase 5 daily-driver review.

Each would get one pass through the `mcp-server-pre-trust-audit` skill (for plugins shipping MCP servers) and the `seed-evaluation` skill (for plugins shipping skills, agents, or commands). The 11 enabled-and-deferred plugins would absorb meaningful Phase 5 audit time.

### §6.4 Tradeoffs

**Lean adoption with documented swap-in paths versus broader adoption with more cache-prefix footprint.**

Each enabled plugin loads its skills, hooks, and MCP servers into the harness surface. Each adds context load. The calibrated minimum (two plugins) kept the harness reference's footprint under control while documenting the swap-in paths for the daily-driver expansion.

The harness reference is the "what would I run with maximum discipline" answer. The daily-driver is the "what do I run with practical productivity" answer. Two different answers for two different audiences.

**context7 specifically.**

Three options surfaced in PHASE-4-NOTES. Pin (register in `mcpServers` with a specific version). Globally install with pin (`npm install -g @upstash/context7-mcp@2.1.3`, invoke via absolute path). Skip (do not adopt. WebFetch covers documentation lookup with broader source).

Recommendation for Phase 5 was option 2 because the global install is already on the machine at v2.1.3 per Phase 1 inventory, and it eliminates the per-session npx fetch entirely.

**Adopting plugins wholesale versus selectively.**

`superpowers@claude-plugins-official` got adopted wholesale. 14 skills, 1 SessionStart hook. The deep-eval found the foundation discipline value, MIT license, lastUpdated 2026-05-05, active maintenance, used in every build phase.

The selective alternative (pick 4-5 of the 14 skills) would have required maintaining a fork or a per-skill enablement layer. The wholesale alternative carried the full 14-skill cache footprint (~4k tokens).

The wholesale call won because the marginal cost of the unused skills was small (they only load context when their description matches), and the maintenance overhead of a fork was higher than the cache cost.

### §6.5 Retrospective

The skill count discipline ("would removing this cause Claude to make a mistake the deterministic layer cannot catch") is the right filter.

I would apply it more aggressively in a fork. The two adopted skills both close real gaps. The two rejected skills would have been duplicative.

The 13-plugin daily-driver review queue is large enough that I would split it across multiple operations rather than one.

Operation 4 partially absorbed it (the rebuild kept all 16 enabled plugins per the Stage 4 modification "keep superclaude 100% operational" and "preserve enabledPlugins map"). The per-plugin audit work is still pending. Each plugin's pre-trust audit lands as its own item over time.

The mempalace adoption decision flagged a known content-corruption bug in `add_drawer`. The deep-eval recorded the workaround (refile as new drawer) and adopted anyway. The bug is not a blocker because the workaround is deterministic. A fork that values strict integrity over the cross-session structured memory might choose differently.

---

## §7 Phase 5: wire and document

### §7.1 Context

Phase 5 was the wire-and-document phase.

The Writer/Reviewer subagent pattern. The main session writes. A reviewer subagent audits. The reviewer's findings carry severity, location, evidence, and a concrete recommendation.

The phase output `PHASE-5-AUDIT.md` is the durable record.

### §7.2 Narrative: the deliverables

I produced the Phase 5 deliverables.

The polished `mac/ARCHITECTURE.md`.

The rebuilt `~/.claude/` content (deferred to Operation 4 for the actual destructive operation).

The updated `mac/harness/CLAUDE.md`.

The bulk-acknowledge tool scaffolding.

The pre-commit wire change to gitleaks.

The semgrep clean install.

The widened drift-check (deferred to Operation 1).

### §7.3 Narrative: the audit

I dispatched the reviewer subagent.

179,555 tokens. 58 tool uses. ~6 minutes wall time. Same-family Opus 4.7 cache lineage with the parent.

The reviewer returned 13 findings. 1 blocker. 4 majors. 8 minors.

**F01** was the blocker. The Phase 5 prompt named PHASE-5-AUDIT.md and PHASE-5-CONTEXT.md as deliverables and required `grep -c 'Severity: blocker' phase-outputs/PHASE-5-AUDIT.md` as verification, but neither file existed at audit time.

The audit log itself became the resolution. A circular dependency. The prompt's verification depended on a file the prompt did not yet require be produced.

**F02** was a major. The deny pattern `Bash(:*--dangerously-skip-permissions*)` used unsupported empty-prefix syntax. The v2.1.x parser's behavior on empty-prefix patterns was undocumented and not observed in live patterns. Likely produced no enforcement.

Dropped from the rule and from settings.json. Wrapped invocations now fall to the auto-mode classifier as residual risk.

**F03** was a major. Line-count mismatch. `mac/ARCHITECTURE.md:38` claimed "102 lines after Phase 5 polish". `wc -l` returned 81. Direct measurement is the source of truth. Updated to 81.

**F04** and **F05** were the supply-chain hook regex bugs detailed in §5.4. F04 (major), F05 (minor). Both fixed with the two-step regex+function pattern.

**F06** was a minor. Redundant `rm -rf /Users/:*` pattern overlapping the broader `rm -rf /:*`. Dropped.

**F07** was a minor. `Phase 01` vs `Phase 0` numbering inconsistency. Standardized.

**F08** was a minor. Superpowers v5.1.0 skill count claim of 17 (actual 14) detailed in §6.3. Corrected.

**F09** was a minor accept-residual-risk. SessionStart hook exit-code-2 semantics are version-dependent. The hook's `additionalContext` is the durable defense regardless of how the runtime handles the exit code. Re-verify on Claude Code minor bump per QC.5.

**F10** was a minor accept-residual-risk. The cached-prefix hook does not gate the harness's own deterministic-layer files. Git pre-commit plus branch protection plus PR review covers those at the public-repo level.

**F11** was a minor accept-residual-risk. `filesystem-deny-write-secrets` glob dialect uncertainty. Runtime verification requires triggering an actual Write tool call against a `.env` path in a live v2.1.138 session. Deferred to the post-launch `~/.claude/` rebuild operational step. Fallback path (extend `PreToolUse-external-write-gate` to gate in-cwd secret paths) lands as a post-launch revision if needed.

**F12** was a minor accept. `enabledPlugins` setting key schema source not authoritatively cited. Empirical evidence (live user settings.json with 16 enabledPlugins entries) is sufficient.

**F13** was a minor fix-now. Mac README claim about Jetson and Windows scaffolding without cross-reference. Added the cross-reference to `jetson/README.md` and `windows/README.md`.

Final disposition.

9 fix-now (F01-F08, F13).

3 accept-residual-risk (F09, F10, F11).

1 accept (F12).

The reviewer's final recommendation was "NOT READY (blocker F01)." With F01 resolved by the audit log itself and the major findings fixed in their artifacts, the build was "READY with majors recorded" rather than "READY clean."

### §7.4 Surprises

The blocker (F01) was the kind of finding that should have been impossible.

The Phase 5 prompt named the audit log as a deliverable AND required its content as verification. The circular dependency was a prompt-authoring bug, not an execution bug.

The Reviewer caught it because the verification command was unrunnable (the file did not exist), not because the Reviewer was reading the prompt carefully against its own contract.

The lesson. Verification commands need to be tested against the failure case, not only the happy case. A prompt that requires its own outputs as verification needs the outputs to exist at verification time, which means the prompt needs to require their production explicitly.

F04 and F05 (the supply-chain hook regex bugs) surfaced because the Reviewer constructed test inputs from the rule files' own examples and exercised them.

The Phase 3 verification commands had passed because they did not exercise the same edge cases. The Reviewer's discipline (read the artifact's own examples, run them through the implementation) was the right pattern for catching this kind of bug.

The audit-log-missing-from-Phase-5 (F01) and the regex bugs (F04, F05) had a common shape.

Documentation describes intended behavior. Implementation does not match. Verification does not catch the gap.

The Phase 5 audit was the first place the gap surfaced because it was the first place anything ran the documented examples through the actual implementation.

F08's miscount surprised me less than the Phase 1 subagent's confidence in the wrong number.

The subagent had reported 17/4/1 for skills/hooks/agents in superpowers v5.1.0. Direct cache inspection returned 14/1/0. The subagent had likely double-counted across two cached versions.

The lesson for subagent reports. Spot-check the headline numbers against direct observation, especially when the numbers feed into downstream sizing decisions (the cache footprint estimate flowed from the skill count).

The three accept-residual-risk findings (F09, F10, F11) were all genuinely residual rather than blockers.

F09's SessionStart exit-code-2 semantics are documentation-incomplete in Liu et al. §6.1. The hook's additionalContext path is the durable defense.

F10's gate scope is consciously narrow. Git workflow covers the gap.

F11's glob dialect uncertainty is verification-deferred. The rebuild operational step is the natural test.

### §7.5 Tradeoffs

**Writer/Reviewer pattern versus inline self-audit.**

The Writer/Reviewer split costs one round-trip with a subagent. The benefit is independent reading: the Reviewer reads the artifacts without the parent's framing of what success looks like.

A self-audit by the Writer would catch fewer findings because the Writer carries the assumptions that produced the artifacts.

The Phase 5 audit's 13 findings (some of which I would have missed in self-audit) justify the round-trip cost.

**"READY with majors recorded" versus "READY clean."** A clean READY would have required additional iteration cycles. Fix the majors. Re-audit. Confirm no new findings.

The "majors recorded" framing accepts that the build ships with documented residual issues. The three accept-residual-risk findings are documented. The post-launch revision triggers are named. Fork readers see the residuals explicitly rather than discovering them later.

**Reviewer subagent permission scope.**

The reviewer is read-only by design (no editing). The cost is that the Writer (the main session) does the fix-now work after the Reviewer reports. The benefit is that the Reviewer cannot accidentally edit something it should have flagged.

Read-only-by-construction is the right posture for an audit role.

### §7.6 Retrospective

The blocker F01 (Phase 5 prompt's circular verification dependency) is the single clearest "I would do this differently" item from the build.

The prompt should have said "produce PHASE-5-AUDIT.md as a deliverable AND verify against it" with the production explicit. A future prompt-authoring revision would catch this kind of dependency before publishing.

The Reviewer's "audit-the-rule-files'-own-examples" discipline is the right pattern.

I would document it as a Reviewer agent definition addendum. "When auditing a hook, construct test inputs from the rule file's positive and negative examples. Run them through the implementation. Report any discrepancy as a finding."

The Phase 5 audit caught F04 and F05 through this discipline. Encoding it explicitly would make it more reliable.

The three accept-residual-risk findings carry post-launch reconsideration triggers in PHASE-5-AUDIT.md.

F09 re-verifies on Claude Code minor bump.

F10 extends the cached-prefix gate if a specific failure mode surfaces.

F11 verifies the glob dialect during the `~/.claude/` rebuild.

The discipline of naming the trigger at the time of acceptance is what makes residual-risk acceptance honest rather than abdicated.

I would also add a "drift-between-Phase-2-answers-and-landed-artifacts" cross-check to the Reviewer's discipline.

Post-Mac 1 surfaced that the Phase 5 audit had missed the Q10 drift-check widening commitment. The answer said widen. No phase prompt named the work. The Reviewer did not flag the gap.

A discipline of "read every Phase 2 ANSWER's Implications line against landed artifacts" would have caught this. Recorded in Post-Mac 1's carry-forward items.

---

## §8 Operations: post-execution work

### §8.1 Context

Operations are the post-Phase-5 work that turned the validated build into the operational environment and propagated learnings.

The Mac build's seven-phase sequence (pre-flight, Phase 0, Phases 1-5) settled the structural artifacts. Operations land what those artifacts produced into the operational environment, propagate cross-pollination across platforms, and produce the public-facing documentation set.

The original phase plan did not include operations as a discrete bucket.

The need surfaced post-Phase-5. The Phase 5 audit had identified the drift-check widening gap (Operation 1). The cross-pollination work was not phase-prompted (Operation 3). The `~/.claude/` rebuild was a Stage-4-Q3 commitment without a phase home (Operation 4). The documentation closeout sequence (Operations 06-10) became the way to land USER_GUIDE, HARNESS_GUIDE, JOURNEY into the public-facing set.

### §8.2 Operation 1: drift-check widening

Phase 2 Q10's "Widen" election did not land in any phase prompt.

The Phase 5 audit Reviewer subagent caught major findings in artifacts but did not cross-reference Phase 2 ANSWERS against landed artifacts to catch the gap.

POST-MAC-1-NOTES.md records the discovery and the resolution.

The pre-edit `scripts/drift-check.sh` measured only the project hierarchy (root + platform CLAUDE.md + harness CLAUDE.md). The 973-line user-level chain (legacy SuperClaude framework loaded via `@import`) was invisible to the check.

The widening added a `walk_imports()` function that recursively follows `@<path>` directives from `~/.claude/CLAUDE.md`, accumulating into a `USER_LEVEL_TOTAL` and `USER_LEVEL_CHAIN`.

Cycle detection via linear-search VISITED array (bash 3.2 compatible).

Missing files contribute zero so CI runners without `~/.claude/CLAUDE.md` stay green.

Post-edit drift-check FAILed at 1161 lines worst-case session (the 973-line user-level chain dominated).

This was the right behavior. The drift check was doing exactly what Q10 said it should. Making the user-level cached-prefix bloat visible and deterministic instead of letting it sit invisibly.

The FAIL would resolve when Operation 4's `~/.claude/` rebuild trimmed the user-level chain. Or, as it turned out, the FAIL would persist as the documented Stage 4 tradeoff (SuperClaude operational continuity worth the QC.4b violation).

### §8.3 Operation 3: cross-pollination

Cross-pollination took Mac-validated findings and propagated them into the Jetson and Windows scaffolds.

POST-MAC-3-NOTES.md records the classification framework and per-class rationale.

86 in-scope `<NEEDS-PORT-VALIDATION>` markers across the two platform sections (43 per platform).

The classification framework had three buckets.

**Bucket A** (platform-agnostic). Replace marker with Mac-validated fact + "verify behaviorally on this platform."

**Bucket B** (platform-informed-but-specific). Tighten the marker to name the Mac observation + the target's equivalent question.

**Bucket C** (Mac-only). Leave marker unchanged.

62 of 86 markers resolved (72% reduction).

The 24 remaining were all meta-references inside scope/stage/verification language describing the marker convention itself, not bare assertions awaiting validation. None were defects.

The propagation explicitly did NOT lift Mac's Phase 2 answers onto Jetson or Windows.

Q1 (auto-mode), Q6 (30-cap), Q11 (90-day retention) are per-platform interview decisions. The propagation cited them as Mac evidence informing the question, not as the target answer.

The discipline matters. Cross-pollination informs the question. The per-platform interview answers it.

### §8.4 Operation 4: the destructive rebuild of `~/.claude/`

The biggest single act of the build.

POST-MAC-4-PLAN.md is the contract. POST-MAC-4-VERIFICATION.md is the result.

The rebuild posture was default-keep for personal configuration.

Only four classes of items got touched without explicit per-item confirmation. Plaintext secrets (env-var indirection). `skipDangerousModePermissionPrompt: true` (Q9 removal). The 55 dangling symlinks under `commands/zerg/`. Session logs older than 90 days (zero matched currently).

Plus one `§Files to classify` entry I confirmed at the Stage 4 gate.

**The Stage 4 modification.** I said "We need to keep superclaude 100% operational."

The classification entry (the 14 SuperClaude framework files) changed from RETIRE to KEEP.

The new `~/.claude/CLAUDE.md` became a MERGE. Harness content + SuperClaude `@import` chain + four custom sections preserved verbatim.

The QC.4b drift-check FAIL at ~1242 lines worst-case session became a deliberately-accepted tradeoff. SuperClaude operational continuity worth the QC.4b violation. POST-MAC-4-VERIFICATION.md documents the FAIL as expected, not as a regression.

**The `§Files to write new` set landed.**

13 files into `~/.claude/hooks/`, `~/.claude/skills/`, `~/.claude/agents/`. Six hook scripts with executable bit preserved. Two skill SKILL.md files. Two agent definitions. Plus README.md per directory.

**The `§Files to modify` set landed.**

Three files.

`~/.claude/CLAUDE.md` (the MERGE described above).

`~/.claude/settings.json` (merged write. Harness deny patterns added. Hook registrations added. Model and sandbox blocks added. Rock's narrow Bash allows preserved. The 16-plugin enabledPlugins preserved. Q9 key removed).

`~/.claude/mcp.json` (env-var indirection on HCLOUD_TOKEN).

**The `§Files to delete` set.**

55 dangling symlinks under `commands/zerg/`. Zero session logs (none matched the >90-day cutoff at rebuild time).

**The `§Files to preserve` set.**

7000+ files across 31 top-level files and 22 subdirectories. Byte-identical. No reorganization.

**Backup at `~/.claude.backup-20260511-134652/`.**

`cp -a` for byte-identical copy. 609 MB. 7140 files. 59 symlinks.

Verification. File count matched. Size within 1%. Five-file checksum spot-check passed.

**Post-rebuild git init at `~/.claude/`.**

Initial commit `b7b83c3` "Initial rebuild from harness-engineering Mac Phase 5". Tracked tree under 5 MB after the .gitignore exclusions (projects/, cache/, plugins/cache/, history.jsonl, etc.).

The rebuild was the largest single act of the build because it touched the most state and was the least reversible. The backup discipline (full `cp -a` before any destructive operation) was the safety net.

<!-- ROCK: confirm the backup discipline language matches your felt experience. The plan says "the backup is the recovery point if something is wrong." The operational reality of doing the rebuild and trusting the backup is your perspective. -->

### §8.5 Operations 06-10: the documentation closeout sequence

Operations 06 through 10 are this closeout sequence.

Operation 06 rewrote README.md as a 180-line front door.

Operation 07 produced USER_GUIDE.md as a 1356-line pragmatic day-to-day reference.

Operation 08 produced HARNESS_GUIDE.md as a 1505-line architectural reference (a restructure of an earlier 1501-line predecessor authored under the old closeout sequence).

Operation 09 (this operation) produces JOURNEY.md as the educational narrative companion.

Operation 10 closes the build.

The shift from the original consolidated-mega-prompt to per-deliverable prompts came from the practical observation that a single closeout prompt would be too large to execute reliably and too coupled to debug. The per-deliverable shape lets each operation focus on one document's spec, verification, and commit.

The late USER_GUIDE addition (Operation 07) closed a real gap.

The original closeout sequence had only HARNESS_GUIDE for the design reference and JOURNEY for the narrative. A reader with the harness loaded had no operational guide. They would have to reverse-engineer the behavior from the hook code or the rule files.

<!-- ROCK: confirm the framing. The conversational record of why USER_GUIDE got added is real but the executing session does not have it. If the trigger was a specific moment ("I opened a session and could not tell what was firing"), substituting your concrete framing here is right. -->

### §8.6 The Q9 narrowing as an operational lesson

The Q9 narrowing happened during Operation 06 Stage 0 verification.

The runtime kept rewriting `skipDangerousModePermissionPrompt: true` to `~/.claude/settings.json` after every removal. Investigation surfaced that the runtime persists the key when the bypass-mode warning dialog is dismissed with the don't-ask-again affordance. My operator-initiated bypass at session start was the trigger.

Q9 was narrowed to apply the deny rule to model-proposed invocations only. Operator-initiated bypass became the documented expected state.

The narrowing landed across CLAUDE.md, mac/harness/CLAUDE.md, mac/ARCHITECTURE.md, the bash-deny rule, foundation/01-threat-model.md, foundation/02-architectural-principles.md, and three references in HARNESS_GUIDE.md plus a `_documentation` block in `~/.claude/settings.json` itself explaining the intentional state.

The generalizable lesson from the Q9 narrowing.

When a configuration setting "keeps coming back" despite repeated fixes, check git diff before checking the runtime.

If the live state differs from committed state, the runtime is writing it.

The next question is whether the runtime's write is wrong or whether the documented expectation is wrong.

In Q9's case, the documentation was wrong. The runtime was working as designed.

This pattern recurs. The supply-chain hook regex bugs (F04, F05) had a similar shape. Documentation describes intended behavior, implementation does not match, the gap surfaces only when something exercises the documented examples through the actual implementation. The discipline is to run the documented examples through the actual artifacts as a routine check, not only when something feels wrong.

---

## §9 Repo state verification

A reader who clones this repo and wants to verify the state can run the commands below.

They are not executable from within this markdown file (the format change from `.ipynb` to `.md` lost the runnable code cells). The verification snapshot preserves the same commands as copy-paste reference.

### Combined CLAUDE.md hierarchy line count

```
bash scripts/drift-check.sh
```

Returns 0 (OK) or 1 (FAIL or WARN). The script walks the project hierarchy plus the user-level `~/.claude/CLAUDE.md` and its `@import` chain transitively, sums lines into a worst-case-per-session calculation, and reports against the QC.4b 400-line cap and 250-line target.

On the validated Mac the script reports `OK (project worst-case 188 lines, full worst-case 1242 lines incl. user-level chain of 15 file(s) / 1054 lines)`.

The user-level chain over the cap is the documented Q3 / Stage 4 exception (SuperClaude operational continuity).

### Foundation document line counts

```
wc -l foundation/*.md
```

Should return five files at modest line counts (75, 56-58, 68-70, 72, 79 on the validated Mac).

Each file's purpose. `00-quality-contract.md` for the six properties that bind every artifact. `01-threat-model.md` for what the harness defends against and what it does not. `02-architectural-principles.md` for the four load-bearing decisions. `03-seed-evaluation-methodology.md` for the discipline that decides which external tools earn integration. `04-research-references.md` for the index of the three source documents the foundation cites.

### Mac build commit sequence

```
git log --oneline -20 -- mac/
```

Returns the recent commits touching the Mac section. Reading through the log surfaces the build sequence (Phase 0, Phase 1, Phase 2, Phase 3, Phase 4, Phase 5, Operations 1-3-4, closeout 06-10) and any post-launch revisions.

### Operations directory state

```
ls -la operations/
```

Lists the operations prompts and any archive. The current sequence is 06-readme-rewrite, 07-user-guide, 08-harness-guide, 09-journey-rewrite, 10-build-closeout in the live set, with the prior sequence preserved in `_archive/` for historical reference.

### Hook executable bits

```
ls -l mac/harness/hooks/*.py
```

All six files should be `-rwxr-xr-x` (executable). Hooks that lose their executable bit silently fail. The runtime tries to invoke them and the operating system refuses.

### settings.json validity

```
python3 << 'PYEOF'
import json
json.load(open('mac/harness/settings.json'))
PYEOF
```

Returns silently on success. A non-zero exit means the JSON is malformed. The runtime would refuse to load the file and the harness would not apply.

### Pre-commit pipeline status

```
pre-commit run --all-files
```

Runs gitleaks, semgrep, shellcheck, markdownlint-cli2, and the drift-check across the full tree. Returns 0 on clean.

On a fresh clone the first run installs hook environments before running. Subsequent runs use the cached environments.

### Rebuilt `~/.claude/` git status

```
cd ~/.claude && git log --oneline -5
```

Should show the initial rebuild commit `b7b83c3` plus any subsequent commits from operational maintenance (Q9 narrowing, sync from in-repo source, etc.).

The `~/.claude/` repo is local-only. No remote configured. Backup discipline is the engineer's responsibility.

### Audit-hash registry

```
test -f ~/.claude/audited-hashes.json && jq 'length' ~/.claude/audited-hashes.json
```

Returns the count of audited hashes. Each hash binds a SHA-256 to its audit metadata (path, audit date, auditor, optional note). The SessionStart hook reads this registry on every session start.

---

## §10 What I learned and what's next

### §10.1 What I learned about Claude Code as a build target

Three things worked well as build mechanisms.

**The AskUserQuestion interview format.**

Phase 2's structured choices with documented options, locked context, and steel-manned counter-arguments produced calibrated decisions with the rationale recorded inline. The format forced me to think through the tradeoff before answering, and the documented steel-man kept me from anchoring on the recommended option.

The Q3 reframing (where my answer was a fourth option beyond the planned three) was a feature, not a bug. The interview surfaced the right question even when the planned options were too narrow.

**The Writer/Reviewer subagent pattern.**

Phase 5's audit caught 13 findings the Writer (main session) would have missed in self-audit. Same-family Opus cache lineage made the reviewer's invocation cheap. The "evidence not adjectives" discipline in the agent definition produced findings the Writer could act on.

The pattern is reusable. Any phase that produces artifacts can spawn a Reviewer.

**Explicit cache-lineage discipline.**

The QC.4a same-family pinning (Opus parent, Opus subagent) compounded across the build. Phase 1's 154,700-token inventory subagent ran tractably because of the cache lineage. Phase 5's 179,555-token audit subagent did the same.

A mixed-family build would have cost meaningfully more and run slower.

Three things did not work as well.

**Phase 5 prompt's circular verification dependency.**

F01's blocker (Phase 5 prompt required PHASE-5-AUDIT.md content as verification but did not require the file's production) was a prompt-authoring bug that the Reviewer caught at execution time. A pre-execution prompt audit would have caught it earlier.

**Supply-chain hook regex assumed without testing.**

F04 and F05 both surfaced because the Reviewer ran the rule files' own positive examples through the implementation. The Phase 3 verification commands had not exercised the same edge cases.

The lesson. Every hook should have a positive test that exercises a case the hook is supposed to handle correctly, run through the actual implementation, before the hook ships.

**Phase 5 audit missed the Q10 drift-check widening gap.**

The Reviewer caught major findings in artifacts but did not cross-reference Phase 2 ANSWERS' Implications lines against landed artifacts. POST-MAC-1-NOTES.md captured the gap. An addendum to the Reviewer agent definition would close it for future revisions.

What surprised me about Opus 4.7 as a build executor.

**Literalism on scope.**

Opus 4.7 follows scope blocks to the letter. When a phase prompt says "apply only to artifacts X, Y, Z," Opus 4.7 does not creep into adjacent files. This was a feature.

The cost was that scope inconsistencies in the prompt itself (Phase 0's `<TBD-PHASE-0>` markers in `mac/harness/settings.json.template` outside Phase 0's scope) became visible as deferrals rather than silent expansions.

**Parallel-tool-call efficiency.**

Initial-read parallel-tool-call patterns saved meaningful wall time across phases. Phase 1's 7-minute inventory and Phase 5's 6-minute audit both used parallel reads of the relevant files. Serial reads would have multiplied wall time without changing the cache economy.

**Tendency to over-emphasize when prompts did.**

When the project root CLAUDE.md used CAPS or "CRITICAL: MUST" language, Opus 4.7 followed the emphasis to the letter and over-applied the rule. Stripping CAPS and "CRITICAL: MUST" from the operational CLAUDE.md (per the QC.4b context-discipline guidance) produced cleaner adherence than the emphasized version.

The lesson. Emphasis in instructions is friction, not signal, with this model.

### §10.2 What I learned about harness engineering as a discipline

The Quality Contract held up under real building.

Each of the six properties (QC.1 Security, QC.2 Tight code, QC.3 Comment the why, QC.4a Cache, QC.4b Context, QC.5 Versioning) caught a specific failure mode during the build.

QC.2 caught scope creep at Phase 5 audit.

QC.3 caught under-commented hooks during the same audit.

QC.4b caught the cached-prefix line growth before any commit landed.

QC.5 caught the Claude Code minor-version assumption that anchored Phase 0.

The contract is not aspirational. It is enforceable, and the enforcement happens in artifacts (drift-check, audit, version pin).

The threat model's six threats were the right framing.

T1 (prompt injection) was the right "skip the hook, accept residual risk" call. The hook would have carried unbounded latency on every tool return.

T2 (supply chain) and T5 (cache poisoning) were the right "narrow hook" calls.

T3 (pre-trust init) was the right "broad hook" call. The SessionStart audit covers the whole class.

T4 (subcommand bypass) was the right "deterministic cap" call. The 30-subcommand cap is the floor below the 50-subcommand bypass class.

T6 (hostile MCP) was the right "structural deny + per-server audit" call.

I would not reorganize the threat model in a fork. I would extend it as new threat classes surface.

The drift between expected and validated findings was real.

The Phase 1 INVENTORY's miscount (F08), the Phase 5 audit's missed Q10 widening commitment (POST-MAC-1), the supply-chain hook regex bugs (F04, F05) all illustrate the same pattern. Documented intent diverges from implementation reality, and the divergence surfaces only when something runs the documented examples through the actual implementation.

The Reviewer subagent is the build-time instance of this discipline. The periodic audit is the post-launch instance.

The seed evaluation methodology held up too. The 30-second pre-filter caught the obvious dead ends quickly. The integration-not-scoring deep-eval produced binary decisions with rationale rather than rubric scores that pretended to be rigorous.

The "prefer rejection when the decision is ambiguous" posture mattered. A rejected candidate can come back when the signals change. An adopted candidate that turns out wrong costs revisions to remove.

The phase-output discipline carried weight beyond what I expected.

The phase outputs are not deliverables. They are the durable receipts of how the deliverables got made. When the Phase 5 audit needed evidence, the phase outputs were the evidence. When the Q9 narrowing needed context months later, the phase outputs carried the original framing.

The discipline of writing the rationale at the time of the decision (rather than reconstructing it later from the artifacts) is what makes the phase outputs useful. Reconstruction is always partial. The "Decision: ... Why: ..." block in a commit message is the same discipline at a smaller scale.

The locked-decisions discipline was harder than I expected to maintain.

CHECKPOINT.md records the locked decisions. Personal-specific is the value. Three platforms (Mac, Jetson, Windows). Shared foundation plus platform sections. MIT license. No discrete dogfooding phase.

Every phase had moments where reopening one of those locked decisions would have made the immediate work easier. The discipline of stopping and surfacing the conflict before silently working around it is what kept the build coherent.

The most recurrent friction was Phase 2 Q3 (the `~/.claude/` rebuild). The original three options assumed in-place overlay. My fourth option (rebuild) reframed Phase 5 and the post-launch operations. The locked-decisions discipline did not catch this because Q3 was an interview question, not a CHECKPOINT.md locked decision. The build adapted.

The discipline scales down. The discipline scales up. The discipline does not scale across "I forgot to write it down." Writing it down is the prerequisite.

### §10.3 What comes next

Jetson execution.

The Jetson AGX Orin platform section is scaffolded with cross-pollination from the Mac validation applied. Running Phases 0 through 5 against the actual hardware lands the validated build.

The expected-different items live in `jetson/ARCHITECTURE.md`'s `<NEEDS-JETSON-PORT-VALIDATION>` markers. Sandbox primitive (AppArmor or SELinux instead of macOS sandbox-exec). Package manager (apt instead of Homebrew). Credential store (GNOME keyring or equivalent instead of Keychain). Disk encryption (LUKS instead of FileVault). Network egress monitor (opensnitch instead of Little Snitch).

Windows execution.

Windows 11 on x86_64. Same scaffolded posture. Same Phase 0-5 sequence. Same per-platform interview answers.

The PowerShell-vs-Python question for hook scripts is a meaningful per-platform divergence. The Mac harness's "Python uniformly" choice may not survive Windows.

Continuous-revision operational model.

The repo is born public. Revisions land continuously, each in its own commit with the Context/Decision/Why/Tradeoff template.

Significant revisions land in `REVISIONS.md` when that file exists. Until then, the commit log is the record. The discipline scales down to a one-line revision and up to a multi-commit operational sequence. The format is the same.

Residual-risk findings carrying their reconsideration triggers.

F09, F10, F11 each have a documented condition under which they become actionable.

F09 re-verifies on Claude Code minor bump per QC.5.

F10 extends the cached-prefix gate if a specific failure mode surfaces.

F11 verifies the glob dialect during the `~/.claude/` rebuild and falls back to a hook extension if the glob does not fire.

agentcontrolstandard.ai swap-in candidate.

I am working on something with agentcontrolstandard.ai that is not ready yet. The Phase 3 deterministic-layer integration shape is built so the future swap-in slots into the existing pattern without architectural surgery.

When agentcontrolstandard.ai ships, it gets first-class consideration alongside the existing seeds.

### §10.4 What I learned about writing this kind of document

JOURNEY was the hardest of the four documents to write.

README is signposting (180 lines). USER_GUIDE is reference (1356 lines, mostly tables and concrete commands). HARNESS_GUIDE is structural (1505 lines, mostly anatomy). JOURNEY is narrative, which means I had to make choices about what to include and how to frame each phase.

The ROCK markers are the honest admission that the executing session does not have my voice for the subjective parts. The phase outputs record what happened. They do not record how I felt about it. The markers say "this sentence needs Rock's voice rather than the executing session's approximation."

I would write JOURNEY differently in a fork. Each fork has its own subjective story. The discipline is the same. Capture the friction. Name the surprise. Record the tradeoff. Don't retroactively edit to look smarter than you were.

### §10.5 How to engage

This is a personal reference repo.

Issues and discussion are welcome.

Pull requests that change locked decisions in `CHECKPOINT.md` are not. The locked decisions are settled and the rationale is recorded.

Issues and PRs that surface factual errors, broken links, or genuine vulnerability concerns are welcome and triaged per `SECURITY.md`.

Forks adapting the harness for other threat models are exactly the intended use.

The locked decision in `CHECKPOINT.md` is that personal-specific is the value. Your harness needs to reflect your decisions, your tool inventory, your workflow, your Claude Code version pin.

Reading this repo teaches a discipline. Copying it wholesale does not.

If you build your own harness using this as a reference, the foundation documents are the load-bearing thinking. Read them first.

The platform sections (Mac, Jetson, Windows) are worked examples of the discipline.

The phase outputs preserve the reasoning chain.

The commit messages carry the decision rationale.

---

## §11 Post-launch revisions

Operations 06-10 were the closeout sequence that landed this documentation set. Everything after is post-launch revision.

Each significant revision lands in its own commit with the Context/Decision/Why/Tradeoff template. The full commit log is the source of truth. This section is the curated narrative.

### 2026-05-11: drift-check widening (Operation 1)

Closed Phase 2 Q10's commitment that no phase prompt named.

Widened `scripts/drift-check.sh` to count user-level `~/.claude/CLAUDE.md` plus its `@import` chain transitively.

Post-edit drift-check FAILed at 1161 lines worst-case session because of the legacy SuperClaude framework chain. The FAIL was the right behavior. It surfaced the bloat deterministically.

### 2026-05-11: pre-commit rewire and tooling install (Operation 2 equivalent)

Pre-commit pipeline rewired to use `gitleaks` v8.30.0 (replacing `detect-secrets`).

`semgrep` v1.162.0 (clean install via pipx, replacing the broken Anaconda install).

`shellcheck` v0.11.0 (Homebrew install).

Each tool version-pinned in `.pre-commit-config.yaml`.

### 2026-05-11: cross-pollination into Jetson and Windows (Operation 3)

86 `<NEEDS-PORT-VALIDATION>` markers across two platform sections (43 per platform).

62 of 86 resolved by the propagation. 24 remained as meta-references (not bare assertions awaiting validation).

The Jetson and Windows scaffolds now carry Mac-validated facts plus per-platform verification requirements rather than generic markers.

### 2026-05-11: `~/.claude/` rebuild (Operation 4)

The destructive rebuild.

Backup at `~/.claude.backup-20260511-134652/`.

New `~/.claude/CLAUDE.md` (MERGE: harness + SuperClaude + custom sections).

Updated settings.json with harness deny patterns, hook registrations, and the Q9 key removal.

mcp.json migrated to env-var indirection.

55 dangling symlinks deleted.

Private git repo initialized at `~/.claude/` with initial commit `b7b83c3`.

The drift-check FAIL post-rebuild at 1242 lines worst-case session is the documented Stage 4 tradeoff (SuperClaude operational continuity worth the QC.4b violation).

### 2026-05-11: Phase 2 Q9 narrowing

The runtime kept rewriting `skipDangerousModePermissionPrompt: true` after every removal.

Investigation surfaced that the runtime persists the key when the bypass-mode warning dialog is dismissed with the don't-ask-again affordance.

Q9 narrowed to apply the deny rule to model-proposed invocations only. Operator-initiated bypass at session start became the documented expected state.

Updates landed across CLAUDE.md, mac/harness/CLAUDE.md, mac/ARCHITECTURE.md, the bash-deny rule, foundation/01-threat-model.md, foundation/02-architectural-principles.md, three references in HARNESS_GUIDE.md, plus a `_documentation` block in `~/.claude/settings.json`.

### 2026-05-11: Operation 06: README rewrite

180-line front door under the new closeout sequence.

Signposts to USER_GUIDE, HARNESS_GUIDE, JOURNEY, foundation/, platform READMEs, research/, operations/.

Reflects the narrowed Q9 in the opinions section and Status.

### 2026-05-12: Operation 07: USER_GUIDE.md added

1356-line pragmatic day-to-day reference.

Ten sections covering quick orientation, what fires when (per-component behavior), common scenarios as a reference table, using skills, using subagents, workflows, troubleshooting, customizing friction, prompting patterns, what to do when something feels off.

Four required mermaid diagrams (Bash sequence, SessionStart audit flowchart, supply-chain hook flowchart, external-write gate flowchart).

Four behavior-vs-doc gaps caught during authoring (git push --force-with-lease blocked, pip install -r and -e pass, rm-rf-root uses three patterns not four, Phase 2 Q9 narrowing applied) recorded in POST-MAC-7-NOTES.md.

### 2026-05-12: Operation 08: HARNESS_GUIDE.md restructure

1505-line architectural reference.

Ten sections per the new spec.

Five required mermaid diagrams (five-layer architecture, hook lifecycle sequence, CLAUDE.md hierarchy tree, subagent cache lineage sequence, threat-to-mitigation flowchart).

Restructured from the 1501-line predecessor. Dropped §0 (reading paths), §5 (how to use, now USER_GUIDE's domain), §12 + appendices A/B/C + final note.

Renumbered §6-§11 to §5-§10.

Added new content. §1.6 scope-setting. §2.5 what harness engineering is not. §4.20 what the harness does NOT include. Worked QC.3 and QC.5 violation examples. §7.8 second worked composition example. §8.7 the Q9 narrowing as operational lesson. §9.8 not a defense against Claude Code itself going rogue. §9.9 not a guarantee of forward compatibility.

### 2026-05-12: Operation 09: JOURNEY.md replaces JOURNEY.ipynb

This document.

The 13-cell scaffold notebook retired in favor of a markdown narrative.

Format-consistency decision (Rock surfaced). The .ipynb format split the documentation maintenance story for marginal verification benefit. The .md format unifies the documentation set.

Verification commands preserved as copy-paste references in §9.

### 2026-05-12: force-push deny rule narrowed to hook-mediated ask

The `bash-deny-git-push-force.md` deny rule (Phase 3, 2026-05-11) was converted to a new PreToolUse hook `PreToolUse-git-push-force-ask.py`. The three patterns (`git push --force`, `git push -f`, `git push --force-with-lease`) now ask for confirmation rather than block outright.

Trigger. Operator-question on a workflow gap: the original deny rule blocked all three force-push variants, but the operator's daily-driver workflow includes admin-bypass force-pushes on sole-contributor public repos (where branch protection requires PRs that no reviewer exists for). The deny rule produced friction that did not match the actual security boundary the operator wanted (the boundary is "ask me to confirm each force-push," not "always block").

Decision. Convert deny to hook-mediated ask. The deterministic floor is preserved through hook-mediated ask: every model-proposed force-push invocation fires the hook and gets an interactive prompt. The operator confirms per invocation rather than removing the rule for the session.

Structurally similar to the Q9 narrowing (2026-05-11) on `--dangerously-skip-permissions`. Operator-terminal invocations are out of scope.

Five-file change in the in-repo source of truth: delete `mac/harness/rules/bash-deny-git-push-force.md`, create `mac/harness/hooks/PreToolUse-git-push-force-ask.py`, update `mac/harness/settings.json` (remove three deny patterns, register hook), update `mac/ARCHITECTURE.md` (renumber rules and hooks counts), update HARNESS_GUIDE.md and USER_GUIDE.md to reflect the new mechanism.

User-level sync (~/.claude/) lands as a separate commit in the private repo.

Generalizable lesson. A deny rule that produces friction misaligned with the operator's actual security boundary is a calibration miss. The fix is to narrow the rule's strictness while preserving its determinism. Hook-mediated ask is the discipline-preserving alternative to outright deny when the operator wants to confirm rather than block.

### Future revisions

Land here as they happen.

Each entry. Date. The change. The threat or assumption it addresses.

The full commit log is the source of truth.

---

Footer note. This document is one of four that make up the public-facing documentation set. README.md answers "what is this." USER_GUIDE.md answers "what does it do day to day." HARNESS_GUIDE.md answers "how is it designed and why." This document answers "how did it get here."
