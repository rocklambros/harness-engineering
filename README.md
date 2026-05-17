# Harness Engineering for Claude Code

A reference repository documenting how I built a production-grade Claude Code harness across three platforms: macOS, NVIDIA Jetson AGX Orin, and Windows. The reasoning is the artifact. The code is supporting evidence.

This is not a clone-and-run template. Personal-specific configuration is the point. Read it to see how a harness gets reasoned into existence, then build your own.

## Why this exists

I needed a Claude Code setup that I could trust to write code across three machines without spending an hour at session start re-configuring trust boundaries, re-installing tooling, and re-stating what the project is. I also needed a setup where security wasn't bolted on after generation, because the data on benign-prompt vulnerability rates in frontier LLMs is bad enough that "fix it in code review" stops being a defensible answer once you understand the rate.

Adopting someone else's harness off the shelf was the obvious shortcut. I tried that. The off-the-shelf options collapse into three categories: opinionated stacks that assume a workflow I don't share, security guardrails that don't survive cross-platform parity, and personal repos that drift from upstream Claude Code faster than the maintainer can patch. Every one of them solved 60% of my problem and left the other 40% as homework. The homework is the interesting part.

I built it from scratch and wrote down why I made every choice. That writing is what this repo is.

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

## How this repo was built

Every artifact here was produced with one development loop: brainstorm the design, write a plan, implement against the plan, review before merge. That loop is not mine. It comes from Superpowers, an agentic skills framework by Jesse Vincent (GitHub `obra`), MIT licensed, at https://github.com/obra/superpowers.

Superpowers is not part of the shipped harness. It is the development discipline that produced the harness. The separation is deliberate. The harness is what you adopt. Superpowers is how this repo got written. Keeping the two distinct is the same boundary this README draws everywhere else.

It earns the dependency. Superpowers injects a skill-discovery instruction at session start, so the brainstorm-before-code gate fires whether or not the operator remembers to ask for it. Its skills enforce the steps a model under time pressure skips: brainstorming separates intent from implementation before a line is written, the planning skill turns an agreed design into a reviewable plan, test-driven development and systematic debugging keep the implementation honest, and the code-review skills force a verification step before work is called done. For a repo whose thesis is that the reasoning is the artifact, a process that forces the reasoning to happen first and get written down is the right substrate.

Credit and license are unambiguous. Superpowers is Jesse Vincent's work, MIT licensed, used here as an external tool with attribution. None of its code ships in the harness. The patterns this repo demonstrates stand on their own, and the repo would not exist in this shape without it.

## What ships in the harness

Each platform produces a harness with the same five-layer shape:

A project-level `CLAUDE.md` under 200 lines, organized into seven sections (Role, code standards, security rules, core constraints, things-that-break, operational, status). A `settings.json` template with permission mode, hook registrations, and trust-boundary configuration. A deterministic rules layer that defines what cannot be bypassed by advisory prompting. A skills layer that lazy-loads guidance on demand. A hooks layer that enforces the deterministic gates and the SecureForge-style commit-time validation feedback loop. An agents layer for specialized sub-tasks.

Each layer is justified in `ARCHITECTURE.md` and traced to a Quality Contract property.

## Security posture

The harness implements a three-layer defense:

Pre-generation guidance flows through a security-review skill seeded from the Arcanum-Sec sec-context anti-pattern taxonomy (CC BY 4.0, Jason Haddix and Arcanum Information Security, https://github.com/Arcanum-Sec/sec-context). On the Mac reference build the skill is fully populated with ten pattern files matching its manifest. Jetson and Windows carry the scaffold with identical structure, pending hardware validation. The skill loads pattern sections by file type, keeping the context tax small.

Commit-time hardening runs Semgrep on changed files after every Write or Edit through a PostToolUse hook. Findings feed back to Claude with line and rule context so it fixes before continuing. This is the methodology from Liu et al. (SecureForge, MIT, arXiv:2605.08382, https://github.com/sisl/SecureForge) Appendix C, implemented as a deterministic hook rather than advisory guidance.

Post-generation validation runs the pinned pre-commit gate: the baseline pre-commit hooks, gitleaks for secrets, Semgrep for SAST, shellcheck for hook scripts, and the local drift check for reference integrity. The secondary supply-chain scanners (trivy, syft, grype) are evaluated and documented as optional in each platform's `evaluations/deep-eval.md`, not part of the pinned gate. Same Semgrep engine as the commit-time hook, different invocation context, redundancy by design.

The reasoning for this layout is in `foundation/01-threat-model.md` and the Quality Contract section QC.1.

## Attribution

External sources that ground this work. The canonical, versioned list is `foundation/04-research-references.md`. The intellectual-property attributions below are explicit and binding:

- **Arcanum-Sec sec-context anti-pattern taxonomy.** Jason Haddix and Arcanum Information Security. Licensed CC BY 4.0. https://github.com/Arcanum-Sec/sec-context. The `security-review` skill's pattern selection and ranking are derived from this taxonomy. Pattern prose is rewritten to this repo's voice with attribution preserved.
- **SecureForge.** Liu, Einstein, Yang, Baumann, Eddy, Manning, Kochenderfer, and Yang. arXiv:2605.08382. MIT. https://github.com/sisl/SecureForge. The commit-time static-analysis feedback methodology is adapted from this work.
- **NIST SP 800-218 Secure Software Development Framework.** U.S. National Institute of Standards and Technology. Public domain. Quality Contract QC.1 aligns to its practices.
- **MITRE Common Weakness Enumeration.** The MITRE Corporation. The security-review pattern files cite CWE identifiers from this catalog.
- **CISA Secure by Design.** U.S. Cybersecurity and Infrastructure Security Agency. Informs the security posture.
- **Superpowers.** Jesse Vincent (`obra`). MIT. https://github.com/obra/superpowers. The brainstorm, plan, implement, review workflow used to build this repo. Not part of the shipped harness. See "How this repo was built."

The reverse-engineering analysis of Claude Code internals and the SAGE systems-architecture analysis that inform the design are cited as R.1.1 and R.2.3 in `foundation/04-research-references.md`.

## License

MIT. Use the patterns. Cite the repo if you adapt them. The attributions above are independent of this license and survive any reuse.

## Status

Build phase. The Mac section is the validated reference build, including the now-populated Phase 4 security-review skill (ten pattern files plus the `security-reviewer` and `writer-reviewer` agents). Jetson and Windows are scaffolded through Phase 2, awaiting hardware validation for Phase 3-5. Revisions land as the harness evolves, with rationale in commit messages. See `JOURNEY.md` for the running narrative.
