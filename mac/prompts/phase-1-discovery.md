# Phase 1 — Discovery

<role>
You are discovering what is already on this Mac that the harness needs to know about: existing Claude Code configuration files, installed CLI tools, MCP server configurations in cloned repositories, pre-existing skills or hooks from prior experimentation, and any conflict between what Phase 0 recorded and what's on disk. Phase 1 produces an inventory and a conflicts list. You do not change anything. You read, you record, and you flag.

Discovery is read-only. The threat model in `foundation/01-threat-model.md` names the pre-trust initialization class (CVE-2025-59536). Phase 1 is structurally similar: you are looking at code that could otherwise execute at session start. The discipline here is to look at the files, not to load them into Claude Code through any configuration mechanism.
</role>

<effort>high</effort>

<mode>plan mode for the entire phase. Phase 1 writes only build-internal phase outputs; plan mode keeps the discovery surface honest.</mode>

<thinking>adaptive</thinking>

<context_budget>Run /context at start and end. Phase 1 reads many files. The inventory subagent absorbs most of the read cost; the main session synthesizes from the subagent's structured output. Record start, end, and delta in `phase-outputs/PHASE-1-CONTEXT.md`.</context_budget>

<parallel_tool_calls>
The inventory scan touches more than 20 files across the machine. Spawn a single inventory subagent for the scan rather than reading files serially in the main session. The subagent runs in plan mode with a focused tool allowlist (Read, Bash for `find` and version commands). Synthesis happens in the main session.

For specific cross-references after the subagent returns (e.g., reading the foundation documents to cross-check the inventory), prefer parallel reads.
</parallel_tool_calls>

<use_parallel_tool_calls>
The inventory scan benefits from parallel `find`, `ls`, and `cat` invocations against independent directories. Within the inventory subagent, use parallel tool calls for directory scans that do not depend on each other.
</use_parallel_tool_calls>

<scope>
Apply only to:
- `phase-outputs/PHASE-1-CONTEXT.md` (writes: context-budget record)
- `phase-outputs/INVENTORY.md` (writes: the inventory)
- `phase-outputs/CONFLICTS.md` (writes: any conflicts with Phase 0)
- `mac/evaluations/pre-filter.md` (updates: candidate rows where the discovery scan finds a candidate installed)

Do not modify any file in `foundation/`, `research/`, `mac/prompts/`, `mac/ARCHITECTURE.md`, `mac/harness/`, or `mac/scripts/`. Do not write hooks, skills, agents, or deny rules. Do not install or remove any tools. Do not edit existing `.claude/` directories anywhere on the machine.
</scope>

## What to do

Read `phase-outputs/PHASE-0-DECISIONS.md` and `mac/ARCHITECTURE.md` to understand what Phase 0 recorded. Then spawn the inventory subagent.

The inventory subagent's task is to record, without modifying:

1. **Claude Code configuration on this machine**: any `~/.claude/`, `~/.config/claude/`, or equivalent directories. The `settings.json`, `CLAUDE.md`, hooks, skills, agents, and MCP server configurations that already exist.
2. **In-repo Claude Code configurations**: every `.claude/` directory in cloned repositories under `~/code/`, `~/projects/`, `~/git/`, or wherever Rock keeps source. The pre-trust initialization audit habit (§4 of `foundation/01-threat-model.md`) starts here.
3. **Installed CLI tools relevant to the harness**: the tools the Phase 0 pre-flight verified, plus any related tools the harness candidates depend on (jq, yq, curl, gh, etc.).
4. **MCP server installations**: any MCP servers installed globally (npm global, pipx, Homebrew). Record what's installed but do not invoke any of them.
5. **Pre-existing skills, hooks, or agents from prior experimentation**: anything Rock built before this repo that the harness should know about (to either incorporate, replace, or explicitly retire).
6. **Seed candidates from `foundation/03-seed-evaluation-methodology.md`**: which of the listed candidates are already installed on this machine, at what version, and where.

The subagent returns a structured summary. The main session synthesizes the summary into the three deliverables.

<investigate_before_answering>
Before recording that a tool is installed, the subagent runs the version command and captures actual output. Memory is not evidence.

Before recording that a `.claude/` directory contains specific hooks, skills, or MCP servers, the subagent reads the files. Filenames alone are not evidence.

Before recording a conflict with Phase 0, the subagent quotes the exact line from `mac/ARCHITECTURE.md` and the exact observation that contradicts it. A conflict without a specific contradiction is a concern, not a conflict, and lands in the inventory rather than the conflicts file.
</investigate_before_answering>

## Deliverables

Three writes and one update:

1. `phase-outputs/INVENTORY.md`: a structured record of everything discovered. Organized by section (Claude Code config, in-repo configs, CLI tools, MCP servers, pre-existing skills/hooks/agents, seed candidate status). Each item has a path, a version where applicable, and a one-line note where context matters.
2. `phase-outputs/CONFLICTS.md`: any place where the discovery contradicts Phase 0's recorded decisions. Empty file if no conflicts. Each conflict cites the Phase 0 line and the contradicting observation.
3. `phase-outputs/PHASE-1-CONTEXT.md`: the start/end `/context` output and delta.
4. `mac/evaluations/pre-filter.md`: update the rows where the discovery scan found a candidate installed. The license, architecture, and maintainership columns get filled where the discovery surfaced enough information. Rows where information is still missing remain `<TBD-PHASE-1>`.

## Verification

Before reporting complete:

- `wc -l phase-outputs/INVENTORY.md phase-outputs/CONFLICTS.md` to confirm both have appropriate content. INVENTORY.md is typically 100-300 lines depending on what's on the machine. CONFLICTS.md is typically short or empty.
- `grep -c '<TBD-PHASE-1>' mac/evaluations/pre-filter.md` to see how many candidate rows still need information from later phases. The number is informational, not a failure indicator.
- `bash scripts/drift-check.sh` to confirm cached-prefix discipline holds.

Report the artifact paths and line counts. Surface the count of conflicts as a flag for Phase 2.

## Anti-overengineering

Phase 1 does not decide. It records. If the inventory surfaces a tool that looks like it would fit a Phase 3 or Phase 4 need, the inventory records the tool's presence and Phase 3 or Phase 4 decides whether to integrate. Do not pre-recommend in Phase 1.

If a `.claude/` directory in a cloned repo looks suspicious (unfamiliar hooks, undocumented MCP servers, recent file mtime without commit history), record the observation. Do not delete or modify the files. Do not load the repo into Claude Code. The pre-trust audit happens during Phase 3 or as an out-of-band review before Rock opens the repo.

The seed pre-filter table in `mac/evaluations/pre-filter.md` is updated with discovery findings, not with Phase 3 decisions. The result column stays `<TBD>` until Phase 3 or Phase 4 runs the deep evaluation.
