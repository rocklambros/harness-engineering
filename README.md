# harness-engineering

## Read this first: educational, not a turnkey product

**This repo documents how *I* (Rock Lambros) built *my* Claude Code harness on *my* specific machine, against *my* threat model and workflow.** It is educational. It is not a configuration to clone and run.

The Mac side is validated against macOS 26.3 on Apple Silicon, Claude Code v2.1.138, the SuperClaude framework I had pre-loaded, and a specific set of seeds (`superpowers`, `mempalace`) adopted through the seed-evaluation methodology in `foundation/03-seed-evaluation-methodology.md`. Every calibration in this repo reflects a decision I made for my environment.

The Jetson AGX Orin and Windows sections are scaffolded with cross-pollination from the Mac validation applied. Specific tooling, hook implementations, and per-platform calibrations for those platforms are TBD pending per-platform execution. Their `<NEEDS-PORT-VALIDATION>` markers identify exactly which assertions still need confirmation on the hardware.

**Mileage will vary**, sometimes substantially, depending on your environment, threat tolerance, tool inventory, and Claude Code version. The patterns and reasoning here are reusable. The configuration is not.

Read this repo as a worked example of one builder's reasoning. Adapt the patterns. Don't copy the configuration wholesale.

## What this repo is

A public reference for how I built my Claude Code harness from first principles across three machines. The repo carries the prompts, configuration, threat model, and reasoning that produced a working hardened harness on Mac, with the Jetson AGX Orin and Windows platforms scaffolded against the validated Mac pattern. Harness engineering treats the configuration around a code-generation model as load-bearing software in its own right, with its own threat model, version pins, and quality contract.

The Mac harness is validated and operating. The Jetson and Windows sections are scaffolded with cross-pollination from the Mac validation applied. Both platform sections carry `<NEEDS-PORT-VALIDATION>` markers identifying assertions that need confirmation on the hardware.

## Why this exists rather than another adopted harness

There are several well-maintained Claude Code configuration projects worth reading: Affaan Mustafa's `everything-claude-code`, Jesse Vincent's `superpowers`, the official Anthropic skills and plugins, Disler's `claude-code-hooks-mastery`, the `awesome-harness-engineering` compilation. Each one is a real piece of work that encodes a particular set of opinions about how the agent loop should be shaped. Those opinions are the point. A harness without opinions is a config file with extra steps.

My opinions did not line up with any of theirs cleanly. The pieces I cared most about (a strict deterministic enforcement layer, identical capabilities across Mac, Jetson, and Windows, an explicit threat model for the harness itself, a seed evaluation methodology that rejects evaluation theater, and rationale preserved as a first-class artifact) were scattered across multiple repos in incompatible shapes. Splicing them together cost more than building the substrate myself and pulling in components as seeds. This repo is the substrate I built and the reasoning that produced it.

## Repo layout at a glance

```
harness-engineering/
├── README.md            (you are here)
├── USER_GUIDE.md        (day-to-day operational behavior, what fires when)
├── HARNESS_GUIDE.md     (architectural reference, how it is designed and why)
├── JOURNEY.md           (chronological build narrative)
├── CHECKPOINT.md        (locked decisions, not relitigated)
├── foundation/          (Quality Contract, threat model, principles, seed evaluation)
├── mac/                 (validated build: ARCHITECTURE.md, 7 phase prompts, harness/, evaluations/)
├── jetson/              (scaffolded: same layout as mac/, awaiting hardware validation)
├── windows/             (scaffolded: same layout as mac/, awaiting hardware validation)
├── research/            (the three source documents the foundation cites)
├── operations/          (post-Phase-5 operational prompts and notes)
├── scripts/             (drift-check.sh and other repo-quality enforcement)
└── phase-outputs/       (build internals: inventory, answers, decisions, gitignored)
```

The structure mirrors the locked decision in `CHECKPOINT.md`: a shared `foundation/` of platform-agnostic thinking plus three platform sections that share an internal layout. Foundation is read once. Platform sections are read by whoever runs the harness on that platform.

## Who this is for

**People building their own Claude Code harness who want a worked reference.** Every phase prompt, every hook script, every deny rule has a rationale attached. The repo answers specific questions: which permission mode to default to, which hook events deserve scripts, what a hook script that survives review looks like, how to decide which MCP servers to enable, how to keep the CLAUDE.md hierarchy short enough to stay in cache. Reading `HARNESS_GUIDE.md` and the Mac section together is a complete walkthrough of one person's harness from goals to runtime artifacts.

