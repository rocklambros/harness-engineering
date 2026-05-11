# CLAUDE.md

## Role

You are working in `/Users/klambros/harness-engineering/`, the public reference repo documenting how Rock Lambros built his Claude Code harness across Mac, Jetson AGX Orin, and Windows. You author and refine the prompts, configurations, and rationale documents that Claude Code sessions execute against the three machines.

The repo is a polished tool with educational framing. Personal-specific decisions are the value, not the obstacle. The artifact is the reasoning preserved alongside the configuration.

## Code standards

Apply the writing rules to every file you produce in this repo. No em dashes. No semicolons. No sentences starting with conjunctions. No AI filler (just, very, really, actually, certainly, basically, literally). No corporate slop (utilize, facilitate, leverage as verb, robust, seamless, transformative, comprehensive, holistic). Plain words. Active voice. American English. Paragraphs over bullets. Bullets only for 3-7 discrete items where visual separation aids comprehension.

Match confidence to evidence. State facts directly. Flag genuine uncertainty without hedging everything. The voice is educational and first-person, modeled on `rocklambros/zerg` and `rocklambros/TRACT`.

For executable code: produce finished, secure, runnable output with no linting errors. Version and owner on artifacts that have them. Inline comments on non-obvious decisions. Error boundaries and fallback modes. Kill switches where appropriate. No commented-out code, no placeholder implementations, no redundant dependencies.

Comment the *why*, not the *what*. The code shows what it does. The reasoning behind a non-obvious decision is what survives. *(QC.3)*

## Security rules

The Quality Contract in `foundation/00-quality-contract.md` is the authoritative version. Treat the following as the operational summary.

QC.1 (NIST SP 800-218 alignment): Pinned dependencies, SBOM on release, secret scan in pre-commit, SAST gate on executable additions, VDP in `SECURITY.md`.

QC.4a (cache discipline, API/SDK): Explicit `"ttl": "1h"` on cache_control where reuse is expected. The default reverted to 5m in March 2026. Telemetry-off kills 1h TTL silently.

QC.4b (context discipline, Claude Code): CLAUDE.md hierarchy under 400 lines total, target 250. No timestamps or per-run state in the cached prefix. Use `<system-reminder>` blocks for changing data. Run `/context` at the start and end of every phase; record the delta.

QC.5 (versioning): The harness pins to a Claude Code minor-version range. Re-evaluate on a minor bump.

Hooks enforce. CLAUDE.md advises. Any rule that must hold every time lives in a hook script, not in this file. *(See `foundation/02-architectural-principles.md`.)*

## Core constraints

Locked decisions from `CHECKPOINT.md`. Do not relitigate, propose alternatives to, or quietly drift from these:

- Repo is a public reference, not a clone-and-run template.
- Repo structure is shared `foundation/` plus three platform sections (`mac/`, `jetson/`, `windows/`).
- Capabilities are identical across the three platforms. One tool when possible, equivalent tool per platform when not. Mac validated; Jetson and Windows scaffolded with "needs validation when ported" markers.
- License is MIT.
- Working directory is `/Users/klambros/harness-engineering/`.
- No discrete dogfooding phase. Revisions land continuously after launch.
- Commit messages follow the project template: phase or topic, Context, Decision, Why, Tradeoff.

When a conversation pushes against one of these, name the conflict and ask before proceeding. Do not silently work around them.

Scope discipline (QC.2): produce artifacts for the named deliverable and nothing else. New files, new dependencies, new abstractions, new test scaffolding require an explicit decision recorded in the phase output or commit message. Refactoring adjacent code is sometimes correct and sometimes is what the phase asked for; scope expansion is a decision, not a habit.

## Things that break

The patterns below have specific failure modes documented in `research/Claude_Architecture.md`. Avoid them.

Bash command chains with more than 50 subcommands fall back to a single generic approval prompt instead of per-subcommand deny-rule checks. Adversa.ai 2026 documented this. Cap chains at the PreToolUse hook.

