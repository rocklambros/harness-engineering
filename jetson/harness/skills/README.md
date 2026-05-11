# skills/ (Jetson)

Claude Code skills on Jetson. Same model as Mac: each skill is a self-contained capability the model invokes through the SkillTool meta-tool.

Skills live here so Phase 4 (extension layer) can write them in their final shape, the Reviewer subagent in Phase 5 audits them against the Quality Contract, and the wiring into `jetson/harness/settings.json` is mechanical.

## Naming convention

Each skill is a directory: `skills/<skill-name>/`. Inside: `SKILL.md`, optional `scripts/`, optional `tests/`. Identical to Mac.

## Security posture

A skill is a permission grant in two directions. Same posture as Mac. Skills with executable bodies pass language-appropriate SAST in pre-commit per QC.1. Skills that register hooks dynamically declare the hook events in the SKILL.md front-matter.

`<NEEDS-JETSON-PORT-VALIDATION>` per skill: any skill ported from Mac that ships executable bodies is verified to behave identically on ARM64 Linux before adoption. Skills that depend on macOS-specific commands (e.g., `pbcopy`, `osascript`, `launchctl`) require a Linux equivalent or get rejected for this platform.

## Phase coverage

Phase 4 populates this directory. Pre-filter survivors from Phase 1 inventory and Phase 3 deep-eval get integrated by exercise in a sandboxed session. Phase 5 produces the polished final form.

Seeds adopted on Mac (`obra/superpowers`, `affaan-m/everything-claude-code`, `disler/claude-code-hooks-mastery`, official `anthropics/claude-code` skills/plugins) require ARM64 Linux verification before adoption here. Each adopted skill records the verification outcome in `jetson/evaluations/deep-eval.md`.
