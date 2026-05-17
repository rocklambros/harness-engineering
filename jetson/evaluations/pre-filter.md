# Stage 1 Pre-Filter Evaluations (Jetson)

Jetson-specific pre-filter results. Run during Phase 2.

The pre-filter gates are License, Architecture support (aarch64 availability), and Maintainership. The Architecture gate is the gate that differs from Mac: tools that lack aarch64 builds fail this gate on Jetson and pass on Mac.

See `foundation/03-seed-evaluation-methodology.md` for the methodology.

## Reference: Mac pre-filter results

Read `mac/evaluations/pre-filter.md` first. Most candidates that passed pre-filter on Mac also pass on Jetson (Semgrep, gitleaks, shellcheck, jq all have aarch64 builds). The Jetson-specific evaluations focus on:

Tools that may not have prebuilt aarch64 binaries (e.g., some commercial SAST scanners).

Tools that have Tegra-specific compatibility considerations.

Phase 2 produces the Jetson-specific pre-filter entries here.
