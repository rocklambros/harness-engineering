# Mac section

The validated build of the harness. macOS on Apple Silicon (ARM64). Claude Code running from `/Users/klambros/harness-engineering/`.

This section is fully written and validated. The seven prompts (pre-flight, Phase 0, Phases 1 through 5) ran end-to-end during the 2026-05-11 build sequence. The Jetson and Windows sections mirror this structure with Phase 3 through Phase 5 scaffolded rather than executed; see `jetson/README.md` and `windows/README.md` for per-platform scaffolding state.

## What's in here

`ARCHITECTURE.md` documents the Mac harness as it stands. Every section reflects the validated build: nine SAGE components, six hooks, six deny rules, two skills, two agents, two enabled plugins, the Quality Contract operationalization, and the version pins. Read this first to understand what the harness does and what it does not do.

`prompts/` holds the seven phase prompts that Claude Code executes against this directory tree. They run in order: `01-pre-flight.md`, then `phase-0-goals.md`, then phases 1 through 5. Every prompt carries the standard header (effort, mode, thinking, context budget, parallel tool calls, scope) and explicit verification criteria. The prompts are contracts with the executing Claude Code session, not memos.

`harness/` holds the operational artifacts that Claude Code reads at runtime when working on day-to-day projects:

- `harness/CLAUDE.md` (81 lines) — the daily-driver instruction file. Distinct from the build-time `CLAUDE.md` at the repo root.
- `harness/settings.json` — the populated Claude Code configuration: permission deny rules, hook event bindings, enabled plugins, model defaults, retention policy.
- `harness/settings.json.template` — the schema skeleton, unchanged from Batch 2 for reference.
- `harness/rules/` (6 markdown files) — Phase 3 deny rule documentation with patterns, threat citations, and tests.
- `harness/hooks/` (6 Python scripts) — Phase 3 hook scripts with header blocks, threat citations, and verification commands.
- `harness/skills/` (2 directories) — Phase 4 harness skills: `mcp-server-pre-trust-audit` and `seed-evaluation`.
- `harness/agents/` (2 markdown files) — Phase 4 subagent definitions: `reviewer` and `inventory`.

`evaluations/` holds two worksheets that operationalize the seed evaluation methodology from `foundation/03-seed-evaluation-methodology.md`. `pre-filter.md` records 30-second triage decisions per candidate. `deep-eval.md` records integration outcomes for survivors. Both populated through Phase 1 (pre-filter rows for installed candidates), Phase 3 (deterministic-layer security tool deep-eval), and Phase 4 (extension-layer seed deep-eval).

`scripts/` is reserved for Mac-platform-specific scripts that come out of operational work post-Phase-5 (e.g., the bulk-acknowledge tool for the 44 in-repo `.claude/` directories Phase 1 surveyed). The root `scripts/drift-check.sh` enforces cached-prefix discipline across the project hierarchy.

## How to use this section

If you are reading this repo as a reference for building your own harness, the path is:

1. Read `foundation/` first. The Quality Contract, threat model, architectural principles, and seed evaluation methodology are the load-bearing thinking.
2. Read this section's `ARCHITECTURE.md` to see how the foundation lands on a specific platform.
3. Read the seven prompts in `prompts/` in order to see the build sequence that produced the harness.
4. Read `harness/CLAUDE.md` and `harness/settings.json` to see the runtime artifacts the prompts produced.

If you are running these prompts against your own machine, do not. The prompts are calibrated for a specific environment, a specific tool inventory, and a specific threat model. Run your own Phase 0 against your own environment, then derive your own Phase 1 inventory and Phase 2 architecture decisions from there. The prompts in this directory are reference, not template.

## Status

Built and validated against macOS on Apple Silicon. First build sequence completed 2026-05-11 across pre-flight, Phase 0 (goals and architecture), and Phases 1 through 5 (discovery, interview, deterministic layer, extension layer, wire and document). Subsequent revisions land continuously, each in its own commit with rationale per the project commit template.

Post-Phase-5 operational steps (separate from the build commits): rebuild `~/.claude/` per Phase 2 Q3, bulk-acknowledge tool for the 44 in-repo `.claude/` directories, pre-commit wire from `detect-secrets` to `gitleaks`, `semgrep` clean install via pipx, widen `scripts/drift-check.sh` per Phase 2 Q10, Hetzner Cloud token env-var indirection, daily-driver plugin audit for the rebuilt config.
