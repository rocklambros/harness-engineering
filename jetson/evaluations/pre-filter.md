# Pre-filter worksheet (Jetson)

Records the 30-second triage decisions per seed candidate for Jetson AGX Orin (ARM64 Linux). The methodology is in `foundation/03-seed-evaluation-methodology.md`. This file is the operational log for the Jetson build.

Pre-filter asks three questions per candidate. Any "no" rejects. Survivors move to `deep-eval.md`.

1. **License**: Compatible with this repo's MIT and with the candidate's intended use here?
2. **Architecture support**: Works on ARM64 Linux specifically? Many tools claim "Linux" support but lack ARM64 builds. This column requires positive verification, not inference from Mac availability.
3. **Maintainership**: Commit in the last 90 days, issue tracker shows real responses?

Each row is one candidate. Rationale fits in one sentence when rejected. Survivors carry forward to deep evaluation in Phase 3 or Phase 4.

## Format

| Candidate | License | Mac | Jetson (ARM64 Linux) | Windows | Maintainership | Result | Rationale |
|---|---|---|---|---|---|---|---|
| `<candidate>` | `<TBD>` | `<TBD>` | `<TBD-JETSON-PORT-VALIDATION>` | `<TBD>` | `<TBD>` | survive / reject | `<one sentence>` |

## Seeds carried forward from Mac

The candidates Mac pre-filter survived are pre-populated here with ARM64 Linux availability set to `<NEEDS-JETSON-PORT-VALIDATION>`. The Jetson Phase 1 discovery scan resolves the marker.

### Configuration repositories and skill libraries

| Candidate | License | Mac | Jetson | Windows | Maintainership | Result | Rationale |
|---|---|---|---|---|---|---|---|
| `obra/superpowers` | `<TBD-PHASE-1>` | `<TBD-MAC>` | `<NEEDS-JETSON-PORT-VALIDATION>` | `<TBD>` | `<TBD>` | `<TBD>` | Pure markdown configuration likely portable; verify any executable bodies |
| `affaan-m/everything-claude-code` | `<TBD-PHASE-1>` | `<TBD-MAC>` | `<NEEDS-JETSON-PORT-VALIDATION>` | `<TBD>` | `<TBD>` | `<TBD>` | Configuration reference; verify executable hook scripts |
| `disler/claude-code-hooks-mastery` | `<TBD-PHASE-1>` | `<TBD-MAC>` | `<NEEDS-JETSON-PORT-VALIDATION>` | `<TBD>` | `<TBD>` | `<TBD>` | Hook scripts use shell; verify GNU vs BSD coreutils compatibility |
| `anthropics/claude-code` skills and plugins | Anthropic | yes | `<NEEDS-JETSON-PORT-VALIDATION>` | `<TBD>` | active | `<TBD-PHASE-3>` | First-party; verify ARM64 Linux build matches Mac feature set |

### Security tools

| Candidate | License | Mac | Jetson | Windows | Maintainership | Result | Rationale |
|---|---|---|---|---|---|---|---|
| `semgrep` | LGPL (Pro: BSL) | yes | `<NEEDS-JETSON-PORT-VALIDATION>` | yes | active | `<TBD-PHASE-3>` | Python; usually ARM64 Linux compatible. Verify the installed version. |
| `gitleaks` | MIT | yes | `<NEEDS-JETSON-PORT-VALIDATION>` | yes | `<TBD-PHASE-1>` | `<TBD-PHASE-3>` | Go binary; ARM64 Linux builds available in releases |
| `trivy` | Apache-2.0 | yes | `<NEEDS-JETSON-PORT-VALIDATION>` | yes | `<TBD-PHASE-1>` | `<TBD-PHASE-3>` | Go binary; ARM64 Linux builds available |
| `syft` | Apache-2.0 | yes | `<NEEDS-JETSON-PORT-VALIDATION>` | yes | `<TBD-PHASE-1>` | `<TBD-PHASE-3>` | Go binary; SBOM generator; QC.1 PS.2.1 candidate |
| `grype` | Apache-2.0 | yes | `<NEEDS-JETSON-PORT-VALIDATION>` | yes | `<TBD-PHASE-1>` | `<TBD-PHASE-3>` | Go binary; vulnerability scanner |
| `cyclonedx-cli` | Apache-2.0 | yes | `<NEEDS-JETSON-PORT-VALIDATION>` | yes | `<TBD-PHASE-1>` | `<TBD-PHASE-3>` | `<TBD>` |
| `sigstore/cosign` | Apache-2.0 | yes | `<NEEDS-JETSON-PORT-VALIDATION>` | yes | `<TBD-PHASE-1>` | `<TBD-PHASE-3>` | Go binary; ARM64 Linux builds available |
| `osv-scanner` | Apache-2.0 | yes | `<NEEDS-JETSON-PORT-VALIDATION>` | yes | `<TBD-PHASE-1>` | `<TBD-PHASE-3>` | Go binary; ARM64 Linux builds available |
| `detect-secrets` | Apache-2.0 | yes | yes (Python) | yes | active | survive | Python; pure Python, ARM64 Linux compatible. Wired in pre-commit. |

### Specialized integrations

| Candidate | License | Mac | Jetson | Windows | Maintainership | Result | Rationale |
|---|---|---|---|---|---|---|---|
| `cosai-oasis/project-codeguard` | `<TBD-PHASE-1>` | `<TBD>` | `<NEEDS-JETSON-PORT-VALIDATION>` | `<TBD>` | pre-1.0 | `<TBD-PHASE-4>` | Pre-1.0; Jetson availability depends on installer story |
| MemPalace | `<TBD-PHASE-1>` | yes (installed) | `<NEEDS-JETSON-PORT-VALIDATION>` | `<TBD>` | `<TBD-PHASE-1>` | `<TBD-PHASE-4>` | Verify ARM64 Linux build and runtime dependencies |
| Serena | `<TBD-PHASE-1>` | yes (installed) | `<NEEDS-JETSON-PORT-VALIDATION>` | `<TBD>` | `<TBD-PHASE-1>` | `<TBD-PHASE-4>` | LSP integration; verify language server ARM64 Linux support |

## Rejected candidates

Each rejection lands here with the one-sentence rationale. Examples of what gets rejected on Jetson specifically:

- Tools with x86-only binaries (no ARM64 Linux build, no source-available alternative).
- Tools depending on macOS-specific libraries (e.g., LaunchAgents, Cocoa frameworks).
- MCP servers maintained by vendors who do not ship ARM64 Linux binaries and refuse to provide source.

Phase 1 and Phase 3 add rejected entries here as they encounter them.

## Notes on the methodology

The 30-second target holds on Jetson. Architecture-support verification on ARM64 Linux is occasionally a few minutes extra (downloading a release archive to inspect) but still fits the pre-filter budget for the candidates evaluated here.

Rubric scoring is not allowed. The result column is binary: survive or reject. The rationale is qualitative.

The post-launch revision cadence is the appeal mechanism. A seed rejected at pre-filter is not rejected forever. ARM64 Linux support sometimes lands in subsequent releases; a re-evaluation trigger fires when the upstream announces.
