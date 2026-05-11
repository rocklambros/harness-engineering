# scripts/ (Windows)

Windows-platform-specific scripts that come out of the build. Empty at scaffold time. Populated by Phase 3 (where deterministic-layer helpers need a script) and Phase 5 (where final wiring produces helpers).

The root `scripts/drift-check.sh` handles cached-prefix discipline across the whole repo through `*/CLAUDE.md` and `*/harness/CLAUDE.md` globs. The script runs via bash, which on Windows requires Git Bash, WSL2, or a similar bash environment. Phase 0 records the bash path for any Windows-side pre-commit invocations.

Windows-specific scripts that land here address platform-specific operational concerns: settings.json schema validation against the Claude Code Windows version pin, hook script execution-policy verification, MCP server reachability checks on the Windows network stack, PowerShell vs WSL2 hook routing verification, and similar.

Each script in this directory carries a header block with: purpose, threat or QC property addressed, verification test, and language-appropriate linter cleanliness (PSScriptAnalyzer for PowerShell, shellcheck for bash, language-appropriate SAST for Python).

`<NEEDS-WINDOWS-PORT-VALIDATION>` for any script ported from Mac or Jetson: the script runs in the expected execution context (native PowerShell, WSL2 bash, or cross-context with explicit routing).

Phase 5 audits this directory against the Quality Contract.