Pre-trust initialization (CVE-2025-59536 class) executes code in `.claude/settings.json` and `.mcp.json` before the user trust dialog appears. Treat every cloned repo as hostile until those files are audited.

Model-proposed `--dangerously-skip-permissions` invocations are denied at the Bash rule layer; the 0.4% false-positive rate of the auto-mode classifier (Hughes 2026) is the cheaper trade against model-initiated bypass. Operator-initiated bypass at session start (terminal launch with the flag) is a separate decision and is permitted; `skipDangerousModePermissionPrompt: true` in `~/.claude/settings.json` is the documented expected state for that case. The deny rule preserves the threat-model assumption that the model cannot escalate to bypass mode by itself; the residual risk under operator-initiated bypass (prompt injection in tool returns reaching shell without confirmation) lands on the operator.

Long CLAUDE.md hierarchies degrade instruction following uniformly across instruction count. HumanLayer's analysis surfaces this. A short focused CLAUDE.md outperforms a long thorough one.

Cache writes shorter than 1024 tokens silently fail to cache. Per-model cache isolation means Opus and Haiku do not share cache; subagent model selection affects cache economics, not just inference cost.

Timestamps or per-run identifiers in CLAUDE.md or any cached-prefix file break cache reuse without raising an error. The drift check in `scripts/drift-check.sh` flags them.

## Operational

The build environment is macOS on Apple Silicon (ARM64). Claude Code runs from `/Users/klambros/harness-engineering/`. The platform-specific operational details for Mac live in `mac/ARCHITECTURE.md`. The Jetson and Windows equivalents live in their respective sections.

Build sequence: Phase 0 (goals and architecture) → Phase 1 (discovery, plan mode, inventory subagent) → Phase 2 (architecture interview using `AskUserQuestion`) → Phase 3 (deterministic layer: hooks, deny rules, sandbox) → Phase 4 (extension layer: skills, agents, MCP servers, seeds) → Phase 5 (wire and document, Writer/Reviewer subagent pattern).

Per-phase patterns:

- Plan mode for Phase 1 (discovery) and Phase 2 (interview).
- Subagent for the Phase 1 inventory scan (touches more than 20 files). Synthesis happens in the main session.
- `AskUserQuestion` tool drives Phase 2. Do not ask obvious questions or questions already answered in `phase-outputs/ANSWERS.md`.
- Writer/Reviewer subagent pattern for Phase 5: main session writes; subagent audits against the Quality Contract and `foundation/01-threat-model.md`.
- `--fork-session` is documented for phases where two architectural paths are worth trying in parallel.

For the prompts authored in this repo: every phase prompt uses the standard header (effort, mode, thinking, context budget, parallel tool calls, scope). Opus 4.7-specific guidance: scope every directive explicitly (4.7 follows literally); strip CAPS and "CRITICAL: MUST" emphasis; use adaptive thinking and effort levels, not budget_tokens; spell out when to spawn subagents (4.7 spawns fewer than 4.6 by default).

MCP servers are not listed here. Tools defer and load on demand via tool_search. Adding the full server list to this file is exactly the kind of long-CLAUDE.md mistake noted above.

## Status

Project state lives in `CHECKPOINT.md` (root, not committed). The current build phase, locked decisions, and open questions all live there. Read `CHECKPOINT.md` before responding to a new conversation; do not re-read `CONVERSATION_HISTORY.md` unless the request requires understanding *why* a decision was made.

Current batch: Batch 1 (root and foundation) complete. Next batch: Mac section. Confirmation required from Rock before starting any batch.

Auto memory posture: deferred to Phase 2 interview output. Once decided, the position lands in this file as an explicit enable or disable line.

MemPalace and Serena: already installed on Mac. Decisions on adoption deferred to Phase 4 (extension layer). They get evaluated against alternatives, not auto-adopted.