**People evaluating Claude Code's security model and want to see what hardening looks like in practice.** The threat model in `foundation/01-threat-model.md` names specific CVE classes (CVE-2025-59536 pre-trust initialization, the 50-subcommand bypass class documented by Adversa.ai 2026, cache poisoning of the prefix). The deterministic layer in `mac/harness/hooks/` and `mac/harness/rules/` is the concrete defense calibrated against a specific threat tolerance and pinned to a specific Claude Code minor version.

**People interested in the harness-engineering discipline as a software-engineering practice.** The repo is opinionated about evaluation rigor (no rubric scoring of seeds), about scope discipline (no speculative abstractions), and about reasoning preservation. The seed evaluation methodology in `foundation/03-seed-evaluation-methodology.md` rejects evaluation theater and replaces it with a 30-second pre-filter plus integration-test deep-evaluation. Reading the foundation documents and the operations log together teaches a posture, not a configuration.

This is not a turnkey product. The locked decision is that personal-specific is the value. Reading the repo teaches a discipline. Copying the configuration wholesale does not.

**Who this is not for.** People looking for a one-command install or a polished marketplace product. People who want to run an LLM-based coding assistant without thinking about its threat surface. People who treat the harness as plumbing rather than as load-bearing software. The repo will frustrate readers in those groups. The documentation is honest about why so the deselection is fast.

## What the harness is opinionated about

Five load-bearing opinions, named here so readers can decide if their thinking lines up.

**Hooks enforce. CLAUDE.md advises.** Claude Code's hook events are deterministic. The model's compliance with CLAUDE.md is probabilistic. Any rule that must hold every time goes in a hook. Anything else goes in CLAUDE.md. The cost of getting this wrong compounds silently.

**Least privilege by default, expand by approving.** Every component starts with the minimum permission set that lets it do its declared job. Auto mode plus an explicit deny list beats `--dangerously-skip-permissions` for model-proposed actions. The 0.4% false-positive rate of the auto-mode classifier (Hughes 2026) costs less than the threat coverage that model-proposed bypass would give up. Operator-initiated bypass at session start is the operator's deliberate choice and is permitted, with the residual risk recorded in the threat model.

**Reversibility weights friction.** Reading is auto-approved. Writing inside the working directory is reversible from version control. Writing outside the working directory triggers a hook. Force-push is denied at the rule layer. The friction matches the consequence.

**Reasoning is the deliverable.** Commit messages name the tradeoff. Phase outputs preserve the reasoning chain. ARCHITECTURE files record the version pins and the next re-evaluation triggers. The harness as a set of config files is the cheap part. The harness as a record of why each line is the way it is, is the value.

**Stress every component against the current model.** Every harness component encodes an assumption about model behavior. A skill description encodes an assumption about how the model will route. A hook denial reason encodes an assumption about how the model will recover. Assumptions go stale across model generations. The discipline is that any component added in Phase 3 or Phase 4 gets exercised against the current model in the same phase, and any minor-version Claude Code bump triggers re-validation against QC.5.

The four opinions land throughout the foundation documents and in `mac/ARCHITECTURE.md`. Reading them together is the load-bearing thinking the rest of the repo rests on.

## The Quality Contract in two sentences

Every artifact in this repo is bound by six properties: QC.1 NIST SP 800-218 alignment (pinned dependencies, secret scanning via gitleaks, SAST gate via semgrep, vulnerability disclosure policy), QC.2 tight code (no speculative scope expansion, no abstractions added without an explicit decision), QC.3 comment the why not the what, QC.4a cache discipline on direct API and SDK use (explicit `"ttl": "1h"` against the March 2026 default revert and the 1024-token minimum), QC.4b context-window discipline on Claude Code sessions (CLAUDE.md hierarchy under 400 lines, no timestamps in cached prefix), and QC.5 versioning (pin to a Claude Code minor-version range and re-evaluate on bump). The detail and the enforcement mechanisms live in `foundation/00-quality-contract.md`, and commit messages cite the QC ID when a decision turns on one of these properties.

