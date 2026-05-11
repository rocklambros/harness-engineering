# harness-engineering

A reference repo for building a Claude Code harness from first principles, across three machines, with the reasoning preserved.

## Why I built my own harness instead of adopting one

The honest answer: I tried adopting one, and the things I needed to change to make it mine were the same things that made the adopted harness coherent. Stripping them out left me with a wrapper around someone else's habits. Keeping them in left me using a tool I did not trust under load.

There are at least six well-maintained Claude Code configuration projects worth reading. Affaan Mustafa's `everything-claude-code`. Jesse Vincent's `superpowers`. The official Anthropic skills and plugins. Disler's `claude-code-hooks-mastery`. The `awesome-harness-engineering` compilation. Each one is a real piece of work and each one encodes a particular set of opinions about how the agent loop should be shaped. Those opinions are the point. A harness without opinions is a config file with extra steps.

My opinions did not line up with any of theirs cleanly. The pieces I cared most about (a strict deterministic enforcement layer, identical capabilities across Mac, Jetson, and Windows, an explicit threat model for the harness itself, a seed evaluation methodology that rejects evaluation theater, and rationale preserved as a first-class artifact) were scattered across multiple repos in incompatible shapes. Splicing them together costs more than building the substrate myself and pulling in components as seeds.

This repo is what I built and why. It is not a clone-and-run template. The personal-specific decisions are the point. If you are reading it, the value is the reasoning, not the configuration.

## What's in here

The repo has a shared foundation and three platform sections.

**`foundation/`** holds the thinking that does not change across platforms. The Quality Contract that binds every phase. The threat model the harness defends against. The architectural principles, with the hooks-enforce-CLAUDE.md-advises split as the load-bearing decision. The seed evaluation methodology. The research reference index.

**`mac/`** is the validated build. macOS on Apple Silicon. Every phase has been written, executed, and reviewed against my actual environment. The Phase 3-5 prompts are battle-tested.

**`jetson/`** mirrors the Mac structure with Phase 0-2 written and Phase 3-5 scaffolded. The Jetson AGX Orin runs ARM64 Linux, and the harness components that differ (sandboxing model, MCP transport, package management) are flagged with "needs validation when ported." Filling in the gaps is the next maintenance pass.

**`windows/`** is the same pattern as `jetson/`. Phase 0-2 written, Phase 3-5 scaffolded. The Windows-specific divergences (PowerShell sandboxing rules, path semantics, credential storage) are flagged for validation.

**`research/`** holds the three documents the repo cites for authoritative claims: Liu et al.'s reverse engineering of Claude Code v2.1.88, the SAGE systems-architecture analysis of harness engineering, and NIST SP 800-218 v1.1.

**`scripts/drift-check.sh`** enforces the cache-discipline rules in the Quality Contract: total CLAUDE.md hierarchy under 400 lines, no timestamps in the cached prefix, no per-run state in cached files.

**`JOURNEY.ipynb`** is the build narrative, filled phase by phase as the harness gets built on each platform. Read this if you want the chronological story rather than the structural one.

## The five build phases

The harness is not all written at once. Five phases plus a Phase 0, executed sequentially on each platform. Every phase has a prompt in `<platform>/prompts/`. Every prompt follows the standard header (effort, mode, thinking, context budget, parallel tool calls, scope) so Claude Code parses it consistently.

**Phase 0** sets goals and writes the platform's `ARCHITECTURE.md`. What capabilities the harness must have. What the success conditions look like. What threats it explicitly does not defend against.

**Phase 1** discovers what's on the machine. Plan mode. Subagent spawned for the inventory scan because it touches more than 20 files. Synthesis in the main session.

**Phase 2** is the architecture interview. The model uses the `AskUserQuestion` tool to drive a focused conversation about which threats live in hooks, which seeds get pre-filtered, and what the platform-specific divergences look like.

**Phase 3** writes the deterministic layer. Hooks, deny rules, sandbox config, the permission posture. Anything that has to hold every time lands here.

**Phase 4** writes the extension layer. Skills, agents, MCP servers, the seeds that survived pre-filter. Each gets stress-tested in a sandboxed integration during the same session.

**Phase 5** wires everything and produces the documentation. A Reviewer subagent audits every change against the Quality Contract and the threat model. The phase output is a polished platform section ready for the next reader.

## What the repo is opinionated about

Six things, listed because hiding them would be dishonest. Each one is a position I hold with high but not absolute confidence, supported by evidence in the foundation documents.

**Hooks enforce, CLAUDE.md advises.** Claude Code's 27 hook events are deterministic. The model's compliance with CLAUDE.md is probabilistic. Any rule that must hold every time goes in a hook. Anything else goes in CLAUDE.md. The cost of getting this wrong compounds silently. *(See `foundation/02-architectural-principles.md`.)*

**Least privilege by default.** Every component starts with the minimum permission set that lets it do its declared job. Auto mode plus an explicit deny list beats `--dangerously-skip-permissions`. The 0.4% false-positive rate of the auto-mode classifier costs less than the threat surface bypass mode opens.

**Reversibility weights friction.** Reading is auto-approved. Writing inside the working directory is reversible from git. Writing outside the working directory triggers a hook. `git push` runs the test suite first. The friction matches the consequence.

**Identical capabilities across three platforms.** Mac, Jetson, Windows. One tool when possible, equivalent tool per platform when not. The cross-platform parity rule is what makes the harness portable and what keeps a future me from drifting into Mac-only habits.

**Seeds get integration-tested, not rubric-scored.** Pre-filter takes 30 seconds. Deep evaluation is wiring the candidate into a sandboxed session and watching what happens. Rubric scoring on harness seeds is mostly noise.

**Reasoning is the deliverable.** Commit messages name the tradeoff. Phase outputs preserve the reasoning chain. ARCHITECTURE files record the version pins and the next re-evaluation triggers. The harness as a set of config files is the cheap part. The harness as a record of why each line is the way it is, is the value.

## Reading order

If you came here to copy and paste, you are in the wrong repo. If you came here to learn how someone else thought about the problem so you can think about yours, the path is:

1. `foundation/02-architectural-principles.md` for the four principles.
2. `foundation/01-threat-model.md` for what the harness defends against.
3. `foundation/00-quality-contract.md` for the five properties that bind every phase.
4. `mac/README.md` to see a fully built platform section.
5. The Phase 0 through Phase 5 prompts in `mac/prompts/` to see how the prompts are structured.
6. `JOURNEY.ipynb` for the chronological version.

The order matters less than the discipline of reading the foundation before the platform sections. The platform sections make sense only against the foundation; the foundation makes sense only against the research documents.

## Status

Build target: end of May 2026. The repo is born public; revisions land as the harness evolves. Each post-launch revision lands with a commit message naming the threat or assumption the change addresses. There is no discrete dogfooding phase. Dogfooding is continuous and is the reason the repo exists.

Significant post-launch changes get summarized in `REVISIONS.md` when that file exists. Until then, the commit log is the record.

## Citing this repo

If you reference this work, the canonical attribution is:
> Rock Lambros (RockCyber), *harness-engineering*, github.com/rocklambros/harness-engineering, 2026.

The three research documents under `research/` carry their own citations and should be cited directly when referencing claims drawn from them.

## License

MIT. See `LICENSE`. The license covers code, configuration, and documentation in this repo. The three research documents under `research/` are not licensed under MIT and are included for reference under whatever license applies to each original document.

## Security

Vulnerability disclosure policy in `SECURITY.md`. The repo's threat model lives in `foundation/01-threat-model.md`.
