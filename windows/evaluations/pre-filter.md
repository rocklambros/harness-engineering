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
| `obra/superpowers` | MIT | integrate 5.1.0 (Phase 4 wholesale) | `<TBD-JETSON>` | Mac integrated; pure markdown, trivially portable, verify any executable bodies | active (lastUpdated 2026-05-05) | `<TBD>` | Mac confirmed pure markdown configuration; Windows port reads 14 skill bodies for non-portable commands |
| `affaan-m/everything-claude-code` | `<TBD-PHASE-1>` | reject (Phase 4 paper) | `<TBD-JETSON>` | Mac rejected; revisit only if a specific skill closes a Windows gap | `<TBD>` | reject (carry Mac rationale) | Configuration reference; Mac's foundation/ + ARCHITECTURE.md cover the equivalent ground |
| `disler/claude-code-hooks-mastery` | `<TBD-PHASE-1>` | reject (Phase 4 paper) | `<TBD-JETSON>` | Mac rejected; native PowerShell port or WSL2 routing required if Phase 3 surfaces a gap | `<TBD>` | reject (carry Mac rationale) | Mac's 6 Python hooks cover Phase 2 elected threats; Windows port may revisit |
| `anthropics/claude-code` skills and plugins | Anthropic | integrate (Phase 4 plugins) | `<TBD-JETSON>` | Mac integrated superpowers + mempalace plugins; verify Windows feature parity | active | `<TBD-PHASE-3>` | First-party; verify Windows build matches Mac feature set |

### Security tools

| Candidate | License | Mac | Jetson | Windows | Maintainership | Result | Rationale |
|---|---|---|---|---|---|---|---|
| `semgrep` | LGPL (Pro: BSL) | integrate 1.162.0 (Phase 3 + pipx install 2026-05-11) | `<TBD-JETSON>` | Mac integrated via pipx; native Windows support added in recent versions, verify installed version + transitive-dep wheels | active | `<TBD-PHASE-3>` | Mac pipx-installed 1.162.0 alongside broken Anaconda install; Windows older versions required WSL |
| `gitleaks` | MIT | integrate 8.30.0 (Phase 3, pre-commit wired 2026-05-11) | `<TBD-JETSON>` | Mac integrated; Go binary, Windows release builds available, verify exact version | `<TBD-PHASE-1>` | `<TBD-PHASE-3>` | Mac validated 440ms clean scan + correct AWS-example-key allowlist |
| `trivy` | Apache-2.0 | integrate 0.69.0 (Phase 3, complements gitleaks) | `<TBD-JETSON>` | Mac integrated; Go binary, Windows release builds available, verify exact version | `<TBD-PHASE-1>` | `<TBD-PHASE-3>` | Mac confirmed 5 secrets detected on realistic fixture |
| `syft` | Apache-2.0 | deferred post-launch | `<TBD-JETSON>` | Mac deferred; Go binary, Windows release expected, verify exact version | `<TBD-PHASE-1>` | `<TBD-PHASE-3>` | Go binary; SBOM generator; QC.1 PS.2.1 candidate |
| `grype` | Apache-2.0 | not deep-evaluated | `<TBD-JETSON>` | Go binary, Windows release expected; verify if Phase 3 surfaces a Mac-untested gap | `<TBD-PHASE-1>` | `<TBD-PHASE-3>` | Go binary; vulnerability scanner |
| `cyclonedx-cli` | Apache-2.0 | not deep-evaluated | `<TBD-JETSON>` | Verify Windows build; not in Mac's Phase 3 candidate set | `<TBD-PHASE-1>` | `<TBD-PHASE-3>` | SBOM tooling; revisit alongside syft adoption |
| `sigstore/cosign` | Apache-2.0 | not deep-evaluated | `<TBD-JETSON>` | Go binary, Windows release available; verify exact version | `<TBD-PHASE-1>` | `<TBD-PHASE-3>` | Go binary; not in Mac's Phase 3 candidate set |
| `osv-scanner` | Apache-2.0 | not deep-evaluated | `<TBD-JETSON>` | Go binary, Windows release available; verify exact version | `<TBD-PHASE-1>` | `<TBD-PHASE-3>` | Go binary; not in Mac's Phase 3 candidate set |
| `detect-secrets` | Apache-2.0 | reject (Phase 3, superseded by gitleaks) | yes (Python) | Mac rejected in favor of gitleaks; the supersession reasoning is platform-agnostic | active | reject | Mac removed from pre-commit 2026-05-11; gitleaks covers the use case with stronger git-history awareness |

### Specialized integrations

| Candidate | License | Mac | Jetson | Windows | Maintainership | Result | Rationale |
|---|---|---|---|---|---|---|---|
| `cosai-oasis/project-codeguard` | `<TBD-PHASE-1>` | defer (Phase 3, pre-1.0 paper eval) | `<TBD-JETSON>` | Mac deferred; verify Windows installer when 1.0 ships | pre-1.0 | `<TBD-PHASE-4>` | Mac integration shape supports future swap; agentcontrolstandard.ai is a same-class candidate per `phase-outputs/PHASE-3-NOTES.md` |
| MemPalace | `<TBD-PHASE-1>` | integrate 3.3.2 (Phase 4) | `<TBD-JETSON>` | Mac integrated via Python on Anaconda; verify Windows native vs WSL2 placement (per Phase 2) + Windows Scheduled Task equivalent for daily maintenance | `<TBD-PHASE-1>` | `<TBD-PHASE-4>` | Mac confirmed all 39 mempalace_* MCP tools working; known add_drawer content-corruption bug has deterministic workaround |
| Serena | `<TBD-PHASE-1>` | defer (Phase 4, user-disabled signal) | `<TBD-JETSON>` | Mac deferred respecting user-disabled signal; Windows LSP integration unverified | `<TBD-PHASE-1>` | `<TBD-PHASE-4>` | Mac's built-in Grep/Glob/Read cover common navigation; revisit on specific use case |

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