Each property names a recurring failure mode in Claude Code harness work and the discipline that prevents it. QC.1 prevents the harness from quietly drifting away from documented secure-development practice. QC.2 prevents speculative scope expansion from accumulating as silent technical debt. QC.3 preserves the reasoning that the code itself does not carry. QC.4a prevents the silent-failure cache traps from inflating costs. QC.4b prevents the long-CLAUDE.md instruction-following degradation that HumanLayer documented. QC.5 prevents the permission and cache schema drift that breaks a working harness across Claude Code minor versions.

## The documentation set

Four documents carry most of the substance. Each one answers a different reader question. Pick by the question you have.

| If you want to know... | Read |
|---|---|
| What this repo is and who it's for | `README.md` (you are here) |
| How do I use this harness day-to-day, what fires when and what to do about it | `USER_GUIDE.md` |
| How is this harness designed and why | `HARNESS_GUIDE.md` |
| How was it built and what would be different next time | `JOURNEY.md` |

Beyond the four main documents, four reference areas hold the supporting material.

| Reference area | Contents |
|---|---|
| `foundation/` | Quality Contract, threat model, architectural principles, seed evaluation methodology, research index. Platform-agnostic. |
| `mac/`, `jetson/`, `windows/` | Per-platform implementation: `ARCHITECTURE.md`, the seven phase prompts, runtime artifacts, evaluation worksheets. Mac validated. Jetson and Windows scaffolded with cross-pollination. |
| `research/` | The three source documents the foundation cites: Liu et al. on Claude Code internals, the SAGE harness-engineering analysis, NIST SP 800-218 SSDF v1.1. |
| `operations/` | Post-Phase-5 operational prompts and notes: drift-check widening, the `~/.claude/` rebuild, the documentation closeout sequence that produced the four main documents. |

The `foundation/` directory itself has five files. Read them in order: `00-quality-contract.md` for the six properties that bind every artifact, `01-threat-model.md` for what the harness defends against and what it does not, `02-architectural-principles.md` for the four load-bearing decisions, `03-seed-evaluation-methodology.md` for the discipline that decides which external tools earn integration, and `04-research-references.md` for the index of the three source documents the foundation cites.

Two short paths through the repo work for most readers. The principle-first path runs `foundation/` then `HARNESS_GUIDE.md` then the relevant platform `ARCHITECTURE.md` then the Mac phase prompts in `mac/prompts/`. This gives you the load-bearing thinking before the platform-specific implementation. The path takes about an hour for an attentive reader.

The narrative-first path runs `JOURNEY.md` then `HARNESS_GUIDE.md` then the foundation documents. This gives you the chronological story before the structural one. The path takes about the same hour but lands the reader in a different mental model.

Either path teaches the discipline. Pick by preference.

## What the validated Mac build contains

Concrete numbers, recorded against the Mac section's first build completion on 2026-05-11.

- 7 phase prompts in `mac/prompts/` (pre-flight, Phase 0, Phases 1 through 5), each with a standard header and explicit verification criteria.
- 5 permission deny rules in `mac/harness/rules/` covering model-proposed bypass mode, sudo, `rm -rf` against root paths, secret-file writes, and the MCP server-prefix default.
- 7 Python hook scripts in `mac/harness/hooks/` covering subcommand-cap, external-write gating, supply-chain checks on unpinned installs, cached-prefix write gating, force-push ask, in-repo `.claude/`-config audit at session start, and session-log pruning at 90 days.
- 2 harness skills in `mac/harness/skills/` (`mcp-server-pre-trust-audit`, `seed-evaluation`) that close foundation gaps the CLAUDE.md describes but does not operationalize.
- 2 subagent definitions in `mac/harness/agents/` (`reviewer`, `inventory`), both pinned to same-family Opus 4.7 for cache lineage per QC.4a.
- 2 enabled plugins (`superpowers@claude-plugins-official` v5.1.0 with 14 skills, `mempalace@mempalace` v3.3.2 with 1 skill and 39 deferred-load tools).
- Pre-commit pipeline wired with `gitleaks` v8.30.0 (secret scanning), `semgrep` v1.162.0 (SAST), and `shellcheck` v0.11.0.

The Quality Contract holds across all of it. The drift-check script in `scripts/drift-check.sh` enforces the cached-prefix discipline as deterministic code rather than as advisory text in CLAUDE.md.

