# harness-engineering

A public reference for how Rock Lambros built his Claude Code harness from first principles across three machines. The repo carries the prompts, configuration, threat model, and reasoning that produced a working hardened harness on Mac, with the Jetson AGX Orin and Windows platforms scaffolded against the validated Mac pattern. Harness engineering treats the configuration around a code-generation model as load-bearing software in its own right, with its own threat model, version pins, and quality contract.

The Mac harness is validated and operating. The Jetson and Windows sections are scaffolded with cross-pollination from the Mac build applied, awaiting validation on their respective hardware.

## Why this exists rather than another adopted harness

There are several well-maintained Claude Code configuration projects worth reading: Affaan Mustafa's `everything-claude-code`, Jesse Vincent's `superpowers`, the official Anthropic skills and plugins, Disler's `claude-code-hooks-mastery`, the `awesome-harness-engineering` compilation. Each one is a real piece of work and each one encodes a particular set of opinions about how the agent loop should be shaped. Those opinions are the point. A harness without opinions is a config file with extra steps.

My opinions did not line up with any of theirs cleanly. The pieces I cared most about (a strict deterministic enforcement layer, identical capabilities across Mac, Jetson, and Windows, an explicit threat model for the harness itself, a seed evaluation methodology that rejects evaluation theater, and rationale preserved as a first-class artifact) were scattered across multiple repos in incompatible shapes. Splicing them together cost more than building the substrate myself and pulling in components as seeds.

This repo is the substrate I built and the reasoning that produced it. Specific seeds get evaluated and adopted where they earn their place. The seed evaluation methodology in `foundation/03-seed-evaluation-methodology.md` records the decisions.

## Repo layout at a glance

```
harness-engineering/
├── README.md            (you are here)
├── HARNESS_GUIDE.md     (what a harness is and how this one works)
├── JOURNEY.ipynb        (chronological build narrative)
├── CHECKPOINT.md        (locked decisions, not relitigated)
├── foundation/          (platform-agnostic thinking: QC, threat model, principles, seed evaluation)
├── mac/                 (validated build: ARCHITECTURE.md, 7 phase prompts, harness/, evaluations/)
├── jetson/              (scaffolded: same layout as mac/, awaiting hardware validation)
├── windows/             (scaffolded: same layout as mac/, awaiting hardware validation)
├── research/            (three source documents the foundation cites)
├── operations/          (post-Phase-5 operational prompts and notes)
├── scripts/             (drift-check.sh and other repo-quality enforcement)
└── phase-outputs/       (build internals: inventory, answers, decisions)
```

The structure mirrors the locked decision in `CHECKPOINT.md`: a shared `foundation/` of platform-agnostic thinking plus three platform sections that share an internal layout. Foundation is read once. Platform sections are read by whoever runs the harness on that platform.

## Who this is for

**People building their own Claude Code harness who want a worked reference.** Every phase prompt, every hook script, every deny rule has a rationale attached. Reading the foundation documents and the Mac section together is a complete walkthrough of one person's harness from goals to runtime artifacts. The reasoning is the point. The configuration is the receipt of decisions made.

If you are at the "I want to harden my Claude Code setup but I do not know which layer to start with" stage, the foundation documents map the territory and the Mac section shows one path through it. Specific questions the repo answers: which permission mode to default to, which hook events deserve scripts, what a hook script that survives review looks like, how to decide which MCP servers to enable, and how to keep the CLAUDE.md hierarchy short enough to stay in cache.

**People evaluating Claude Code's security model and want to see what hardening looks like in practice.** The threat model in `foundation/01-threat-model.md` names specific CVE classes and architectural failure modes (CVE-2025-59536 pre-trust initialization, the 50-subcommand bypass class documented by Adversa.ai 2026, cache poisoning of the prefix). The deterministic layer in `mac/harness/hooks/` and `mac/harness/rules/` is the concrete defense. The architectural principles in `foundation/02-architectural-principles.md` carry the load-bearing rule that hooks enforce and CLAUDE.md advises.

If you are auditing what a hardened personal Claude Code setup looks like, the Mac section is a worked example calibrated against a specific threat tolerance and pinned to a specific Claude Code minor version.

**People interested in the harness-engineering discipline itself as a software-engineering practice.** The repo is opinionated about evaluation rigor (no rubric scoring of seeds), about scope discipline (no speculative abstractions), and about reasoning preservation. Commit messages name tradeoffs. Phase outputs preserve the chain. The seed evaluation methodology in `foundation/03-seed-evaluation-methodology.md` rejects evaluation theater and replaces it with a 30-second pre-filter plus integration-test deep-evaluation. Reading the foundation documents and the operations log together teaches a posture, not a configuration.

