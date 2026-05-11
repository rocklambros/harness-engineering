# Seed Evaluation Methodology

A "seed" is an external project the harness might draw from: an open-source Claude Code configuration repo, a hook library, a skill collection, a security tool with an MCP server. The set of plausible seeds is much larger than the set the harness can actually integrate. This document describes how candidates get evaluated.

The methodology has one goal: kill obvious dead ends fast, then put real effort into the survivors. The failure mode it prevents is evaluation theater, the practice of producing detailed rubric scores for every candidate without ever running any of them.

## The two stages

### Stage 1: Pre-filter (~30 seconds per candidate)

Three questions. Any "no" rejects the candidate.

1. **License**: Is the license compatible with this repo's MIT license and with the candidate's intended use here? GPL-licensed tools cannot live in this repo's source tree; they can be invoked as subprocesses if their CLI license permits. SSPL, BSL, and similar source-available licenses are case-by-case.
2. **Architecture support**: Does the candidate work on Mac (Apple Silicon), Jetson AGX Orin (ARM64 Linux), and Windows (x86_64)? Where it does not, is the gap acceptable for this component, or is a per-platform equivalent required?
3. **Maintainership**: Has the project shipped a commit in the last 90 days, and does the issue tracker show real responses? Dead projects are not seeds. Pre-1.0 projects with active maintenance are acceptable; the harness will pin to the current version and re-evaluate on upgrade.

Pre-filter results land in the phase output (typically `phase-outputs/INVENTORY.md` from Phase 1 or in the per-phase notes from Phase 3 and Phase 4). Each rejected candidate gets one sentence of rationale, not a paragraph.

The 30-second target is real. Pre-filter is a triage step, not a deep dive. If a candidate takes 10 minutes to pre-filter, the methodology is failing and the question framing needs to be tightened.

### Stage 2: Deep evaluation (sandbox integration)

Survivors move to Stage 2. The mechanism is integration, not scoring.

The candidate gets wired into a sandboxed session of the harness during Phase 3 (deterministic layer) or Phase 4 (extension layer), depending on what it touches. The Phase 3/4 prompt names the candidate and the integration scope. The session runs the candidate against three exercises:

1. **A nominal task** that the candidate is supposed to do well.
2. **An edge case** that exercises the failure mode the threat model worries about.
3. **A no-op interaction** to measure the cost of having the candidate installed and idle (cache footprint, startup time, tool pool inflation).

The phase output records, for each candidate:

- What the candidate did well.
- What it did badly, with the specific failure mode named.
- What it cost (cache tokens, startup latency, tool slot, mental complexity).
- The decision: integrate, integrate with constraints, reject.

If the decision is integrate-with-constraints, the constraints become hook rules or deny patterns in the same phase. Constraints in CLAUDE.md only (advisory) do not count as constraints for this purpose; QC architectural principle 1 (hooks enforce, CLAUDE.md advises) applies.

## What's not in the methodology

**No rubric scoring.** Rubric scoring on harness seeds is mostly noise. The qualities that matter (cache behavior, interaction with the permission system, prompt injection resilience, drift over upgrades) do not score cleanly on a 1-to-5 scale, and the qualities that score cleanly on 1-to-5 (star count, README polish, presence of tests) are not the qualities that determine harness fit.

**No exhaustive matrix.** A 15-column matrix comparing 20 seeds across every conceivable dimension is the visible artifact of evaluation theater. The methodology rejects this output by design. The phase output is a short narrative per survivor, not a spreadsheet.

**No vendor pitch trust.** A vendor's claim that their product "works with Claude Code" is data, not evidence. The Stage 2 integration is the evidence.

## Seeds slated for evaluation in this build

Listed in the CHECKPOINT and carried into the Phase 1 and Phase 3/4 prompts. Captured here as a snapshot; the live list is in the phase outputs.

- **Configuration repos and skill libraries**: `obra/superpowers`, `affaan-m/everything-claude-code`, `disler/claude-code-hooks-mastery`, the official `anthropics/claude-code` skills and plugins.
- **Security tools**: Semgrep (already installed), `gitleaks`, `trivy`, `syft` (SBOM), `grype`, `cyclonedx-cli`, `sigstore/cosign`, `osv-scanner`, `detect-secrets`.
- **Specialized integrations**: `cosai-oasis/project-codeguard` (pre-1.0, integrating in a shape that allows future swap), MemPalace (already installed, evaluating against alternatives), Serena (already installed).

Each gets pre-filtered in Phase 1 or Phase 3 (depending on whether the discovery scan finds it on the machine). Pre-filter survivors get deep-evaluated in Phase 3 or Phase 4 as the layer matches.

## What changes when a seed gets adopted

Adoption produces three artifacts in the same commit:

1. The wiring change (config, MCP server registration, skill copy, hook script).
2. The rationale, either in the commit message under "Why" or in the phase output. Names the failure mode the seed prevents and the alternative seeds rejected.
3. The drift trigger: a line in `mac/ARCHITECTURE.md` (and equivalents) recording the seed's version pin and the next re-evaluation trigger (upstream major version, security advisory, periodic review date).

Adoption is the start of a maintenance commitment, not the end of an evaluation.

## When the methodology is wrong

The methodology trades exhaustive coverage for speed. The known failure mode: a seed that would have been transformative gets rejected at the pre-filter because the maintainership signal looked wrong. The mitigation: the post-launch revision cadence is the second chance. Seeds that get rejected here can come back later when the signals change. The methodology does not produce a final verdict; it produces the current decision.

Trying to make this methodology produce a final verdict is how evaluation theater starts.
