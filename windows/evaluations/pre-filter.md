# Pre-filter worksheet (Windows)

Records the 30-second triage decisions per seed candidate for Windows 11 x86_64. The methodology is in `foundation/03-seed-evaluation-methodology.md`. This file is the operational log for the Windows build.

Pre-filter asks three questions per candidate. Any "no" rejects. Survivors move to `deep-eval.md`.

1. **License**: Compatible with this repo's MIT and with the candidate's intended use here?
2. **Architecture support**: Works on Windows x86_64 specifically? Native Windows is the preferred target; WSL2 fallback is documented per candidate when adopted. This column requires positive verification, not inference from Mac or Linux availability.
3. **Maintainership**: Commit in the last 90 days, issue tracker shows real responses?

Each row is one candidate. Rationale fits in one sentence when rejected. Survivors carry forward to deep evaluation in Phase 3 or Phase 4.

## Format

| Candidate | License | Mac | Jetson | Windows (native or WSL2) | Maintainership | Result | Rationale |
|---|---|---|---|---|---|---|---|
| `<candidate>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD-WINDOWS-PORT-VALIDATION>` | `<TBD>` | survive / reject | `<one sentence>` |

## Seeds carried forward from Mac

The candidates Mac pre-filter survived are pre-populated here with Windows availability set to `<NEEDS-WINDOWS-PORT-VALIDATION>`. The Windows Phase 1 discovery scan resolves the marker.

### Configuration repositories and skill libraries

| Candidate | License | Mac | Jetson | Windows | Maintainership | Result | Rationale |
|---|---|---|---|---|---|---|---|
| `obra/superpowers` | `<TBD-PHASE-1>` | `<TBD-MAC>` | `<TBD-JETSON>` | `<NEEDS-WINDOWS-PORT-VALIDATION>` | `<TBD>` | `<TBD>` | Pure markdown configuration likely portable; verify any executable bodies |
| `affaan-m/everything-claude-code` | `<TBD-PHASE-1>` | `<TBD-MAC>` | `<TBD-JETSON>` | `<NEEDS-WINDOWS-PORT-VALIDATION>` | `<TBD>` | `<TBD>` | Configuration reference; verify executable hook scripts on PowerShell |
| `disler/claude-code-hooks-mastery` | `<TBD-PHASE-1>` | `<TBD-MAC>` | `<TBD-JETSON>` | `<NEEDS-WINDOWS-PORT-VALIDATION>` | `<TBD>` | `<TBD>` | Hook scripts likely bash; native PowerShell ports needed or WSL2 routing |
| `anthropics/claude-code` skills and plugins | Anthropic | yes | `<TBD-JETSON>` | `<NEEDS-WINDOWS-PORT-VALIDATION>` | active | `<TBD-PHASE-3>` | First-party; verify Windows build matches Mac feature set |

### Security tools

| Candidate | License | Mac | Jetson | Windows | Maintainership | Result | Rationale |
|---|---|---|---|---|---|---|---|
| `semgrep` | LGPL (Pro: BSL) | yes | `<TBD-JETSON>` | `<NEEDS-WINDOWS-PORT-VALIDATION>` | active | `<TBD-PHASE-3>` | Native Windows support recent; older versions required WSL. Verify installed version. |
| `gitleaks` | MIT | yes | `<TBD-JETSON>` | `<NEEDS-WINDOWS-PORT-VALIDATION>` | `<TBD-PHASE-1>` | `<TBD-PHASE-3>` | Go binary; Windows builds available in releases |
| `trivy` | Apache-2.0 | yes | `<TBD-JETSON>` | `<NEEDS-WINDOWS-PORT-VALIDATION>` | `<TBD-PHASE-1>` | `<TBD-PHASE-3>` | Go binary; Windows builds available |
| `syft` | Apache-2.0 | yes | `<TBD-JETSON>` | `<NEEDS-WINDOWS-PORT-VALIDATION>` | `<TBD-PHASE-1>` | `<TBD-PHASE-3>` | Go binary; SBOM generator |
| `grype` | Apache-2.0 | yes | `<TBD-JETSON>` | `<NEEDS-WINDOWS-PORT-VALIDATION>` | `<TBD-PHASE-1>` | `<TBD-PHASE-3>` | Go binary; vulnerability scanner |
| `cyclonedx-cli` | Apache-2.0 | yes | `<TBD-JETSON>` | `<NEEDS-WINDOWS-PORT-VALIDATION>` | `<TBD-PHASE-1>` | `<TBD-PHASE-3>` | `<TBD>` |
| `sigstore/cosign` | Apache-2.0 | yes | `<TBD-JETSON>` | `<NEEDS-WINDOWS-PORT-VALIDATION>` | `<TBD-PHASE-1>` | `<TBD-PHASE-3>` | Go binary; Windows builds available |
| `osv-scanner` | Apache-2.0 | yes | `<TBD-JETSON>` | `<NEEDS-WINDOWS-PORT-VALIDATION>` | `<TBD-PHASE-1>` | `<TBD-PHASE-3>` | Go binary; Windows builds available |
| `detect-secrets` | Apache-2.0 | yes | yes (Python) | yes (Python) | active | survive | Python; pure Python, Windows compatible via pip. Wired in pre-commit. |

### Specialized integrations

| Candidate | License | Mac | Jetson | Windows | Maintainership | Result | Rationale |
|---|---|---|---|---|---|---|---|
| `cosai-oasis/project-codeguard` | `<TBD-PHASE-1>` | `<TBD>` | `<TBD-JETSON>` | `<NEEDS-WINDOWS-PORT-VALIDATION>` | pre-1.0 | `<TBD-PHASE-4>` | Pre-1.0; Windows availability depends on installer story |
| MemPalace | `<TBD-PHASE-1>` | yes (installed) | `<TBD-JETSON>` | `<NEEDS-WINDOWS-PORT-VALIDATION>` | `<TBD-PHASE-1>` | `<TBD-PHASE-4>` | Verify Windows build and runtime dependencies |
| Serena | `<TBD-PHASE-1>` | yes (installed) | `<TBD-JETSON>` | `<NEEDS-WINDOWS-PORT-VALIDATION>` | `<TBD-PHASE-1>` | `<TBD-PHASE-4>` | LSP integration; verify language server Windows support |

## Rejected candidates

Each rejection lands here with the one-sentence rationale. Examples of what gets rejected on Windows specifically:

- Tools depending on POSIX-only system calls without a documented Windows fallback (no WSL2 path acceptable to the use case).
- Tools requiring kernel modules or system extensions Windows does not support.
- MCP servers maintained by vendors who do not ship Windows binaries and whose native dependencies do not build under MSVC or MinGW.

Phase 1 and Phase 3 add rejected entries here as they encounter them.

## Notes on the methodology

The 30-second target holds on Windows. Native vs WSL2 routing decisions occasionally take longer (downloading a release archive or running a test install), but this still fits the pre-filter budget for the candidates evaluated here.

Rubric scoring is not allowed. The result column is binary: survive or reject. The rationale is qualitative.

The post-launch revision cadence is the appeal mechanism. Windows-native support frequently lands in subsequent releases of cross-platform tools; a re-evaluation trigger fires when the upstream announces.