This is not a turnkey product. The locked decision is that personal-specific is the value. Reading the repo teaches a discipline. Copying the configuration wholesale does not.

**Who this is not for.** People looking for a one-command install or a polished marketplace product. People who want to run an LLM-based coding assistant without thinking about its threat surface. People who treat the harness as plumbing rather than as load-bearing software. The repo will frustrate readers in those groups. The documentation is honest about why.

## What the harness is opinionated about

Four load-bearing opinions, named here so readers can decide if their thinking lines up.

**Hooks enforce. CLAUDE.md advises.** Claude Code's hook events are deterministic. The model's compliance with CLAUDE.md is probabilistic. Any rule that must hold every time goes in a hook. Anything else goes in CLAUDE.md. The cost of getting this wrong compounds silently.

**Least privilege by default, expand by approving.** Every component starts with the minimum permission set that lets it do its declared job. Auto mode plus an explicit deny list beats `--dangerously-skip-permissions`. The 0.4% false-positive rate of the auto-mode classifier costs less than the threat coverage that bypass mode gives up.

**Reversibility weights friction.** Reading is auto-approved. Writing inside the working directory is reversible from version control. Writing outside the working directory triggers a hook. Force-push is denied at the rule layer. The friction matches the consequence.

**Reasoning is the deliverable.** Commit messages name the tradeoff. Phase outputs preserve the reasoning chain. ARCHITECTURE files record the version pins and the next re-evaluation triggers. The harness as a set of config files is the cheap part. The harness as a record of why each line is the way it is, is the value.

The four opinions land throughout the foundation documents and in `mac/ARCHITECTURE.md`. Reading them together is the load-bearing thinking the rest of the repo rests on.

## The Quality Contract in two sentences

Every artifact in this repo is bound by six properties, each of which names a recurring failure mode in Claude Code harness work and the discipline that prevents it. QC.1 (NIST SP 800-218 alignment) prevents the harness from quietly drifting away from documented secure-development practice. QC.2 (tight code) prevents speculative scope expansion from accumulating as silent technical debt. QC.3 (comment the why, not the what) preserves the reasoning that the code itself does not carry. QC.4a (cache discipline on API and SDK use) prevents the 1024-token-minimum and 5-minute-default-TTL traps from silently inflating costs. QC.4b (Claude Code context discipline, under 400 lines of CLAUDE.md hierarchy) prevents the long-CLAUDE.md instruction-following degradation that HumanLayer documented. QC.5 (version pinning) prevents the permission and cache schema drift that breaks a working harness across Claude Code minor versions.

The detail and the enforcement mechanisms live in `foundation/00-quality-contract.md`. Commit messages cite the QC ID when a decision turns on one of these properties. The contract is short on purpose. A long contract becomes wallpaper. These six carry their weight.

## What the validated Mac build contains

Concrete numbers, recorded against the Mac section's first build completion on 2026-05-11:

- 7 phase prompts in `mac/prompts/` (pre-flight, Phase 0, Phases 1 through 5), each with a standard header and explicit verification criteria.
- 6 permission deny rules in `mac/harness/rules/` covering `git push --force`, bypass mode, sudo, `rm -rf` against root paths, secret-file writes, and the MCP server-prefix default.
- 6 Python hook scripts in `mac/harness/hooks/` covering subcommand-cap (30 max, defense in depth below the Adversa.ai 50 threshold), external-write gating, supply-chain checks on unpinned installs, cached-prefix write gating, in-repo `.claude/`-config audit at session start, and session-log pruning at 90 days.
- 2 harness skills in `mac/harness/skills/` (`mcp-server-pre-trust-audit`, `seed-evaluation`) that close foundation gaps the CLAUDE.md describes but does not operationalize.
- 2 subagent definitions in `mac/harness/agents/` (`reviewer`, `inventory`), both pinned to same-family Opus 4.7 for cache lineage per QC.4a.
- 2 enabled plugins (`superpowers@claude-plugins-official` v5.1.0 with 14 skills, `mempalace@mempalace` v3.3.2 with 1 skill and 39 deferred-load tools).
- Pre-commit pipeline wired with `gitleaks` v8.30.0 (secret scanning), `semgrep` v1.162.0 (SAST), and `shellcheck` v0.11.0.

The Quality Contract holds across all of it. The drift-check script in `scripts/drift-check.sh` enforces the cached-prefix discipline as deterministic code rather than as advisory text in CLAUDE.md.

## How the build was sequenced

The harness was built in seven phases per platform, each phase carrying its own prompt and its own verification criteria.

