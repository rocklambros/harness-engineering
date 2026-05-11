# Architectural Principles

The architecture of this harness rests on four principles. Each one is a constraint on how decisions get made for the lifetime of the project. They sit above any specific tool choice, any specific seed repo, and any specific platform. When a Phase 2 architecture interview decision conflicts with one of these principles, the principle wins.

## Principle 1: Hooks enforce, CLAUDE.md advises

This is the load-bearing decision in the harness. Every other architectural choice depends on it being clear.

Claude Code hooks are deterministic. The runtime fires them at defined lifecycle events, the handler returns a decision, the runtime acts on the decision. The model has no veto. The 27 hook events defined in Claude Code v2.1.88 (15 with rich output schemas) give the harness a place to enforce any rule that must hold every time.

CLAUDE.md is advisory. The model reads the file, incorporates the content into context, and follows the instructions probabilistically. The model's compliance with CLAUDE.md is a function of prompt design, model version, context window pressure, and conversation length. None of those are stable over time.

The practical rule: any property the harness must hold goes in a hook. Anything that is preference, taste, style, or guidance goes in CLAUDE.md. When a phase produces both kinds of content, the Reviewer subagent in Phase 5 checks that the right rule landed in the right layer.

The cost of putting an enforcement rule in CLAUDE.md only: eventual silent failure. The cost of putting a preference in a hook: brittle behavior on edge cases, false-positive friction. Both costs are real. The asymmetry is that the first cost compounds and the second is loud.

## Principle 2: Least privilege by default, expand by approving

The Claude Code permission system implements deny-first, ask-by-default evaluation. The harness extends that posture into the tools and MCP servers it exposes. The starting permission set for every new component is the minimum that lets the component do its declared job. Permission widening happens through explicit decision, recorded.

This rules out two common patterns. First: starting with `--dangerously-skip-permissions` and adding deny rules to taste. The 0.4% false-positive rate of the auto-mode classifier costs less than the threat surface that bypass mode opens up. Second: registering an MCP server with the full tool surface enabled and assuming the deny rules will catch problems. MCP server-level rules (`mcp__server` pattern) strip whole tool families from the model's view before invocation, and the harness uses them as the default position. Specific tools get re-enabled by name when a phase justifies the need.

The seven permission modes (plan, default, acceptEdits, auto, dontAsk, bypassPermissions, bubble) form a spectrum. The harness's default mode is documented per platform in the platform `ARCHITECTURE.md`. Mode changes are deliberate.

## Principle 3: Reversibility-weighted risk

Tool invocations differ in how easily they can be undone. Reading a file: trivially reversible. Writing to a file inside the working directory: reversible from version control. Writing outside the working directory: not reversible without filesystem backup. Network calls with side effects (POST to an API that mutates state): not reversible. `git push`: not reversible. `rm -rf` against a path outside the working directory: not reversible.

The harness weights risk by reversibility, not by tool name. Hook scripts and deny rules raise the friction proportionally. A read against any path inside the working directory is auto-approved. A write to a path outside the working directory triggers a hook that requires explicit confirmation. A `git push` is gated behind a SkillTool that runs the test suite first.

The principle comes from Anthropic's documented design (reversibility-weighted risk assessment is one of the 13 principles Liu et al. derive from the source code). Implementing it consistently across three machines is what makes the harness portable.

## Principle 4: Stress every component against the current model

Every harness component encodes an assumption about model behavior. A skill description encodes an assumption about how the model will route. A hook denial reason encodes an assumption about how the model will recover. A deny rule encodes an assumption about how the model will phrase a tool call. Assumptions go stale across model generations.

The discipline: any component added in Phase 3 or Phase 4 gets exercised against the current model in the same phase. "Wire it up, see what happens, document the surprise" is the loop. The architecture analysis cites Rajasekaran's harness retrospective: context resets that were necessary on Opus 4.5 became unnecessary on 4.6, and a harness that did not re-test the assumption was over-engineered for the new model.

QC.5 (versioning posture) is the policy expression of this principle. The principle itself is broader: every decision in this harness is provisional against the current model and gets re-validated on major version changes.

---

## The harness anatomy (nine components)

The architecture analysis decomposes a Claude Code harness into nine components. They are not optional; every harness has all nine, configured deliberately or by default. The repo's job is to make every choice deliberate.

1. **Agent loop**: The runtime that interleaves model calls and tool executions. Owned by Claude Code itself. The harness configures the agent loop through model selection, effort level, and session mode.
2. **Instruction layer**: Project CLAUDE.md, harness CLAUDE.md, skill bodies. Advisory text. Composed in the cached prefix. Subject to QC.4b context discipline.
3. **Tool pool**: Built-in tools, custom tools, MCP-exposed tools. Assembled by the runtime at session start. Filtered by deny rules and mode.
4. **Permission layer**: Permission modes, deny rules, allow rules, hook-based gates. Deterministic. Owned by the harness's `permissions` config and hook scripts.
5. **Context pipeline**: Compaction, system reminders, context resets, file references. Influenced by harness design through what goes in vs. out of the cached prefix.
6. **Sandbox**: Filesystem and network isolation for Bash and PowerShell commands. Configured per platform. Independent of the permission layer.
7. **MCP integration**: External tool surfaces. Each MCP server is a permission grant. Allowlisting, network egress controls, and per-server tool filtering live here.
8. **Subagent delegation**: The Task tool and its worktree isolation. Subagent model selection affects both inference cost and cache economy (QC.4a).
9. **Persistence**: The session log, conversation history, memory tools. The session is the only durable component in the Claude Code execution model; the harness and sandbox are explicitly disposable.

Every phase of the build addresses one or more of these components. Phase 2 (architecture interview) explicitly maps which components get which treatment. The components are the vocabulary the harness uses to describe itself.

## How the principles land in the build

The four principles produce a set of concrete checks the Reviewer subagent uses in Phase 5:

- Does every rule that must hold every time live in a hook?
- Does every component start from the minimum permission set?
- Does the friction on each tool match its reversibility class?
- Has every component added in this phase been exercised against the current Claude Code version?

Failure on any check is a finding, not a blocker. The phase output records the finding and the decision (fix now, accept residual risk, defer to a later revision). The principles are honest constraints, not slogans.
