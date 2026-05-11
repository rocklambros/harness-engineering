# Mac section

The validated build of the harness. macOS on Apple Silicon (ARM64). Claude Code running from `/Users/klambros/harness-engineering/`.

This section is fully written: Phase 0 through Phase 5 prompts, the harness skeleton, the operational `CLAUDE.md`, the architecture document, the seed evaluation worksheets. The Jetson and Windows sections mirror this structure, with Phase 3-5 scaffolded rather than executed.

## What's in here

`ARCHITECTURE.md` documents the Mac harness as it stands. It is a filled draft with `<TBD-PHASE-0>` blocks where Phase 0 records platform-specific version pins and configuration decisions. Read this first to understand what the harness does and what it does not do.

`prompts/` holds the seven phase prompts that Claude Code executes against this directory tree. They run in order: `01-pre-flight.md`, then `phase-0-goals.md`, then phases 1 through 5. Every prompt carries the standard header (effort, mode, thinking, context budget, parallel tool calls, scope) and explicit verification criteria. The prompts are contracts with the executing Claude Code session, not memos.

`harness/` holds the operational artifacts that Claude Code reads at runtime when working on day-to-day projects. `harness/CLAUDE.md` is the daily-driver instruction file (distinct from the build-time `CLAUDE.md` at the repo root). `harness/settings.json.template` is the Claude Code permission and hook configuration. Phase 3 fills `harness/rules/` and `harness/hooks/`; Phase 4 fills `harness/skills/` and `harness/agents/`.

`evaluations/` holds two worksheets that operationalize the seed evaluation methodology from `foundation/03-seed-evaluation-methodology.md`. `pre-filter.md` records 30-second triage decisions per candidate. `deep-eval.md` records integration outcomes for survivors.

`scripts/` is reserved for Mac-platform-specific scripts that come out of Phase 3 or Phase 5. The root `scripts/drift-check.sh` already enforces cached-prefix discipline across the whole repo; Mac-specific operational scripts land here when the build produces them.

## How to use this section

If you are reading this repo as a reference for building your own harness, the path is:

1. Read `foundation/` first. The Quality Contract, threat model, architectural principles, and seed evaluation methodology are the load-bearing thinking.
2. Read this section's `ARCHITECTURE.md` to see how the foundation lands on a specific platform.
3. Read the seven prompts in `prompts/` in order to see the build sequence.
4. Read `harness/CLAUDE.md` and `harness/settings.json.template` to see the runtime artifacts the prompts produce.

If you are running these prompts against your own machine, do not. The prompts are calibrated for a specific environment, a specific tool inventory, and a specific threat model. Run your own Phase 0 against your own environment, then derive your own Phase 1 inventory and Phase 2 architecture decisions from there. The prompts in this directory are reference, not template.

## Status

Built and validated against macOS on Apple Silicon. The first build sequence ran end of May 2026. Subsequent revisions land continuously, each in its own commit with rationale per the project commit template.

The `<TBD-PHASE-0>` blocks in `ARCHITECTURE.md` reflect the build sequence: every block is filled after the first Phase 0 session, then re-evaluated on Claude Code minor-version bumps per QC.5.