- **Pre-flight** moves the research documents into place and verifies the working directory baseline.
- **Phase 0** sets goals and writes `ARCHITECTURE.md` for the platform: what capabilities the harness must have, what success looks like, what threats it does not defend against.
- **Phase 1** runs in plan mode and discovers what is on the machine. A subagent handles the inventory scan because it touches more than 20 files. Synthesis happens in the main session.
- **Phase 2** is the architecture interview. The `AskUserQuestion` tool drives a focused conversation about which threats live in hooks, which seeds get pre-filtered, and what the platform-specific divergences look like.
- **Phase 3** writes the deterministic layer: hook scripts, deny rules, sandbox configuration, the permission posture. Anything that has to hold every time lands here.
- **Phase 4** writes the extension layer: skills, agents, MCP servers, the seeds that survived pre-filter. Each gets stress-tested in a sandboxed integration during the same session.
- **Phase 5** wires everything and produces the documentation. A Reviewer subagent audits every change against the Quality Contract, the threat model, and the architectural principles. The phase output is the polished platform section.

Each phase prompt uses the same standard header (effort, mode, thinking, context budget, parallel tool calls, scope). Each prompt records its context-budget delta. Each prompt commits its output with a rationale block in the commit message. The discipline of the build sequence is the same discipline the harness imposes on day-to-day work.

## Three platforms, one harness

The locked decision in `CHECKPOINT.md` is that capabilities are identical across Mac, Jetson AGX Orin, and Windows. One tool when one tool covers all three. An equivalent tool per platform when one tool does not. The cross-platform parity rule is what makes the harness portable and what keeps a future me from drifting into Mac-only habits.

Mac is validated and operating against macOS on Apple Silicon. Jetson is scaffolded against JetPack-based Ubuntu on ARM64, with the platform-specific divergences (AppArmor or SELinux in place of macOS sandbox-exec, apt in place of Homebrew, LUKS in place of FileVault, opensnitch in place of Little Snitch) recorded in `jetson/ARCHITECTURE.md`. Windows is scaffolded against Windows 11 on x86_64, with the platform-specific divergences (PowerShell versions, WSL2 posture, BitLocker, Windows Credential Manager, AppLocker) recorded in `windows/ARCHITECTURE.md`. Both Jetson and Windows section READMEs flag the `<NEEDS-PORT-VALIDATION>` markers as honest signals about which assertions have not yet been confirmed on the platform.

## Where to read next

The repo has seven entry points organized by reader question.

| If you want to know... | Read |
|---|---|
| What a Claude Code harness is and how this one works | `HARNESS_GUIDE.md` |
| Why I built it this way, in chronological order | `JOURNEY.ipynb` |
| What design principles bind every decision | `foundation/` |
| What the Mac-specific harness looks like in detail | `mac/` |
| What the Jetson and Windows scaffolds look like | `jetson/` and `windows/` |
| What underlying research the harness cites | `research/` |
| How the build was sequenced and operated | `operations/` |

The `foundation/` directory itself has five files. Read them in order: `00-quality-contract.md` for the six properties that bind every artifact, `01-threat-model.md` for what the harness defends against and what it does not, `02-architectural-principles.md` for the four load-bearing decisions, `03-seed-evaluation-methodology.md` for the discipline that decides which external tools earn integration, and `04-research-references.md` for the index of the three source documents the foundation cites.

Two short paths through the repo work for most readers.

The principle-first path runs `foundation/` then `mac/ARCHITECTURE.md` then the Mac phase prompts in `mac/prompts/`. This gives you the load-bearing thinking before the platform-specific implementation. The path takes about an hour for an attentive reader.

The narrative-first path runs `JOURNEY.ipynb` then `HARNESS_GUIDE.md` then the foundation documents. This gives you the chronological story before the structural one. The path takes about the same hour but lands the reader in a different mental model.

Either path teaches the discipline. Pick by preference.

## Quick start

If you want to evaluate this harness as a reference for your own work, the path is four steps.

1. Clone the repo. No build step, no install, no entry point.
2. Read `README.md` (you are here), then `HARNESS_GUIDE.md`, then the platform README that matches your machine.
3. Read `JOURNEY.ipynb` for the context behind the decisions. The notebook fills phase by phase as the build progresses. Treat the chronology as the version of the reasoning that survives.
4. Adapt rather than copy. Run your own Phase 0 against your own environment to record what you have. Run your own Phase 1 to inventory it. Then decide where your harness should diverge.

Do not symlink `mac/harness/` over your `~/.claude/` directory without going through the adaptation section in `HARNESS_GUIDE.md`. The prompts in `mac/prompts/` are calibrated to a specific tool inventory, a specific threat tolerance, a specific working directory, and a specific Claude Code version pin. Running them against an arbitrary machine produces output that looks plausible and is wrong.

