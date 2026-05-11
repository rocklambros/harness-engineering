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
| `obra/superpowers` | MIT (verified in plugin cache LICENSE) | yes (installed, v5.1.0) | `<TBD-PHASE-3>` | `<TBD-PHASE-3>` | active (plugin lastUpdated 2026-05-05) | `<TBD-PHASE-4>` | Installed as Claude Code plugin via claude-plugins-official marketplace |
| `affaan-m/everything-claude-code` | `<TBD-PHASE-3>` | not installed | `<TBD-PHASE-3>` | `<TBD-PHASE-3>` | `<TBD-PHASE-3>` | `<TBD-PHASE-4>` | Not on machine; Phase 3 web-checks license and maintainership |
| `disler/claude-code-hooks-mastery` | `<TBD-PHASE-3>` | not installed | `<TBD-PHASE-3>` | `<TBD-PHASE-3>` | `<TBD-PHASE-3>` | `<TBD-PHASE-4>` | Not on machine; Phase 3 web-checks license and maintainership |
| `anthropics/claude-code` skills and plugins | Anthropic | yes | yes | yes | active | `<TBD-PHASE-3>` | First-party, baseline reference |

### Security tools

| Candidate | License | Mac | Jetson | Windows | Maintainership | Result | Rationale |
|---|---|---|---|---|---|---|---|
| `semgrep` | LGPL (Pro: BSL) | yes (installed at /opt/anaconda3/bin/semgrep, broken per Phase 0; Phase 3 re-verifies) | yes | yes | active | `<TBD-PHASE-3>` | Installed already; deep-eval in Phase 3 |
| `gitleaks` | MIT | yes (installed v8.30.0 via Homebrew) | yes | yes | active (Homebrew formula, recent version) | `<TBD-PHASE-3>` | Already installed; Phase 3 deep-evaluates against detect-secrets |
| `trivy` | Apache-2.0 | yes (installed v0.69.0 via Homebrew) | yes | yes | active (Homebrew formula, recent version) | `<TBD-PHASE-3>` | Already installed; Phase 3 evaluates as IaC + container scanner |
| `syft` | Apache-2.0 | yes (not installed) | yes | yes | `<TBD-PHASE-3>` | `<TBD-PHASE-3>` | SBOM generator; QC.1 PS.2.1 candidate; Phase 3 installs if adopted |
| `grype` | Apache-2.0 | yes (not installed) | yes | yes | `<TBD-PHASE-3>` | `<TBD-PHASE-3>` | Vulnerability scanner; Phase 3 considers as syft companion |
| `cyclonedx-cli` | Apache-2.0 | yes (not installed) | yes | yes | `<TBD-PHASE-3>` | `<TBD-PHASE-3>` | SBOM tooling; Phase 3 considers if syft+grype don't cover the format need |
| `sigstore/cosign` | Apache-2.0 | yes (not installed) | yes | yes | `<TBD-PHASE-3>` | `<TBD-PHASE-3>` | Sigstore signing; Phase 3 considers for QC.1 PS.2.1 release integrity |
| `osv-scanner` | Apache-2.0 | yes (not installed) | yes | yes | `<TBD-PHASE-3>` | `<TBD-PHASE-3>` | OSV vulnerability scanning; Phase 3 considers as grype alternative |
| `detect-secrets` | Apache-2.0 | yes (binary NOT installed; pre-commit hook wired in Batch 1) | yes | yes | active | survive (pre-commit wired; Phase 3 installs binary) | Wired in Batch 1 pre-commit but binary missing on this machine per Phase 0/1 |

### Specialized integrations

| Candidate | License | Mac | Jetson | Windows | Maintainership | Result | Rationale |
|---|---|---|---|---|---|---|---|
| `cosai-oasis/project-codeguard` | `<TBD-PHASE-4>` | not installed | `<TBD-PHASE-4>` | `<TBD-PHASE-4>` | pre-1.0 | `<TBD-PHASE-4>` | Pre-1.0; not on machine; Phase 4 web-checks license and integrates with future-swap shape |
| MemPalace | MIT (verified in marketplace LICENSE) | yes (plugin v3.3.2 + binaries at /opt/anaconda3/bin/) | `<TBD-PHASE-4>` | `<TBD-PHASE-4>` | active (installed 2026-04-23; daily LaunchAgent at 03:00) | `<TBD-PHASE-4>` | Evaluate against alternatives; not auto-adopt |
| Serena | `<TBD-PHASE-4>` (plugin local cache is stub only; full source at github:oraios/serena needs web check) | yes (plugin installed but DISABLED in user settings.json) | `<TBD-PHASE-4>` | `<TBD-PHASE-4>` | active per plugin marketplace (lastUpdated 2026-03-26), but user-disabled | `<TBD-PHASE-4>` | Evaluate against alternatives; not auto-adopt; current disabled state is a user-policy choice |

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
