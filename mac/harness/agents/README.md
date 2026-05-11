# agents/

Subagent definitions for Claude Code. Each agent specification configures a Task tool invocation: model selection, effort level, allowed tools, worktree isolation, and the description that the parent uses to decide when to spawn the subagent.

Agents live here so Phase 4 (extension layer) can write them as discrete files with rationale, and the Reviewer subagent in Phase 5 audits them against the Quality Contract before wiring.

## Naming convention

`agents/<agent-name>.md`. Kebab-case. The name appears in the parent agent's tool selection logic; descriptive durable names beat clever ones.

Inside each file: the agent's role, the model and effort defaults, the allowed-tools list, the when-to-spawn guidance (per Opus 4.7-specific instruction discipline), and the verification criteria that the parent uses to judge the subagent's output.

## Security posture

Subagent delegation is a permission inheritance question. By default a subagent inherits the parent's permission posture, with worktree isolation as a sandboxing layer per Claude_Architecture.md §8. The harness's agents narrow rather than widen: each `<agent-name>.md` lists the tools the agent is allowed to use, not the tools it is forbidden from.

Same-family parent and subagent (Opus parent, Opus subagent) share cache. Cross-family (Opus parent, Haiku subagent) does not. Subagent model selection is therefore a QC.4a concern in addition to a capability concern.

## Phase coverage

Phase 4 populates this directory. The Reviewer subagent itself is defined here as `agents/reviewer.md` and is loaded by Phase 5 to audit Phase 5's own output. Phase 5 produces the polished final form of every agent file.
