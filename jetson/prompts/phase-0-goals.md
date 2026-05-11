# Phase 0 — Goals and Architecture (Jetson)

<role>
You are setting the goals for the Jetson harness build and filling the platform-specific blocks in `jetson/ARCHITECTURE.md`. Phase 0 records the version pins, the model and effort defaults, the sandbox posture, the persistence configuration, and the next-evaluation triggers. You make calibrated decisions and document the rationale. You do not write hooks, deny rules, skills, or agents here. Those are Phase 3 and Phase 4 deliverables.

The Jetson document carries two kinds of unresolved blocks: `<TBD-PHASE-0>` (Phase 0 owns) and `<NEEDS-JETSON-PORT-VALIDATION>` (Phase 0 verifies any that the live environment can confirm; the rest stay for Phase 3 implementation).
</role>

<effort>xhigh</effort>

<mode>plan mode at start. Switch to default mode only to write the updated `jetson/ARCHITECTURE.md`. No other files change in Phase 0.</mode>

<thinking>adaptive</thinking>

<context_budget>Run /context at start and end. Phase 0 reads several foundation documents and the architecture reference. Record state in `phase-outputs/PHASE-0-CONTEXT.md`.</context_budget>

<parallel_tool_calls>
Read foundation documents in parallel: `foundation/00-quality-contract.md`, `foundation/01-threat-model.md`, `foundation/02-architectural-principles.md`, `foundation/03-seed-evaluation-methodology.md`, `foundation/04-research-references.md`. Read `jetson/README.md`, `jetson/ARCHITECTURE.md`, `jetson/harness/CLAUDE.md`, and `jetson/harness/settings.json.template` in parallel.
</parallel_tool_calls>

<scope>
Apply only to:
- `jetson/ARCHITECTURE.md` (writes: fills `<TBD-PHASE-0>` blocks; resolves `<NEEDS-JETSON-PORT-VALIDATION>` blocks the live environment can confirm)
- `phase-outputs/PHASE-0-CONTEXT.md` (writes: the context-budget record)
- `phase-outputs/PHASE-0-DECISIONS.md` (writes: the rationale log)

Do not modify any file in `foundation/`, `research/`, `jetson/prompts/`, `jetson/harness/` (except as scoped), `jetson/evaluations/`, or `jetson/scripts/`. Do not create hooks, skills, agents, or deny rules. Do not pre-write Phase 1 inventory content.
</scope>

## What to do

Read the foundation documents and `jetson/ARCHITECTURE.md`. For each `<TBD-PHASE-0>` block, decide the value or leave it explicitly deferred with a recorded reason. For each `<NEEDS-JETSON-PORT-VALIDATION>` block, verify against the live Jetson environment and either confirm (replacing the marker with the confirmed fact) or document the gap (replacing the marker with a more specific deferred note for Phase 3).

The blocks Phase 0 fills include the standard set (macOS version pin replaced with Ubuntu/JetPack version pin, Node and Python versions, Claude Code version pin, working directory, daily-driver harness path, default model and subagent default, permission mode default, persistence configuration). Add to these:

- **Ubuntu version pin and JetPack version**: read from `/etc/os-release` and `/etc/nv_tegra_release` or equivalent.
- **GPU and CUDA state**: record what's installed and what the harness sees. The harness does not require CUDA, but the inventory of what's available informs Phase 4.
- **Shell default**: `echo $SHELL`. Bash is typical on Ubuntu, but record what's actually configured.
- **Network egress monitoring**: record whether `opensnitch` or equivalent is installed.
- **Disk encryption status**: `lsblk -o NAME,TYPE,FSTYPE` to confirm LUKS is in the stack. Record.
- **Bash sandboxing**: `<NEEDS-JETSON-PORT-VALIDATION>` block. Verify what Claude Code's installed version supports on ARM64 Linux. If sandboxing is not yet implemented for this platform-architecture pair at the installed version, record the gap and the fallback posture (deny-rules + hooks carry the full enforcement burden until sandboxing arrives).
- **Claude Code session log path on Linux**: `<NEEDS-JETSON-PORT-VALIDATION>` block. Run a short session and observe where the log lands. Record.

For each block filled, the decision lands in `jetson/ARCHITECTURE.md`. The rationale lands in `phase-outputs/PHASE-0-DECISIONS.md`, one short paragraph per decision, citing the foundation document or research source that informs the choice.

For each block that cannot be resolved on Jetson without Phase 3 implementation work, record the reason explicitly and tag it for Phase 3.

<investigate_before_answering>
Before recording a version pin, run the version command. Do not assume.

Before recording Claude Code's session log path or sandbox behavior on ARM64 Linux, consult the documentation and run a short session to observe. Do not assume parity with Mac.

Before claiming Bash sandboxing is enabled or has specific behavior on ARM64 Linux, verify against the running Claude Code's actual behavior. Inference from Mac is not evidence.

Before claiming a tool is the ARM64 build, verify with `file $(which <tool>)` or version output that names the architecture.
</investigate_before_answering>

## Deliverables

Three updates and writes:

1. `jetson/ARCHITECTURE.md`: every `<TBD-PHASE-0>` block filled or explicitly deferred with reason. Every `<NEEDS-JETSON-PORT-VALIDATION>` block the live environment can confirm is resolved. Remaining validation markers stay tagged for Phase 3 with a more specific note about what evidence resolves them.
2. `phase-outputs/PHASE-0-CONTEXT.md`: the `/context` output at start and end, with delta.
3. `phase-outputs/PHASE-0-DECISIONS.md`: one short paragraph per filled block, naming the decision and citing the source.

## Verification

Before reporting complete:

- `grep -c '<TBD-PHASE-0>' jetson/ARCHITECTURE.md` confirms no unaddressed Phase 0 blocks remain.
- `grep -c '<NEEDS-JETSON-PORT-VALIDATION>' jetson/ARCHITECTURE.md` reports how many validation markers remain. The number is informational, not a failure indicator. Each remaining marker carries a more specific note than the scaffold version.
- `bash scripts/drift-check.sh` returns 0.
- `wc -l jetson/ARCHITECTURE.md phase-outputs/PHASE-0-DECISIONS.md` confirms substantive content.

Report line counts and remaining validation marker count.

## Anti-overengineering

Phase 0 records decisions. It does not implement them. Hooks, deny rules, skills, agents, and MCP server registrations are Phase 3 and Phase 4. If a Phase 0 decision implies a hook or skill, record the implication for Phase 3 or Phase 4 to act on. Do not write the hook or skill here.

The Quality Contract operationalization section references tools that are not yet wired. Phase 0 does not wire them. Phase 3 evaluates and decides.

When in doubt, defer to Phase 2 or Phase 3 with a recorded reason rather than acting.
