# scripts/

Mac-platform-specific scripts that come out of the build. Empty in Batch 2. Populated by Phase 3 (where deterministic-layer helpers may need a script) and Phase 5 (where final wiring may produce helpers).

The root `scripts/drift-check.sh` already handles cached-prefix discipline across the whole repo through the `*/CLAUDE.md` and `*/harness/CLAUDE.md` globs. Mac-specific scripts that land here address platform-specific operational concerns the root script does not cover: settings.json schema validation against the Claude Code version pin, hook script executable-bit verification, MCP server reachability checks, and similar.

Each script in this directory carries a header block with the same elements required of hook scripts: purpose, threat or QC property addressed, verification test, and shellcheck cleanliness.

Phase 5 audits this directory against the Quality Contract and produces the polished final state.
