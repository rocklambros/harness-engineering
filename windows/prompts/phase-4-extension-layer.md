# Phase 4 — Extension Layer (Windows) [SCAFFOLDED]

**This prompt is scaffolded, not validated.** The structure mirrors `mac/prompts/phase-4-extension-layer.md`. Windows-specific details carry `<NEEDS-WINDOWS-PORT-VALIDATION>` markers.

<role>
You are writing the extension layer of the Windows harness: skills, subagent definitions, MCP server allowlist with per-server tool filtering, extension-layer integrations that survived pre-filter. Phase 3 produced determinism. Phase 4 produces the capability surface that the model uses within that determinism.

Skills are the model's vocabulary for capabilities. Subagents are the model's vocabulary for delegation. MCP servers are the model's vocabulary for external tool surfaces. Each is a permission grant. Least-privilege per Principle 2.
</role>

<effort>xhigh</effort>

<mode>default mode. Phase 4 writes skill files, agent files, updates the MCP allowlist in settings.json.</mode>

<thinking>adaptive</thinking>

<context_budget>Run /context at start and end. Phase 4 reads Phase 3 outputs, foundation, then writes the extension layer. Skill descriptions sit in the cached prefix discovery flow. QC.4b cap is tight. Record in `phase-outputs/PHASE-4-CONTEXT.md`.</context_budget>

<parallel_tool_calls>
Read inputs in parallel: `phase-outputs/ANSWERS.md`, `phase-outputs/INVENTORY.md`, `phase-outputs/PHASE-3-NOTES.md`, `windows/ARCHITECTURE.md`, `windows/harness/settings.json`, `windows/harness/skills/README.md`, `windows/harness/agents/README.md`, `windows/evaluations/pre-filter.md`, `windows/evaluations/deep-eval.md`, `foundation/02-architectural-principles.md`, `foundation/03-seed-evaluation-methodology.md`, relevant sections of `research/Claude_Architecture.md`. Also read Mac and Jetson equivalents if those have built.
</parallel_tool_calls>

<use_parallel_tool_calls>
When deep-evaluating multiple seed candidates, run integration tests in parallel where candidates do not share state.
</use_parallel_tool_calls>

<scope>
Apply only to:
- `windows/harness/skills/` (writes: one directory per skill)
- `windows/harness/agents/` (writes: one markdown file per agent)
- `windows/harness/settings.json` (updates: `mcpServers` block, `permissions.allow` entries)
- `windows/evaluations/deep-eval.md` (updates: extension-layer integration outcomes)
- `phase-outputs/PHASE-4-CONTEXT.md` (writes)
- `phase-outputs/PHASE-4-NOTES.md` (writes: rationale per skill, agent, MCP server)

Do not modify `foundation/`, `research/`, `windows/prompts/`, `windows/harness/CLAUDE.md`, `windows/harness/rules/`, `windows/harness/hooks/`, `windows/ARCHITECTURE.md`, or `windows/README.md`.
</scope>

## What to do

### Skills

For each capability the model needs that does not already exist as a Claude Code built-in or as an MCP tool, write a skill in `windows/harness/skills/<skill-name>/`. Same discipline as Mac and Jetson.

Mac wrote 2 skills (per `phase-outputs/PHASE-4-NOTES.md`): `mcp-server-pre-trust-audit` (six-check audit framework) and `seed-evaluation` (two-stage methodology). Both are pure markdown with no executable bodies. Mac also adopted 14 skills from `superpowers@claude-plugins-official` v5.1.0 wholesale (corrected from the earlier 17-skill miscount per Phase 5 audit F08). Per-skill port verifies:

- Executable bodies use commands available on Windows (no `pbcopy`, `osascript`, `launchctl`, `apt`, `brew`).
- Path conventions match Phase 2's canonicalization decision.
- Any compiled binaries shipped with the skill have Windows x86_64 builds.
- Any Python dependencies install via pip without compilation errors (or via pre-built wheels).
- Shell-class skills route via Phase 2's chosen execution context (native PowerShell, native cmd, WSL2 bash).

