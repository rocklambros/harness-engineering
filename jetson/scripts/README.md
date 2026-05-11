# scripts/ (Jetson)

Jetson-platform-specific scripts that come out of the build. Empty at scaffold time. Populated by Phase 3 (where deterministic-layer helpers need a script) and Phase 5 (where final wiring produces helpers).

The root `scripts/drift-check.sh` handles cached-prefix discipline across the whole repo through `*/CLAUDE.md` and `*/harness/CLAUDE.md` globs. Jetson-specific scripts that land here address platform-specific operational concerns the root script does not cover: settings.json schema validation against the Claude Code ARM64 Linux version pin, hook script executable-bit verification, MCP server reachability checks on the Jetson network, and similar.

Each script in this directory carries a header block with: purpose, threat or QC property addressed, verification test, and shellcheck-cleanliness.

`<NEEDS-JETSON-PORT-VALIDATION>` for any script ported from Mac: the script's commands work on GNU coreutils, not just BSD coreutils.

Phase 5 audits this directory against the Quality Contract.
