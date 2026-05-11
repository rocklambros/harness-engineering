# Phase 1 — Discovery (Windows)

<role>
You are discovering what is already on this Windows machine that the harness needs to know about: existing Claude Code configuration files, installed CLI tools, MCP server configurations in cloned repositories, pre-existing skills or hooks, WSL2 distribution state, and any conflict between what Phase 0 recorded and what's on disk. Phase 1 produces an inventory and a conflicts list. You do not change anything. You read, you record, you flag.

Discovery is read-only. The threat model in `foundation/01-threat-model.md` names the pre-trust initialization class (CVE-2025-59536). Phase 1 is structurally similar: you are looking at code that could otherwise execute at session start. The discipline is to look at the files, not to load them into Claude Code through any configuration mechanism.
</role>

<effort>high</effort>

<mode>plan mode for the entire phase. Phase 1 writes only build-internal phase outputs.</mode>

<thinking>adaptive</thinking>

<context_budget>Run /context at start and end. Phase 1 reads many files. The inventory subagent absorbs most of the read cost. Record in `phase-outputs/PHASE-1-CONTEXT.md`.</context_budget>

<parallel_tool_calls>
The inventory scan touches more than 20 files. Spawn an inventory subagent for the scan.
</parallel_tool_calls>

<use_parallel_tool_calls>
Within the inventory subagent, use parallel directory listings and `Get-Item` invocations against independent directories.
</use_parallel_tool_calls>

<scope>
Apply only to:
- `phase-outputs/PHASE-1-CONTEXT.md` (writes)
- `phase-outputs/INVENTORY.md` (writes)
- `phase-outputs/CONFLICTS.md` (writes: any conflicts with Phase 0)
- `windows/evaluations/pre-filter.md` (updates: candidate rows where discovery finds a candidate installed)

Do not modify any file in `foundation/`, `research/`, `windows/prompts/`, `windows/ARCHITECTURE.md`, `windows/harness/`, or `windows/scripts/`. Do not write hooks, skills, agents, or deny rules. Do not install or remove any tools. Do not edit existing `.claude/` directories anywhere on the machine.
</scope>

## What to do

Read `phase-outputs/PHASE-0-DECISIONS.md` and `windows/ARCHITECTURE.md` to understand what Phase 0 recorded. Spawn the inventory subagent.

The inventory subagent's task, without modifying:

1. **Claude Code configuration on this Windows machine**: `%USERPROFILE%\.claude\`, `%APPDATA%\claude\`, or equivalent paths the installed Claude Code uses. The `settings.json`, `CLAUDE.md`, hooks, skills, agents, and MCP server configurations already present.
2. **In-repo Claude Code configurations**: every `.claude/` directory in cloned repositories under whatever paths the Windows machine keeps source. Pre-trust audit habit starts here.
3. **WSL2 instance Claude Code configurations**: if WSL2 is in scope, the WSL2 home directory carries its own `~/.claude/` and per-repo configurations. The inventory records WSL2-side and Windows-side separately.
4. **Installed CLI tools relevant to the harness**: tools Phase 0 pre-flight verified, plus dependencies (jq, yq, curl, gh, etc.). Verify Windows x86_64 builds where ambiguous. Record native-Windows vs WSL2-only availability per tool.
5. **MCP server installations**: any MCP servers installed globally (npm global, pipx, winget). Record without invoking.
6. **Pre-existing skills, hooks, or agents from prior experimentation**: anything pre-dating this repo. Note hook script language (PowerShell, bash, Python) per existing artifact.
7. **Seed candidate status**: which candidates from `foundation/03-seed-evaluation-methodology.md` are installed, at what version, with Windows x86_64 confirmation.
8. **Windows-specific signals**: PowerShell module inventory (`Get-Module -ListAvailable` summary), winget package list, Chocolatey/Scoop package list if those package managers are installed, browser presence (relevant for any MCP browser tools), and any host-OS configuration that informs Phase 2 (BitLocker, Defender, AppLocker, WDAC, network monitor).

The subagent returns a structured summary. The main session synthesizes into the three deliverables.

<investigate_before_answering>
Before recording that a tool is installed, run the version command. Memory is not evidence.

Before recording that a `.claude/` directory contains specific hooks, skills, or MCP servers, read the files.

Before recording a Windows x86_64 build is present, verify by file inspection or architecture-naming version output.

Before recording a conflict with Phase 0, quote the exact line from `windows/ARCHITECTURE.md` and the observation that contradicts it.

Before recording a tool as "WSL2-only" or "native Windows", verify by inspecting the install location and `where` (PowerShell) or `which` (WSL2) output.
</investigate_before_answering>

## Deliverables

Three writes and one update:

1. `phase-outputs/INVENTORY.md`: structured record. Sections per category. Each item has path, version where applicable, architecture and execution-context confirmation where ambiguous, one-line context note.
2. `phase-outputs/CONFLICTS.md`: places where discovery contradicts Phase 0. Empty if none.
3. `phase-outputs/PHASE-1-CONTEXT.md`: start/end `/context` output and delta.
4. `windows/evaluations/pre-filter.md`: rows updated where discovery filled the architecture, maintainership, or license columns.

## Verification

Before reporting complete:

- Inventory and conflicts files have appropriate content.
- `<NEEDS-WINDOWS-PORT-VALIDATION>` markers in pre-filter.md are reduced as discovery fills the architecture column.
- The drift check returns 0.

Report artifact paths, line counts, conflict count.

## Anti-overengineering

Phase 1 does not decide. It records. If inventory surfaces a tool that looks like it would fit a Phase 3 or Phase 4 need, the inventory records the tool's presence and Phase 3 or Phase 4 decides. Do not pre-recommend.

If a `.claude/` directory in a cloned repo looks suspicious, record the observation. Do not delete or modify. Do not load the repo into Claude Code. Pre-trust audit happens during Phase 3 or out-of-band before Rock opens the repo.

The seed pre-filter table updates with discovery findings, not Phase 3 decisions. Result column stays `<TBD>` until Phase 3 or Phase 4 runs the deep evaluation.