Pre-filter survivors that land in the extension layer include configuration repos (`obra/superpowers`, `affaan-m/everything-claude-code`, `disler/claude-code-hooks-mastery`). For each, the deep-eval decision in `windows/evaluations/deep-eval.md` records whether to adopt wholesale, cherry-pick, or reject.

### Subagent definitions

For each subagent role the harness needs, write a markdown file in `windows/harness/agents/`. The Phase 5 Reviewer is the most consequential agent. Other agents: inventory subagent for Phase 1, domain-specific reviewers, test-writer if Phase 2 elected.

Mac wrote 2 agents (per `phase-outputs/PHASE-4-NOTES.md`): `reviewer` (Phase 5 Writer/Reviewer pattern, same-family Opus 4.7 for cache lineage per QC.4a) and `inventory` (read-only discovery scan codifying the Phase 1 role for future re-runs). Agent definitions are mostly platform-agnostic; per-agent port verifies the allowed-tools list resolves to actually-installed tools on Windows under expected names and execution contexts.

### MCP server allowlist

For each MCP server Phase 1 inventoried and Phase 4 deep-evaluated, decide whether to allowlist. Each allowlisted server lands in `windows/harness/settings.json` under `mcpServers` with invocation, explicit tool subset, network egress posture, version pin.

Default posture: deny.

Mac's Phase 4 `enabledPlugins` calibrated minimum was `superpowers@claude-plugins-official` v5.1.0 + `mempalace@mempalace` v3.3.2 (per `phase-outputs/PHASE-4-NOTES.md`), with `mcpServers` empty. Mac deferred 13 currently-enabled-but-not-in-harness-reference plugins to Phase 5 daily-driver review. Per-MCP-server port verifies Windows x86_64 availability of the server binary or runtime. Go binaries usually portable. Python typically works. npm sometimes hits Windows-specific issues with native modules requiring MSVC build tools. The context7 `npx -y @upstash/context7-mcp` unpinned-fetch supply-chain concern (per Mac Phase 4 notes) applies cross-platform; pin the version or skip.

### Deep-evaluate extension-layer seeds

Phase 1 pre-filtered. Phase 4 deep-evaluates survivors. For each, run the three exercises plus the Windows-specific validation checks per `windows/evaluations/deep-eval.md` format.

### Anti-overengineering block

Adopting an entire seed repo because some of it looks useful is the common trap. Each skill, each agent, each MCP server is a separate decision. Cherry-pick.

Do not write skills for capabilities Claude Code already exposes as built-in tools.

Do not register MCP servers Rock will not actually use on Windows.

Do not add `permissions.allow` rules to widen access for convenience.

<investigate_before_answering>
Before adopting a skill from an external repo, read the skill's body and the tools it requires. README is not evidence.

Before allowlisting an MCP server, read the server's tool list and source code where available. Pre-trust audit applies.

Before recording an agent definition, verify model selection against QC.4a cache economics.

Before resolving a marker, run the actual verification on Windows. Mac or Jetson inference is informational, not evidence. Mac Phase 4 deep-eval results land in `mac/evaluations/deep-eval.md` for reference; the Windows equivalent must produce its own three-exercise outcomes per `foundation/03-seed-evaluation-methodology.md`.
</investigate_before_answering>

## Deliverables

- Skill directories in `windows/harness/skills/`.
- Agent definitions in `windows/harness/agents/`.
- Updated `windows/harness/settings.json` with MCP allowlist and extension-layer `permissions.allow`.
- Updated `windows/evaluations/deep-eval.md`.
- `phase-outputs/PHASE-4-NOTES.md`.
- `phase-outputs/PHASE-4-CONTEXT.md`.

## Verification

Before reporting complete:

- `windows/harness/settings.json` parses as strict JSON.
- Skill count and agent count reported.
- Each skill with executable body: SAST-clean (language-appropriate).
- Each MCP server: starts cleanly, lists tools, stops cleanly. Do not register a server that does not start.
- Drift check returns 0.

Report counts and line counts.

## Anti-overengineering reminder

Phase 4 is where seeds expand the cached prefix. The instinct to adopt useful-looking things is strong. The discipline: reject components that *would be nice to have* and only adopt components that *close a gap Phase 2 named*.

Ambiguous deep-eval results prefer rejection. Post-launch revision cadence is the appeal mechanism.
