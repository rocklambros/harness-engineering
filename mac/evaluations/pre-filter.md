# Pre-filter worksheet (Mac)

Records the 30-second triage decisions per seed candidate. The methodology is in `foundation/03-seed-evaluation-methodology.md`. This file is the operational log for the validated Mac build (first build sequence 2026-05-11).

Pre-filter asks three questions per candidate. Any "no" rejects. Survivors move to `deep-eval.md`.

1. **License**: Is the license compatible with this repo's MIT and with the candidate's intended use here?
2. **Architecture support**: Does the candidate work on Mac (Apple Silicon), Jetson AGX Orin (ARM64 Linux), and Windows (x86_64)? If not, is the gap acceptable or is a per-platform equivalent required?
3. **Maintainership**: Commit in the last 90 days, and issue tracker shows real responses?

Each row carries one sentence of rationale where rejection or deferral is the result. Survivors land in `deep-eval.md` with the Stage 2 paragraph.

## Format

| Candidate | License | Mac | Jetson | Windows | Maintainership | Result | Rationale |
|---|---|---|---|---|---|---|---|

## Configuration repositories and skill libraries

| Candidate | License | Mac | Jetson | Windows | Maintainership | Result | Rationale |
|---|---|---|---|---|---|---|---|
| `obra/superpowers` | MIT (verified in plugin LICENSE) | yes (plugin v5.1.0 installed) | yes (plugin works cross-platform) | yes | active (lastUpdated 2026-05-05) | INTEGRATE | Phase 4 deep-eval; wholesale adoption, used across all build phases |
| `affaan-m/everything-claude-code` | not verified (not installed) | not on machine | not assessed | not assessed | not assessed | REJECT | Phase 4 paper eval: reference repo duplicates `foundation/` and `mac/ARCHITECTURE.md` |
| `disler/claude-code-hooks-mastery` | not verified (not installed) | not on machine | not assessed | not assessed | not assessed | REJECT | Phase 4 paper eval: Phase 3 hooks already cover Phase 2-elected threats; adopting broader collection would add hooks for skipped threats |
| `anthropics/claude-code` plugins | Anthropic (baseline) | yes (marketplace registered) | yes | yes | active | BASELINE | First-party reference; individual plugins evaluated per row in Specialized integrations |

## Security tools (Phase 3 deep-eval scope: deterministic layer)

| Candidate | License | Mac | Jetson | Windows | Maintainership | Result | Rationale |
|---|---|---|---|---|---|---|---|
| `gitleaks` | MIT | yes (v8.30.0 via Homebrew) | yes | yes | active (Homebrew formula recent) | INTEGRATE | Phase 3 deep-eval: 3 leaks detected on realistic-shape fixture at 58ms; pre-commit rewire from detect-secrets is post-Phase-5 |
| `trivy` | Apache-2.0 | yes (v0.69.0 via Homebrew) | yes | yes | active | INTEGRATE | Phase 3 deep-eval: 5 secrets detected, broader content coverage than gitleaks; complementary integration |
| `semgrep` | LGPL (Pro: BSL) | yes (Anaconda install broken with ImportError) | yes | yes | active | INTEGRATE-WITH-CONSTRAINTS | Phase 3 deep-eval: pipx install in separate venv (post-Phase-5); the Anaconda install ripple effects are out of scope |
| `detect-secrets` | Apache-2.0 | not installed (pre-commit wire references missing binary) | yes (if installed) | yes (if installed) | active | REJECT | Phase 3 deep-eval: superseded by gitleaks; pre-commit rewire is post-Phase-5 |
| `syft` | Apache-2.0 | not installed | yes | yes | active | DEFER | SBOM generator; QC.1 PS.2.1 candidate; revisit when release-time SBOM workflow lands |
| `grype` | Apache-2.0 | not installed | yes | yes | active | DEFER | Vulnerability scanner; revisit alongside syft if SBOM workflow adopts both |
| `cyclonedx-cli` | Apache-2.0 | not installed | yes | yes | active | DEFER | SBOM tooling; revisit if syft+grype do not cover the format need |
| `sigstore/cosign` | Apache-2.0 | not installed | yes | yes | active | DEFER | Sigstore signing; QC.1 PS.2.1 release integrity candidate; revisit at first release |
| `osv-scanner` | Apache-2.0 | not installed | yes | yes | active | DEFER | OSV vulnerability scanning; grype alternative; revisit if grype coverage gap |

