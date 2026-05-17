# Seed Evaluation Methodology

Every external tool, repo, or pattern considered for adoption goes through this rubric. The point is to kill obvious dead ends quickly and reserve deep evaluation for survivors.

The methodology is two-stage: pre-filter, then deep evaluation. Most candidates die at pre-filter. The deep evaluation happens only for candidates that survive, and it happens in a sandbox by actually wiring the tool up, not by reading documentation.

This document includes a worked example at the bottom from the May 2026 evaluation of Arcanum-Sec/sec-context and Stanford SecureForge.

---

## Stage 1: Pre-filter

The pre-filter takes 30 seconds per tool. It is intentionally fast and intentionally harsh. The cost of running pre-filter on 50 candidates is lower than the cost of running deep evaluation on one wrong candidate.

The pre-filter has three gates. Failure on any gate ends the evaluation.

### Gate 1: License

The tool's license must be compatible with the repo's MIT license for any code we'd actually import. CC BY 4.0 is acceptable for content we'd attribute, not for code we'd embed. GPL, AGPL, and non-commercial-only licenses are killers unless we're using the methodology only (re-implementing from the paper rather than embedding the code).

If the license is unstated, the tool fails the gate. "Open source" without a LICENSE file is not open source.

### Gate 2: Architecture support

The tool must run on all three target architectures: macOS on Apple Silicon (ARM64), NVIDIA Jetson AGX Orin (ARM64 with Tegra extensions), and Windows on x86-64 (with WSL2 acceptable).

A tool that's macOS-only fails the gate. A tool that's Linux-only is acceptable on Mac via Homebrew and on Jetson natively, and acceptable on Windows via WSL2.

A tool that requires GPU acceleration not available on all three platforms fails the gate unless we accept the capability gap, which requires an explicit decision in AP.3.

### Gate 3: Maintainership

The tool must show evidence of active maintenance. Concrete signals:

Commits within the last 90 days, or a stated release cadence that's still being honored.

Multiple contributors, or a single maintainer with a track record of multi-year sustained work.

Issue response time under 30 days for high-severity issues.

A clear governance model for security disclosures.

A tool with one commit ever, no contributors beyond the original author, and no security policy fails the gate. A tool with active maintenance but a single point of failure passes the gate but is flagged for the deep evaluation to weigh against alternatives.

---

## Stage 2: Deep evaluation

Survivors of the pre-filter get wired into a Phase 3 or Phase 4 sandbox. The deep evaluation has five dimensions, each scored on a 1-5 scale. A candidate must score 3 or higher on every dimension to be adopted.

### Dimension 1: Capability fit

Does the tool solve the actual problem, or does it solve a related problem we'd have to bend to match? Scored on how closely the tool's intended use case matches our use case.

A tool that solves exactly our problem scores 5. A tool that solves a superset and can be configured down scores 4. A tool that solves a subset and would need to be supplemented scores 3. A tool that solves a tangential problem we'd be bending into shape scores 1-2.

### Dimension 2: Quality Contract alignment

Does the tool's behavior align with QC.1 through QC.5? Specifically:

QC.1: Does the tool produce auditable security outputs in a standard format (SARIF, CycloneDX, OSV)?

QC.2: Does the tool's footprint match the problem, or does it bring far more than we need?

QC.4b: Does the tool's context cost match its value? Tools that demand large context budgets need to deliver proportionally.

QC.5: Does the tool pin its own dependencies, or does it float?

### Dimension 3: Integration cost

How much code does it take to integrate the tool into the harness? Scored on lines-of-glue, configuration complexity, and the number of moving parts that have to stay aligned across platform sections.

A tool that integrates with a single binary call and one configuration file scores 5. A tool that requires a service running alongside Claude Code scores 2-3. A tool that requires custom scripting per platform scores 1.

### Dimension 4: Replaceability

If the tool fails (becomes unmaintained, changes license, ships a breaking change), how hard is it to replace? Scored on the structural commitment the harness makes to the tool.

A tool we call through a generic interface (SAST runner that consumes SARIF) is highly replaceable: score 5. A tool that's deeply embedded in our hook scripts and skill content is poorly replaceable: score 2. A tool whose data formats are proprietary and can't be migrated scores 1.

### Dimension 5: Maintenance burden