## Tools and seeds I use

The Mac harness depends on a specific external surface. The list below names what I run on this machine with repo links so readers can evaluate each on its own terms. Version pins are recorded in `mac/ARCHITECTURE.md` §Version pins. Per-seed adoption rationale lives in `mac/evaluations/deep-eval.md` and `phase-outputs/PHASE-4-NOTES.md`.

**The runtime.**

- [Claude Code](https://docs.claude.com/en/docs/claude-code) by Anthropic. Pinned to v2.1.* (currently 2.1.138).

**Adopted seeds (plugins and skill collections).**

- [`obra/superpowers`](https://github.com/obra/superpowers) by Jesse Vincent. MIT license. Adopted wholesale at v5.1.0 (14 skills + 1 SessionStart hook). The plugin's `using-superpowers` skill drives a lot of my routine workflow.
- [`MemPalace/mempalace`](https://github.com/MemPalace/mempalace). MIT license. Adopted at v3.3.2. Provides cross-session structured memory (drawers, AAAK diaries, knowledge-graph triples) alongside Claude Code's native auto-memory.

**Security tools wired into the pre-commit pipeline.**

- [`gitleaks/gitleaks`](https://github.com/gitleaks/gitleaks) v8.30.0 for secret scanning.
- [`semgrep/semgrep`](https://github.com/semgrep/semgrep) v1.162.0 for SAST against Python files (installed via pipx in a separate venv because the Anaconda install was broken).
- [`koalaman/shellcheck`](https://github.com/koalaman/shellcheck) v0.11.0 for shell linting.
- [`DavidAnson/markdownlint-cli2`](https://github.com/DavidAnson/markdownlint-cli2) for markdown linting.
- [`pre-commit/pre-commit`](https://github.com/pre-commit/pre-commit) framework wiring.

**Tools I evaluated but did not adopt at this build.**

- [`anthropics/claude-code`](https://github.com/anthropics/claude-code) marketplace plugins beyond the calibrated minimum (context7, github, security-guidance, playwright, etc.). Each gets reviewed under the `mcp-server-pre-trust-audit` and `seed-evaluation` skills before landing in the daily-driver `~/.claude/`.
- [`oraios/serena`](https://github.com/oraios/serena). Installed but disabled in my user settings. The user-disabled signal is the reason for deferral, not a quality assessment of the tool.
- [`cosai-oasis/project-codeguard`](https://github.com/cosai-oasis/project-codeguard). Pre-1.0. Deferred per `foundation/03-seed-evaluation-methodology.md`'s pre-filter (revisit on 1.0 release).
- [`affaan-m/everything-claude-code`](https://github.com/affaan-m/everything-claude-code) and [`disler/claude-code-hooks-mastery`](https://github.com/disler/claude-code-hooks-mastery). Read as references. Not integrated because my opinions did not line up cleanly with their patterns.

**Cited research.**

- Liu et al., reverse-engineering analysis of Claude Code v2.1.88. The `research/Claude_Architecture.md` document.
- The SAGE document on harness engineering as a discipline. The `research/Harness_Engineering_for_Claude_Code_A_Systems_Architecture_Analysis.md` document.
- NIST SP 800-218 v1.1, Secure Software Development Framework. The `research/NIST_SP_800-218-Secure-Software-Development-Framework.md` document.

**Jetson AGX Orin tools: TBD.** Specific tooling decisions for the Jetson platform (sandbox primitive choice between AppArmor and SELinux, package manager strategy, credential store, network egress monitor) are deferred to per-platform Phase 0 execution. The Mac-validated patterns inform the questions. The per-platform answers land when the build runs against the actual hardware.

**Windows tools: TBD.** Same shape as Jetson. The PowerShell-vs-Python question for hook scripts, the WSL2 posture decision, the credential store (Windows Credential Manager), and the network egress monitor (GlassWire / simplewall) all wait on per-platform Phase 0 execution.

This list is not a recommendation that you adopt the same tools. It is documentation of what I chose for my environment. Your fork should run the same seed-evaluation discipline against your own threat model and tool inventory. You may end up with a different set.

## How the build was sequenced

The harness was built in seven phases per platform, each phase carrying its own prompt and its own verification criteria.

- **Pre-flight** moves the research documents into place and verifies the working directory baseline.
- **Phase 0** sets goals and writes `ARCHITECTURE.md` for the platform: what capabilities the harness must have, what success looks like, what threats it does not defend against.
- **Phase 1** runs in plan mode and discovers what is on the machine. A subagent handles the inventory scan because it touches more than 20 files. Synthesis happens in the main session.
- **Phase 2** is the architecture interview. The `AskUserQuestion` tool drives a focused conversation about which threats live in hooks, which seeds get pre-filtered, and what the platform-specific divergences look like.
- **Phase 3** writes the deterministic layer: hook scripts, deny rules, sandbox configuration, the permission posture. Anything that has to hold every time lands here.
- **Phase 4** writes the extension layer: skills, agents, MCP servers, the seeds that survived pre-filter. Each gets stress-tested in a sandboxed integration during the same session.
- **Phase 5** wires everything and produces the documentation. A Reviewer subagent audits every change against the Quality Contract, the threat model, and the architectural principles.

Each phase prompt uses the same standard header (effort, mode, thinking, context budget, parallel tool calls, scope). Each prompt records its context-budget delta. Each prompt commits its output with a rationale block in the commit message. The discipline of the build sequence is the same discipline the harness imposes on day-to-day work.

## Three platforms, one harness

The locked decision in `CHECKPOINT.md` is that capabilities are identical across Mac, Jetson AGX Orin, and Windows. One tool when one tool covers all three. An equivalent tool per platform when one tool does not. The cross-platform parity rule is what makes the harness portable and what keeps a future me from drifting into Mac-only habits. Mac is validated and operating against macOS on Apple Silicon. Jetson is scaffolded against JetPack-based Ubuntu on ARM64. Windows is scaffolded against Windows 11 on x86_64. The platform-specific divergences (sandbox primitives, package managers, credential stores, disk encryption, network egress monitors) are recorded in each platform's `ARCHITECTURE.md`.

## Quick start

If you want to evaluate this harness as a reference for your own work, the path is four steps.

1. Clone the repo. No build step, no install, no entry point.
2. Read this README. Then read `USER_GUIDE.md` for the day-to-day operational behavior. Then read `HARNESS_GUIDE.md` for the design context. Then read the platform README that matches your machine.
3. Read `JOURNEY.md` for the chronological story of how the harness got built and what would be different next time. The narrative carries the context the reference documents leave out.
4. Adapt rather than copy. Run your own Phase 0 against your own environment to record what you have. Run your own Phase 1 to inventory it. Then decide where your harness should diverge.
5. Read the `operations/` directory if you want to see how the harness was operated after Phase 5. The post-launch operational prompts (drift-check widening, the `~/.claude/` rebuild, the documentation closeout sequence) carry the practice of treating revisions as deliberate work rather than as drift.

Do not symlink `mac/harness/` over your `~/.claude/` directory without going through the extension and adaptation guidance in `HARNESS_GUIDE.md`. The prompts in `mac/prompts/` are calibrated to a specific tool inventory, a specific threat tolerance, a specific working directory, and a specific Claude Code version pin. Running them against an arbitrary machine produces output that looks plausible and is wrong.

## What this repo is not

This is not a CLI tool. There is no `npm install`, no entry point, no daemon, no service. The artifact is reasoning preserved alongside configuration. Tools in `scripts/` exist to enforce internal quality properties (drift checks, secret scans) rather than to expose surface for external consumption.

This is not a product. The repo is public because the reasoning is useful to other people building harnesses. The configuration is published because removing it would make the reasoning harder to follow, not because the configuration is meant to be cloned. Personal-specific decisions are the value, not the obstacle.

This is not a project seeking pull requests that change locked decisions. The locked decisions in `CHECKPOINT.md` are settled and the rationale is recorded. Issues and PRs that surface factual errors, broken links, or genuine vulnerability concerns are welcome and triaged per `SECURITY.md`. PRs that propose alternative architectures land in the closed-without-merge bucket with a pointer to the rationale.

This is not a finished document set. Revisions land as the harness evolves. Each revision lands in its own commit with the rationale block in the commit message. There is no discrete dogfooding phase. Dogfooding is continuous, and it is the reason the repo exists.

This is not a substitute for understanding Claude Code itself. The `research/Claude_Architecture.md` document (Liu et al. on the v2.1.88 internals) is the upstream reference for how the runtime works. The harness sits on top of that runtime and depends on its documented behavior. A reader who tries to reason about the harness without the runtime mental model will find the rationale opaque in places.

## Status

Mac validated and operating as of 2026-05-11. The seven phase prompts (pre-flight, Phase 0, Phases 1 through 5) ran end-to-end against macOS on Apple Silicon (Darwin 25.3.0, Claude Code v2.1.138). The validation criteria are recorded against each phase's verification block, and the Reviewer subagent in Phase 5 audited every artifact against the Quality Contract, the threat model, and the architectural principles before commit.

Post-Phase-5 operational steps landed in their own commits with rationale: the drift-check widening per Phase 2 Q10, the pre-commit rewire from `detect-secrets` to `gitleaks` plus `semgrep` and `shellcheck` install, the `~/.claude/` rebuild from the in-repo source of truth, and the Phase 2 Q9 narrowing to model-proposed-only. Operator-initiated bypass at session start is permitted under the narrowed Q9. Model-proposed bypass invocations remain denied at the Bash rule layer. The documentation closeout sequence that produced this README, `USER_GUIDE.md`, `HARNESS_GUIDE.md`, and `JOURNEY.md` ran across Operations 06 through 10.

Jetson and Windows sections are scaffolded with cross-pollination from the Mac validation applied. The next build sequences run Phases 0 through 5 against actual Jetson AGX Orin and Windows 11 machines. Until those builds run, treat the `<NEEDS-PORT-VALIDATION>` markers in those sections as live questions rather than finished documentation.

Persistence posture: Claude Code's native auto-memory carries free-form per-project memories. MemPalace (plugin v3.3.2) lives alongside auto-memory for structured workflows (drawers, AAAK diaries, knowledge-graph triples) where the free-form `.md` format does not fit. The two systems are complementary, not redundant. Auto-memory carries the lightweight defaults. MemPalace carries the structured cross-session work. The seed evaluation methodology in `foundation/03-seed-evaluation-methodology.md` recorded the decision that landed both rather than choosing between them.

Continuous post-launch revisions land in their own commits per the project commit template. Significant changes get summarized in `REVISIONS.md` when that file exists. Until then, the commit log is the record. The repo is alive. If you find a factual error, a broken link, or a real vulnerability concern, file an issue or email per `SECURITY.md`. If you want to propose a different architecture, the closed-without-merge response is not personal. The locked decisions are load-bearing.

## License, security, contact

**License.** MIT. See `LICENSE`. The license covers the code, configuration, and documentation in this repo. The three documents under `research/` carry their own licenses and are included for reference.

**Security.** Vulnerability disclosure policy in `SECURITY.md`. The harness's threat model lives in `foundation/01-threat-model.md`. Reports go to `security@rockcyber.com` with a triage target of five business days. Out-of-scope items (Claude Code itself, third-party seeds referenced by the seed evaluation documents) get redirected upstream.

**Repo.** `github.com/rocklambros/harness-engineering`.

**Citation.** Rock Lambros (RockCyber), *harness-engineering*, `github.com/rocklambros/harness-engineering`, 2026.

## Conventions for reading the repo

Commit messages follow a fixed template: a one-line summary, then a `Context` block (what was happening), a `Decision` block (what was chosen), a `Why` block (the reasoning, anchored to a QC ID or a piece of evidence), and a `Tradeoff` block (what was given up). The template is the same on every commit so the rationale stays close to the change. Reading the commit log is a faster way to follow the build than reading the phase outputs in isolation.

Writing conventions for every artifact: American English, active voice, plain words. No em dashes. No semicolons. No sentences starting with conjunctions. No AI filler. No corporate slop. Paragraphs over bullets. Bullets only for three to seven discrete items where visual separation aids comprehension. The voice is educational and first-person, modeled on `rocklambros/zerg` and `rocklambros/TRACT`.

If you need to find the rationale for a specific decision, three places hold it. The relevant `foundation/` document carries the principle-level reasoning. The platform `ARCHITECTURE.md` carries the platform-specific operationalization. The commit message on the change that introduced the decision carries the immediate context. The three layers correspond to three different reader questions: "why does this kind of decision get made this way," "why does it look this way on this platform," and "why did it land in this commit at this time."
