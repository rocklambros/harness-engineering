# Stage 1 Pre-Filter Evaluations (Windows)

Windows-specific pre-filter results. The Architecture gate differs from Mac and Jetson: tools must work either natively on Windows or inside WSL2.

Most tools that pass on Mac and Jetson pass on Windows through WSL2 (Semgrep, gitleaks, shellcheck, jq all run in WSL2 Ubuntu without modification).

The Windows-specific consideration is whether a tool requires native Windows execution. Tools that need native Windows access to APIs or filesystem hooks unavailable in WSL2 get flagged here.

See `foundation/03-seed-evaluation-methodology.md`. Reference: `mac/evaluations/pre-filter.md`.

Phase 2 produces the Windows-specific entries here.
