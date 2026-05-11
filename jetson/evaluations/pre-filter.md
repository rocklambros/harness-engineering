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
| `obra/superpowers` | MIT | integrate 5.1.0 (Phase 4 wholesale) | Mac integrated; pure markdown, trivially portable, verify any executable bodies | `<TBD>` | active (lastUpdated 2026-05-05) | `<TBD>` | Mac confirmed pure markdown configuration; ARM64 Linux port is reading 14 skill bodies for non-portable commands |
| `affaan-m/everything-claude-code` | `<TBD-PHASE-1>` | reject (Phase 4 paper) | Mac rejected; revisit only if a specific skill closes an ARM64 Linux gap | `<TBD>` | `<TBD>` | reject (carry Mac rationale) | Configuration reference; Mac's foundation/ + ARCHITECTURE.md cover the equivalent ground |
| `disler/claude-code-hooks-mastery` | `<TBD-PHASE-1>` | reject (Phase 4 paper) | Mac rejected; revisit if a specific hook fills a Phase 3 gap on Linux | `<TBD>` | `<TBD>` | reject (carry Mac rationale) | Mac's 6 Python hooks cover Phase 2 elected threats; ARM64 Linux port may revisit if GNU-specific patterns surface |
| `anthropics/claude-code` skills and plugins | Anthropic | integrate (Phase 4 plugins) | Mac integrated superpowers + mempalace plugins; verify ARM64 Linux feature parity | `<TBD>` | active | `<TBD-PHASE-3>` | First-party; verify ARM64 Linux build matches Mac feature set |

### Security tools

| Candidate | License | Mac | Jetson | Windows | Maintainership | Result | Rationale |
|---|---|---|---|---|---|---|---|
| `semgrep` | LGPL (Pro: BSL) | integrate 1.162.0 (Phase 3 + pipx install 2026-05-11) | Mac integrated via pipx (clean isolated venv); Python pure, verify ARM64 wheels for transitive deps | yes | active | `<TBD-PHASE-3>` | Mac pipx-installed 1.162.0 alongside broken Anaconda install; ARM64 Linux question is wheel availability for opentelemetry and friends |
| `gitleaks` | MIT | integrate 8.30.0 (Phase 3, pre-commit wired 2026-05-11) | Mac integrated; Go binary, ARM64 Linux release builds typical, verify exact version | yes | `<TBD-PHASE-1>` | `<TBD-PHASE-3>` | Mac validated 440ms clean scan + correct AWS-example-key allowlist; ARM64 Linux port verifies release tag |
| `trivy` | Apache-2.0 | integrate 0.69.0 (Phase 3, complements gitleaks) | Mac integrated; Go binary, ARM64 Linux release builds typical, verify exact version | yes | `<TBD-PHASE-1>` | `<TBD-PHASE-3>` | Mac confirmed 5 secrets detected on realistic fixture (broader than gitleaks); ARM64 Linux release expected |
| `syft` | Apache-2.0 | deferred post-launch | Mac deferred; Go binary, ARM64 Linux release expected, verify exact version | yes | `<TBD-PHASE-1>` | `<TBD-PHASE-3>` | Go binary; SBOM generator; QC.1 PS.2.1 candidate |
| `grype` | Apache-2.0 | not deep-evaluated | Go binary, ARM64 Linux release expected; verify if Phase 3 surfaces a Mac-untested gap | yes | `<TBD-PHASE-1>` | `<TBD-PHASE-3>` | Go binary; vulnerability scanner; not in Mac's Phase 3 candidate set |
| `cyclonedx-cli` | Apache-2.0 | not deep-evaluated | Verify ARM64 Linux build; not in Mac's Phase 3 candidate set | yes | `<TBD-PHASE-1>` | `<TBD-PHASE-3>` | SBOM tooling; revisit alongside syft adoption |
| `sigstore/cosign` | Apache-2.0 | not deep-evaluated | Go binary, ARM64 Linux release available; verify exact version | yes | `<TBD-PHASE-1>` | `<TBD-PHASE-3>` | Go binary; not in Mac's Phase 3 candidate set |
| `osv-scanner` | Apache-2.0 | not deep-evaluated | Go binary, ARM64 Linux release available; verify exact version | yes | `<TBD-PHASE-1>` | `<TBD-PHASE-3>` | Go binary; not in Mac's Phase 3 candidate set |
| `detect-secrets` | Apache-2.0 | reject (Phase 3, superseded by gitleaks) | Mac rejected in favor of gitleaks; the supersession reasoning is platform-agnostic | yes | active | reject | Mac removed from pre-commit 2026-05-11; gitleaks covers the use case with stronger git-history awareness |

### Specialized integrations

| Candidate | License | Mac | Jetson | Windows | Maintainership | Result | Rationale |
|---|---|---|---|---|---|---|---|
| `cosai-oasis/project-codeguard` | `<TBD-PHASE-1>` | defer (Phase 3, pre-1.0 paper eval) | Mac deferred; verify ARM64 Linux installer when 1.0 ships | `<TBD>` | pre-1.0 | `<TBD-PHASE-4>` | Mac integration shape (PreToolUse supply-chain hooks + deny rules) supports future swap; agentcontrolstandard.ai is a same-class candidate per `phase-outputs/PHASE-3-NOTES.md` |
| MemPalace | `<TBD-PHASE-1>` | integrate 3.3.2 (Phase 4) | Mac integrated via Python on Anaconda; verify ARM64 wheels for transitive deps + systemd-equivalent for daily maintenance | `<TBD>` | `<TBD-PHASE-1>` | `<TBD-PHASE-4>` | Mac confirmed all 39 mempalace_* MCP tools working; known add_drawer content-corruption bug has deterministic workaround |
| Serena | `<TBD-PHASE-1>` | defer (Phase 4, user-disabled signal) | Mac deferred respecting user-disabled signal; ARM64 Linux LSP integration unverified | `<TBD>` | `<TBD-PHASE-1>` | `<TBD-PHASE-4>` | Mac's built-in Grep/Glob/Read cover common navigation; revisit on specific use case |

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
