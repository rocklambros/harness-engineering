# Harness Engineering for Claude Code

A reference repository documenting how I built a production-grade Claude Code harness across three platforms: macOS, NVIDIA Jetson AGX Orin, and Windows. The reasoning is the artifact. The code is supporting evidence.

This is not a clone-and-run template. Personal-specific configuration is the point. Read it to see how a harness gets reasoned into existence, then build your own.

## Why this exists

I needed a Claude Code setup that I could trust to write code across three machines without spending an hour at session start re-configuring trust boundaries, re-installing tooling, and re-stating what the project is. I also needed a setup where security wasn't bolted on after generation, because the data on benign-prompt vulnerability rates in frontier LLMs is bad enough that "fix it in code review" stops being a defensible answer once you understand the rate.

Adopting someone else's harness off the shelf was the obvious shortcut. I tried that. The off-the-shelf options collapse into three categories: opinionated stacks that assume a workflow I don't share, security guardrails that don't survive cross-platform parity, and personal repos that drift from upstream Claude Code faster than the maintainer can patch. Every one of them solved 60% of my problem and left the other 40% as homework. The homework is the interesting part.

So I built it from scratch and wrote down why I made every choice. That writing is what this repo is.

## What's in here

The repo is organized into one foundation section (the thinking that's identical across all three platforms) and three platform sections (the build sequences specific to each).

**`foundation/`** holds the Quality Contract, the threat model, the architectural principles, the seed evaluation methodology, and the research references. These bind every artifact in every platform section. Read these first if you want to understand the design intent.

**`mac/`** is the validated reference build. Phase 0 through Phase 5 prompts are written and tested against my actual environment. If you want to see what a fully-realized harness looks like, start here.

**`jetson/`** and **`windows/`** mirror the Mac structure. Phase 0 through Phase 2 are written and ready. Phase 3 through Phase 5 are scaffolded with explicit "needs validation when ported" markers because I haven't run them against those environments yet. Capabilities are identical to Mac, tools differ where they have to.

**`research/`** holds the three source documents that ground the design decisions: the Liu et al. reverse engineering of Claude Code v2.1.88, the SAGE harness engineering systems-architecture analysis, and NIST SP 800-218.

## The build-vs-adopt question

The honest answer for most people reading this is: don't build. Adopt. The cost of a harness is not in the writing. It's in the maintenance against an upstream that ships breaking changes on minor version bumps. The TTL cache regression in March 2026 alone was enough to silently halve the economics of half the harnesses in circulation before anyone noticed.

The case for building is narrow but real: you operate across multiple machines, you have a non-trivial security posture, you don't trust the off-the-shelf trust boundaries, and you can afford the time to keep a reasoning trail current. If that's you, this repo shows the shape.

## How to read this repo

Read `foundation/00-quality-contract.md` first. It binds everything else.

Then pick your path:

If you want to adopt the harness in your own project, read `USER_GUIDE.md`. Quickstart, daily commands, troubleshooting.

If you want the cross-platform technical reference, read `HARNESS_GUIDE.md`. Five layers, three-layer security stack, tool equivalency, build sequence.

If you want the full validated build with all reasoning intact, read `mac/` start to finish. The Jetson and Windows sections mirror the same structure for those platforms.

Each platform section opens with a `README.md` that routes to its `ARCHITECTURE.md` (what the harness does and why), then to `prompts/` (the phase-by-phase build sequence), then to `harness/` (the actual files that ship), then to `evaluations/` (how seed tools were evaluated).

Commit history is part of the artifact. Every commit follows the template in `foundation/02-architectural-principles.md`. Read commits in order and the rationale chain is visible.

## What ships in the harness

Each platform produces a harness with the same five-layer shape:

A project-level `CLAUDE.md` under 200 lines, TRACT-pattern (Role, code standards, security rules, core constraints, things-that-break, operational, status). A `settings.json` template with permission mode, hook registrations, and trust-boundary configuration. A deterministic rules layer that defines what cannot be bypassed by advisory prompting. A skills layer that lazy-loads guidance on demand. A hooks layer that enforces the deterministic gates and the SecureForge-style commit-time validation feedback loop. An agents layer for specialized sub-tasks.

Each layer is justified in `ARCHITECTURE.md` and traced to a Quality Contract property.

## Security posture

The harness implements a three-layer defense:

Pre-generation guidance flows through a security-review skill seeded from the Arcanum-Sec/sec-context anti-pattern taxonomy (CC BY 4.0, attributed to Jason Haddix). The skill loads pattern sections by file type, keeping the context tax small.

Commit-time hardening runs Semgrep on changed files after every Write or Edit through a PostToolUse hook. Findings feed back to Claude with line and rule context so it fixes before continuing. This is the methodology from Liu et al. (SecureForge, MIT license) Appendix C, implemented as a deterministic hook rather than advisory guidance.

Post-generation validation runs the full SAST stack (Semgrep, gitleaks, trivy, syft, grype) at the pre-commit gate. Same tools, different invocation context, redundancy by design.

The reasoning for this layout is in `foundation/01-threat-model.md` and the Quality Contract section QC.1.

## License

MIT. Use the patterns. Cite the repo if you adapt them.

## Status

Build phase. Mac section validated through Phase 5. Jetson and Windows scaffolded through Phase 2, awaiting hardware validation for Phase 3-5. Revisions land as the harness evolves, with rationale in commit messages. See `JOURNEY.md` for the running narrative.
