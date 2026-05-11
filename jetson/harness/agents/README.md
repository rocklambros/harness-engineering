# agents/ (Jetson)

Subagent definitions for Claude Code on Jetson. Each agent specification configures a Task tool invocation: model selection, effort level, allowed tools, worktree isolation, when-to-spawn guidance.

Agents live here so Phase 4 (extension layer) can write them as discrete files with rationale, and the Reviewer subagent in Phase 5 audits them before wiring.

## Naming convention

`agents/<agent-name>.md`. Kebab-case. Same as Mac.

Inside each file: role, model and effort defaults, allowed-tools list, when-to-spawn guidance per the Opus 4.7 instruction discipline, verification criteria.

## Security posture

Subagent delegation is a permission inheritance question. Same posture as Mac. Worktree isolation provides the sandboxing layer per Claude_Architecture.md §8.

Same-family parent and subagent share cache (Opus+Opus). Cross-family (Opus+Haiku) does not. Subagent model selection is a QC.4a concern in addition to a capability concern.

## Phase coverage

Phase 4 populates this directory. The Reviewer subagent is defined here as `agents/reviewer.md` and is loaded by Phase 5 to audit Phase 5's own output. Phase 5 produces the polished final form.

`<NEEDS-JETSON-PORT-VALIDATION>` per agent: agent definitions ported from Mac are verified to function identically on Jetson before adoption. Most agent definitions are platform-agnostic, but any agent that invokes Mac-specific tools or paths requires adaptation.
