# Pre-filter worksheet (Mac)

Records the 30-second triage decisions per seed candidate. The methodology is in `foundation/03-seed-evaluation-methodology.md`. This file is the operational log for the Mac build.

Pre-filter asks three questions per candidate. Any "no" rejects. Survivors move to `deep-eval.md`.

1. **License**: Is the license compatible with this repo's MIT and with the candidate's intended use here?
2. **Architecture support**: Does the candidate work on Mac (Apple Silicon), Jetson AGX Orin (ARM64 Linux), and Windows (x86_64)? If not, is the gap acceptable or is a per-platform equivalent required?
3. **Maintainership**: Commit in the last 90 days, and issue tracker shows real responses?

Each row is one candidate. Rationale fits in one sentence when a candidate is rejected. Survivors carry forward to deep evaluation in Phase 3 or Phase 4.

## Format

| Candidate | License | Mac | Jetson | Windows | Maintainership | Result | Rationale |
|---|---|---|---|---|---|---|---|
| `<candidate>` | `<TBD-PHASE>` | `<TBD-PHASE>` | `<TBD-PHASE>` | `<TBD-PHASE>` | `<TBD-PHASE>` | survive / reject | `<one sentence>` |

## Seeds from CHECKPOINT slated for evaluation

The list below carries forward from `CHECKPOINT.md` and `foundation/03-seed-evaluation-methodology.md`. Phase 1 (discovery) updates this table with what's already on the machine. Phase 3 (deterministic-layer candidates) and Phase 4 (extension-layer candidates) update the per-candidate result and rationale.

### Configuration repositories and skill libraries

| Candidate | License | Mac | Jetson | Windows | Maintainership | Result | Rationale |
|---|---|---|---|---|---|---|---|
| `obra/superpowers` | `<TBD-PHASE-1>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` |
| `affaan-m/everything-claude-code` | `<TBD-PHASE-1>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` |
| `disler/claude-code-hooks-mastery` | `<TBD-PHASE-1>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` |
| `anthropics/claude-code` skills and plugins | Anthropic | yes | yes | yes | active | `<TBD-PHASE-3>` | First-party, baseline reference |

### Security tools

| Candidate | License | Mac | Jetson | Windows | Maintainership | Result | Rationale |
|---|---|---|---|---|---|---|---|
| `semgrep` | LGPL (Pro: BSL) | yes | yes | yes | active | `<TBD-PHASE-3>` | Installed already; deep-eval in Phase 3 |
| `gitleaks` | MIT | yes | yes | yes | `<TBD-PHASE-1>` | `<TBD-PHASE-3>` | `<TBD>` |
| `trivy` | Apache-2.0 | yes | yes | yes | `<TBD-PHASE-1>` | `<TBD-PHASE-3>` | `<TBD>` |
| `syft` | Apache-2.0 | yes | yes | yes | `<TBD-PHASE-1>` | `<TBD-PHASE-3>` | SBOM generator; QC.1 PS.2.1 candidate |
| `grype` | Apache-2.0 | yes | yes | yes | `<TBD-PHASE-1>` | `<TBD-PHASE-3>` | `<TBD>` |
| `cyclonedx-cli` | Apache-2.0 | yes | yes | yes | `<TBD-PHASE-1>` | `<TBD-PHASE-3>` | `<TBD>` |
| `sigstore/cosign` | Apache-2.0 | yes | yes | yes | `<TBD-PHASE-1>` | `<TBD-PHASE-3>` | `<TBD>` |
| `osv-scanner` | Apache-2.0 | yes | yes | yes | `<TBD-PHASE-1>` | `<TBD-PHASE-3>` | `<TBD>` |
| `detect-secrets` | Apache-2.0 | yes | yes | yes | active | survive | Wired in Batch 1 pre-commit |

### Specialized integrations

| Candidate | License | Mac | Jetson | Windows | Maintainership | Result | Rationale |
|---|---|---|---|---|---|---|---|
| `cosai-oasis/project-codeguard` | `<TBD-PHASE-1>` | `<TBD>` | `<TBD>` | `<TBD>` | pre-1.0 | `<TBD-PHASE-4>` | Pre-1.0; integration shape allows future swap |
| MemPalace | `<TBD-PHASE-1>` | yes (installed) | `<TBD>` | `<TBD>` | `<TBD-PHASE-1>` | `<TBD-PHASE-4>` | Evaluate against alternatives, not auto-adopt |
| Serena | `<TBD-PHASE-1>` | yes (installed) | `<TBD>` | `<TBD>` | `<TBD-PHASE-1>` | `<TBD-PHASE-4>` | Evaluate against alternatives, not auto-adopt |

## Rejected candidates

Each rejection lands here with the one-sentence rationale. Examples of what gets rejected:

- Repositories with no commit in the last 12 months (rejected on maintainership).
- Tools with hard dependencies on x86-only binaries (rejected on architecture support, unless a per-platform equivalent exists).
- Tools under SSPL or BSL licenses where the harness's intended use violates the license terms (rejected on license).

Phase 1 and Phase 3 add rejected entries here as they encounter them. Phase 5 reviews the rejection list for any candidate that should be reconsidered.

## Notes on the methodology

The 30-second target is real. If pre-filter on a candidate takes 10 minutes, the question framing is failing. Tighten the question, not the time budget.

Rubric scoring on a 1-to-5 scale is not allowed in this worksheet. The methodology rejects it by design. The result column is binary: survive or reject. The rationale is qualitative.

The post-launch revision cadence is the appeal mechanism for rejected candidates. A seed rejected here at the pre-filter is not rejected forever. Signals change, and the methodology produces the current decision, not a final verdict.
