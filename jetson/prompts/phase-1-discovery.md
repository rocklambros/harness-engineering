# Phase 1 — Discovery (Jetson)

<role>
You are discovering what is already on this Jetson AGX Orin that the harness needs to know about: existing Claude Code configuration files, installed CLI tools, MCP server configurations in cloned repositories, pre-existing skills or hooks, and any conflict between what Phase 0 recorded and what's on disk. Phase 1 produces an inventory and a conflicts list. You do not change anything. You read, you record, you flag.

Discovery is read-only. The threat model in `foundation/01-threat-model.md` names the pre-trust initialization class (CVE-2025-59536). Phase 1 is structurally similar: you are looking at code that could otherwise execute at session start. The discipline is to look at the files, not to load them into Claude Code through any configuration mechanism.
</role>

<effort>high</effort>

<mode>plan mode for the entire phase. Phase 1 writes only build-internal phase outputs.</mode>

<thinking>adaptive</thinking>

<context_budget>Run /context at start and end. Phase 1 reads many files. The inventory subagent absorbs most of the read cost. Record in `phase-outputs/PHASE-1-CONTEXT.md`.</context_budget>

<parallel_tool_calls>
The inventory scan touches more than 20 files. Spawn an inventory subagent for the scan rather than reading files serially in the main session.
</parallel_tool_calls>

<use_parallel_tool_calls>
Within the inventory subagent, use parallel `find`, `ls`, and `cat` invocations against independent directories.
</use_parallel_tool_calls>

<scope>
Apply only to:
- `phase-outputs/PHASE-1-CONTEXT.md` (writes)
- `phase-outputs/INVENTORY.md` (writes)
- `phase-outputs/CONFLICTS.md` (writes: any conflicts with Phase 0)
- `jetson/evaluations/pre-filter.md` (updates: candidate rows where discovery finds a candidate installed)

Do not modify any file in `foundation/`, `research/`, `jetson/prompts/`, `jetson/ARCHITECTURE.md`, `jetson/harness/`, or `jetson/scripts/`. Do not write hooks, skills, agents, or deny rules. Do not install or remove any tools. Do not edit existing `.claude/` directories anywhere on the machine.
</scope>

## What to do

Read `phase-outputs/PHASE-0-DECISIONS.md` and `jetson/ARCHITECTURE.md` to understand what Phase 0 recorded. Spawn the inventory subagent.

The inventory subagent's task, without modifying:

1. **Claude Code configuration on this Jetson**: `~/.claude/`, `~/.config/claude/`, or equivalent. The `settings.json`, `CLAUDE.md`, hooks, skills, agents, and MCP server configurations already present.
2. **In-repo Claude Code configurations**: every `.claude/` directory in cloned repositories under whatever paths the Jetson keeps source. Pre-trust audit habit starts here.
3. **Installed CLI tools relevant to the harness**: tools Phase 0 pre-flight verified, plus dependencies (jq, yq, curl, gh, etc.). Verify ARM64 Linux builds for any tool where this is ambiguous.
4. **MCP server installations**: any MCP servers installed globally (npm global, pipx, apt). Record without invoking.
5. **Pre-existing skills, hooks, or agents from prior experimentation**: anything pre-dating this repo. ARM64 Linux behavior verification of any shipped executable bodies.
6. **Seed candidate status**: which candidates from `foundation/03-seed-evaluation-methodology.md` are installed, at what version, with ARM64 Linux confirmation.
7. **Jetson-specific signals**: `nvidia-smi` output (or Jetson equivalent), CUDA version, GPU library state. The harness does not depend on these but the inventory informs Phase 4 capability decisions.

The subagent returns a structured summary. The main session synthesizes into the three deliverables.

<investigate_before_answering>
Before recording that a tool is installed, run the version command. Memory is not evidence.

Before recording that a `.claude/` directory contains specific hooks, skills, or MCP servers, read the files.

Before recording an ARM64 Linux build is what's present, verify with `file` or architecture-naming version output.

Before recording a conflict with Phase 0, quote the exact line from `jetson/ARCHITECTURE.md` and the observation that contradicts it.
</investigate_before_answering>

## Deliverables

Three writes and one update:

1. `phase-outputs/INVENTORY.md`: structured record of everything discovered. Sections per category. Each item has path, version where applicable, architecture confirmation where ambiguous, one-line context note where relevant.
2. `phase-outputs/CONFLICTS.md`: places where discovery contradicts Phase 0's recorded decisions. Empty if none.
3. `phase-outputs/PHASE-1-CONTEXT.md`: start/end `/context` output and delta.
4. `jetson/evaluations/pre-filter.md`: rows updated where discovery filled the architecture, maintainership, or license columns.

## Verification

Before reporting complete:

- `wc -l phase-outputs/INVENTORY.md phase-outputs/CONFLICTS.md` confirms appropriate content.
- `grep -c '<NEEDS-JETSON-PORT-VALIDATION>' jetson/evaluations/pre-filter.md` reports how many candidate rows still need ARM64 confirmation. Informational.
- `bash scripts/drift-check.sh` returns 0.

Report artifact paths, line counts, conflict count.

## Anti-overengineering

Phase 1 does not decide. It records. If inventory surfaces a tool that looks like it would fit a Phase 3 or Phase 4 need, the inventory records the tool's presence and Phase 3 or Phase 4 decides. Do not pre-recommend.

If a `.claude/` directory in a cloned repo looks suspicious, record the observation. Do not delete or modify. Do not load the repo into Claude Code. Pre-trust audit happens during Phase 3 or out-of-band before Rock opens the repo.

The seed pre-filter table updates with discovery findings, not Phase 3 decisions. Result column stays `<TBD>` until Phase 3 or Phase 4 runs the deep evaluation.