## Specialized integrations (Phase 4 deep-eval scope: extension layer)

| Candidate | License | Mac | Jetson | Windows | Maintainership | Result | Rationale |
|---|---|---|---|---|---|---|---|
| `cosai-oasis/project-codeguard` | not verified (pre-1.0, not installed) | not on machine | not assessed | not assessed | pre-1.0 | DEFER | Phase 3 deep-eval: pre-1.0; integration shape Phase 3 built supports future swap; revisit at 1.0 release or agentcontrolstandard.ai ship |
| `MemPalace` | MIT (verified in marketplace LICENSE) | yes (plugin v3.3.2 + binaries) | not assessed | not assessed | active (installed 2026-04-23; daily LaunchAgent) | INTEGRATE | Phase 4 deep-eval: cross-session structured memory complements native auto-memory; known add_drawer bug with deterministic workaround |
| `Serena` | not verified (plugin local cache is stub; full source at `oraios/serena`) | yes (plugin installed but user-disabled) | not assessed | not assessed | active per marketplace (lastUpdated 2026-03-26) | DEFER | Phase 4 deep-eval: respect user's deliberate disable signal in `~/.claude/settings.json`; revisit on specific code-navigation use case |
| `goodmem@claude-plugins-official` | not verified (plugin) | yes (plugin enabled in Rock's daily-driver) | not assessed | not assessed | active per marketplace | DEFER | Phase 4 surfaced as MemPalace alternative; rejected by MemPalace's deep-eval (redundant); Phase 5 daily-driver review may keep alongside or drop |
| `context7@claude-plugins-official` | not verified (plugin) | yes (plugin enabled in Rock's daily-driver) | not assessed | not assessed | active | DEFER | Phase 4 surfaced: plugin's `.mcp.json` uses unpinned `npx -y @upstash/context7-mcp`; daily-driver review (post-Phase-5) picks pin vs global-install vs skip |

## Other currently-enabled plugins from Phase 1 inventory

These 11 plugins are enabled in Rock's current `~/.claude/settings.json` but not in the calibrated harness reference. Each gets a daily-driver review pass (post-Phase-5) under the `mcp-server-pre-trust-audit` and `seed-evaluation` skills.

| Plugin | Result | Rationale |
|---|---|---|
| `github` | DEFER (likely keep) | gh CLI integration heavily used; audit pass routine |
| `playwright` | DEFER (likely keep) | E2E browser testing; audit pass routine |
| `security-guidance` | DEFER | Audit needed before daily-driver decision |
| `pyright-lsp` | DEFER | LSP integration; cost-vs-value review |
| `feature-dev` | DEFER | Audit needed |
| `code-review` | DEFER | Audit needed |
| `vercel` | DEFER | Three install versions retained; cleanup + audit |
| `ralph-loop` | DEFER | Audit needed |
| `frontend-design` | DEFER | Audit needed |
| `typescript-lsp` | DEFER (currently disabled) | Stays disabled unless specific use case |
| `sentry` | DEFER (currently disabled) | Stays disabled unless specific use case |

## Rejected candidates summary

- `affaan-m/everything-claude-code` — duplicates the harness's own foundation reasoning. Adopting would create a maintenance vector for material the harness owns.
- `disler/claude-code-hooks-mastery` — broader hook collection would introduce hooks for threats Phase 2 explicitly skipped, weakening the calibrated-minimum posture.
- `detect-secrets` — superseded by gitleaks (stronger coverage on the same fixture and already installed). Pre-commit rewire is post-Phase-5.

## Notes on the methodology

The 30-second target is real. Pre-filter is triage, not a deep dive. The result column is binary by intent (survive / reject) plus DEFER for candidates where the integration cost or signal is not yet clear; defer carries a tracked next-evaluation trigger in `mac/evaluations/deep-eval.md`.

Rubric scoring on a 1-to-5 scale is rejected by design. The result column is qualitative, the rationale is qualitative, the deep-eval is the empirical evidence.

The post-launch revision cadence is the appeal mechanism for rejected candidates. A seed rejected here at the pre-filter is not rejected forever. Signals change, and the methodology produces the current decision, not a final verdict.
