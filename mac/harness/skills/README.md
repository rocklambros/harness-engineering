# skills/

Claude Code skills. Each skill is a self-contained capability the model can invoke through the SkillTool meta-tool: a name, a description that drives discovery, an instruction body, and optional allowed-tools, hook registrations, and execution context per Claude_Architecture.md §6.1.

Skills live here so Phase 4 (extension layer) can write them in their final shape, the Reviewer subagent in Phase 5 audits them against the Quality Contract, and the wiring into `mac/harness/settings.json` is mechanical.

## Naming convention

Each skill is a directory: `skills/<skill-name>/`. Inside the directory: `SKILL.md` (front-matter and body), `scripts/` (if the skill ships executable bodies), and `tests/` (verification fixtures).

The skill name is kebab-case, descriptive, and durable. Skill names appear in cached prefixes through the discovery flow; renaming a skill costs cache hits across every project that uses it.

## Security posture

A skill is a permission grant in two directions. The model gains access to whatever the skill describes (via the `allowedTools` front-matter field). The skill gains access to whatever the model decides to do with it. Both directions get reviewed before the skill ships.

Skills with executable bodies pass language-appropriate SAST in pre-commit per QC.1 (PW.5.1, PW.8.2). Skills that register hooks dynamically (via the SkillTool injection path per Claude_Architecture.md §6.1) declare the hooks in the SKILL.md front-matter so the audit trail is in version control.

## Phase coverage

Phase 4 populates this directory. Pre-filter survivors from Phase 1 and Phase 3 inventory get deep-evaluated by integration in a sandboxed session. Phase 5 produces the polished final form. Seeds adopted from `obra/superpowers`, `affaan-m/everything-claude-code`, `disler/claude-code-hooks-mastery`, and the official `anthropics/claude-code` skills land here with their rationale recorded in commit messages and in `mac/evaluations/deep-eval.md`.