How much ongoing attention does the tool demand? Scored on update cadence, breaking-change frequency, and the cost of keeping pinned versions current.

A tool with one stable release per year and consistent CLI interfaces scores 5. A tool with monthly breaking changes scores 2. A tool that requires re-reading documentation every quarter scores 1.

### Adoption decision

A candidate that scores 3 or higher on every dimension is adopted. A candidate with any dimension below 3 is either rejected or has the failing dimension addressed before reconsidering.

Tied candidates fall back to the principle in AP.6: adopt where possible, build where necessary. If two adoptable tools tie, pick the one with the smaller integration cost.

---

## Worked example: sec-context and SecureForge (May 16, 2026)

### Candidate 1: Arcanum-Sec/sec-context

Pre-filter:

License: CC BY 4.0, attribution to Jason Haddix and Arcanum Information Security. Pass for content reference, not for code import.

Architecture support: text-based markdown content, platform-agnostic. Pass.

Maintainership: 12 commits, single-org (Arcanum-Sec), 573+ stars, recent activity 2025-2026. Pass with flag (single point of failure).

Survived pre-filter, proceeded to deep evaluation.

Deep evaluation:

Capability fit: 3. The taxonomy covers the right anti-patterns for our threat model T.1, but the delivery mechanism (65K-100K token markdown docs) is not how we'd use it.

QC alignment: 2. QC.4b fails if loaded wholesale; passes if used as content seed for a lazy-loaded skill.

Integration cost: 4 if used as content seed, 1 if used as direct context import. We're using as content seed.

Replaceability: 5. It's reference content. Replacing it means re-curating from primary sources.

Maintenance burden: 3. Content drifts as the CWE landscape shifts. Not a code dependency, but a content review cadence is needed.

Adoption decision: adopted as content seed for the `security-review` skill. Attribution maintained per CC BY 4.0. Deep-pattern content extracted and rewritten to repo voice during Phase 4.

### Candidate 2: Stanford SecureForge

Pre-filter:

License: MIT (confirmed via Rock May 16, 2026). Pass.

Architecture support: Python pipeline, runs anywhere Python and Semgrep run. Pass.

Maintainership: Stanford research artifact, paper published 2026. Stanford SISL lab has multi-year track record. Pass.

Survived pre-filter, proceeded to deep evaluation.

Deep evaluation:

Capability fit: 3. The methodology (commit-time hardening via Semgrep feedback loop) maps cleanly to our threat model T.1. The artifact (optimized system prompts) maps poorly, because they target single-turn Python generation against specific model versions and we run Claude Code as a multi-turn agent.

QC alignment: 4. SARIF-compatible Semgrep output, pins via pip, well-documented.

Integration cost: 2 for the full pipeline, 4 for the Appendix C commit-time hardening pattern. We're adopting only the latter.

Replaceability: 4. The Appendix C pattern is generic enough that any SAST-feedback hook implements it. Locking in to SecureForge specifically is unnecessary.

Maintenance burden: 3. The pipeline ages with model versions; the Appendix C pattern is stable.

Adoption decision: adopted as methodology, not as artifact. The commit-time hardening hook implements Appendix C using Semgrep. The optimized prompts are not adopted. The full pipeline is reserved for optional periodic runs against Rock's actual workload to discover Claude-Code-specific failure modes.

### Combined integration

The `security-review` skill (Phase 4) is seeded from the sec-context top-10 ranking and deep-pattern content, normalized to repo voice, attributed under CC BY 4.0.

The `post-tool-use-semgrep.sh` hook (Phase 3) implements the SecureForge Appendix C commit-time hardening pattern.

The full pre-commit SAST stack remains in place as the post-generation validation layer.

This three-layer composition is the implementation of AP.2.

---

## What this methodology does not cover

This methodology evaluates individual tools and patterns. It does not evaluate architectural decisions or build-vs-adopt questions at the harness level. Those go through the foundation docs and phase prompts.

It does not evaluate the Anthropic platform itself, the Claude Code agent, or the underlying models. Those are accepted as the substrate the harness runs on.

It does not produce paper rubrics divorced from integration. Reject "evaluation theater" where a tool scores 5 across the board on paper and then nobody actually wires it up. The Stage 2 evaluation is gated on actually integrating the tool into a sandbox.
