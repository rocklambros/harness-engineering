# Agents

Subagent definitions for tasks that benefit from delegation. Agents are advisory: they are still model-driven, just with a constrained scope and focused context. Per AP.1, agents complement rather than replace the deterministic enforcement in hooks.

## Agents in this directory

`security-reviewer.md` is the deep security analysis subagent. Invoked explicitly when the main session requests a security review of a code change. Operates in plan mode (read-only). Produces a structured findings report keyed to CWE and severity.

`writer-reviewer.md` is the two-agent documentation pattern used by Phase 5. One agent writes, the other reviews against the Quality Contract. Iterates until the reviewer signs off or three iterations have elapsed.

## When to use a subagent vs. the main session

A subagent makes sense when:

The task benefits from a fresh context window unburdened by the main session's prior work.

The task is read-heavy and the main session's context budget is constrained.

The task produces a structured output (a review report, a curated list) that the main session can consume without re-reading the inputs.

A subagent does not make sense when:

The task requires the main session's full context to be coherent.

The task is single-step and can be done inline.

The cost of subagent setup exceeds the cost of doing the task directly.

## Adding new agents

New agent files land in this directory as Markdown with YAML frontmatter declaring the agent name and role.

Each agent specifies its scope (read-only vs. write-capable), its expected inputs, and its expected output format.

Agent definitions are advisory; the main session still decides when to delegate.

## Status

Phase 4 deliverable. Agent files are produced during Phase 4 execution. Initial scaffolding pending hardware-validated build.