The seven phase prompts in `mac/prompts/` are the entry point if you want to see how the harness was built step by step. Each prompt carries the standard header (effort, mode, thinking, context budget, parallel tool calls, scope) and explicit verification criteria. The prompts are contracts with the executing Claude Code session, not memos to a future self.

## What this repo is not

This is not a CLI tool. There is no `npm install`, no entry point, no daemon, no service. The artifact is reasoning preserved alongside configuration. Tools in `scripts/` exist to enforce internal quality properties (drift checks, secret scans) rather than to expose surface for external consumption.

This is not a product. The repo is public because the reasoning is useful to other people building harnesses. The configuration is published because removing it would make the reasoning harder to follow, not because the configuration is meant to be cloned. Personal-specific decisions are the value, not the obstacle.

This is not a project seeking pull requests that change locked decisions. The locked decisions in `CHECKPOINT.md` are settled and the rationale is recorded. Issues and PRs that surface factual errors, broken links, or genuine vulnerability concerns are welcome and triaged per `SECURITY.md`. PRs that propose alternative architectures land in the closed-without-merge bucket with a pointer to the rationale.

This is not a finished document. Revisions land as the harness evolves. Each revision lands in its own commit with the rationale block in the commit message. There is no discrete dogfooding phase. Dogfooding is continuous, and it is the reason the repo exists.

## Status and what comes next

Mac validated and operating as of 2026-05-11. The seven phase prompts (pre-flight, Phase 0, Phases 1 through 5) ran end-to-end. The post-Phase-5 operational steps (drift-check widening per Phase 2 Q10, pre-commit rewire from `detect-secrets` to `gitleaks`, `semgrep` and `shellcheck` install, the `~/.claude/` rebuild from the in-repo source of truth) landed in their own commits with rationale.

Jetson and Windows sections are scaffolded with cross-pollination from the Mac validation applied. Both sections carry `<NEEDS-PORT-VALIDATION>` markers identifying assertions that need confirmation on the hardware. The next build sequences run Phases 0 through 5 against actual Jetson AGX Orin and Windows 11 machines.

Continuous post-launch revisions land in their own commits per the project template. Significant changes get summarized in `REVISIONS.md` when that file exists. Until then, the commit log is the record.

Read `JOURNEY.ipynb` for the build narrative phase by phase. Read `operations/` for the post-Phase-5 operational prompts (drift-check widening, `~/.claude/` rebuild, the documentation closeout sequence that produced this README).

The repo is alive. If you find a factual error, a broken link, or a real vulnerability concern, file an issue or email per `SECURITY.md`. If you find a typo, a PR is welcome. If you want to propose a different architecture, the closed-without-merge response is not personal. The locked decisions are load-bearing.

## License, security, contact

**License.** MIT. See `LICENSE`. The license covers the code, configuration, and documentation in this repo. The three documents under `research/` carry their own licenses and are included for reference.

**Security.** Vulnerability disclosure policy in `SECURITY.md`. The harness's threat model lives in `foundation/01-threat-model.md`. Reports go to `security@rockcyber.com` with a triage target of five business days. Out-of-scope items (Claude Code itself, third-party seeds referenced by the seed evaluation documents) get redirected upstream.

**Repo.** `github.com/rocklambros/harness-engineering`.

**Citation.** Rock Lambros (RockCyber), *harness-engineering*, github.com/rocklambros/harness-engineering, 2026.

## Conventions for reading the repo

Commit messages follow a fixed template: a one-line summary, then a `Context` block (what was happening), a `Decision` block (what was chosen), a `Why` block (the reasoning, anchored to a QC ID or a piece of evidence), and a `Tradeoff` block (what was given up). The template is the same on every commit so the rationale stays close to the change. Reading the commit log is a faster way to follow the build than reading the phase outputs in isolation.

Writing conventions for every artifact in this repo: American English, active voice, plain words. No em dashes. No semicolons. No sentences starting with conjunctions. No AI filler. No corporate slop. Paragraphs over bullets. Bullets only for three to seven discrete items where visual separation aids comprehension. The voice is educational and first-person, modeled on `rocklambros/zerg` and `rocklambros/TRACT`.

If you need to find the rationale for a specific decision, three places hold it. The relevant `foundation/` document carries the principle-level reasoning. The platform `ARCHITECTURE.md` carries the platform-specific operationalization. The commit message on the change that introduced the decision carries the immediate context. The three layers correspond to three different reader questions: "why does this kind of decision get made this way," "why does it look this way on this platform," and "why did it land in this commit at this time."
