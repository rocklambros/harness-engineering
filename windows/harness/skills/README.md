# skills/ (Windows)

Claude Code skills on Windows. Same model as Mac and Jetson: each skill is a self-contained capability the model invokes through the SkillTool meta-tool.

Skills live here so Phase 4 (extension layer) can write them in their final shape, the Reviewer subagent in Phase 5 audits them, and the wiring into `windows/harness/settings.json` is mechanical.

## Naming convention

Each skill is a directory: `skills/<skill-name>/`. Inside: `SKILL.md`, optional `scripts/`, optional `tests/`. Identical to Mac and Jetson.

## Security posture

A skill is a permission grant in two directions. Same posture as Mac and Jetson. Skills with executable bodies pass language-appropriate SAST in pre-commit per QC.1. Skills that register hooks dynamically declare the hook events in the SKILL.md front-matter.

`<NEEDS-WINDOWS-PORT-VALIDATION>` per skill: any skill ported from Mac or Jetson that ships executable bodies is verified to behave identically on Windows before adoption. Skills that depend on POSIX-specific commands (e.g., `chmod`, `chown`, `find` with `-perm`) require a Windows equivalent (typically PowerShell cmdlets or a WSL2 routing) or get rejected for this platform.

Skills that invoke shell commands choose one of three execution models: native PowerShell, native cmd, or WSL2 bash. The choice lives in the skill's front-matter and the Reviewer audits for consistency.

## Phase coverage

Phase 4 populates this directory. Pre-filter survivors from Phase 1 inventory and Phase 3 deep-eval get integrated by exercise in a sandboxed session. Phase 5 produces the polished final form.

Seeds adopted on Mac (`obra/superpowers`, `affaan-m/everything-claude-code`, `disler/claude-code-hooks-mastery`, official `anthropics/claude-code` skills/plugins) require Windows verification before adoption here. Each adopted skill records the verification outcome in `windows/evaluations/deep-eval.md`.
