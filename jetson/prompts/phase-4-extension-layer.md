# Phase 4 — Extension Layer (Jetson) [SCAFFOLDED]

**This prompt is scaffolded, not validated.** The structure mirrors `mac/prompts/phase-4-extension-layer.md`. Jetson-specific details carry `<NEEDS-JETSON-PORT-VALIDATION>` markers that resolve when Rock executes the Jetson build.

<role>
You are writing the extension layer of the Jetson harness: skills, subagent definitions, MCP server allowlist with per-server tool filtering, extension-layer integrations that survived pre-filter. Phase 3 produced determinism. Phase 4 produces the capability surface that the model uses within that determinism.

Skills are the model's vocabulary for capabilities. Subagents are the model's vocabulary for delegation. MCP servers are the model's vocabulary for external tool surfaces. Each is a permission grant. Least-privilege per Principle 2.
</role>

<effort>xhigh</effort>

<mode>default mode. Phase 4 writes skill files, agent files, updates the MCP allowlist in settings.json.</mode>

<thinking>adaptive</thinking>

<context_budget>Run /context at start and end. Phase 4 reads Phase 3 outputs, foundation, then writes the extension layer. Skill descriptions sit in the cached prefix discovery flow; QC.4b cap is tight. Record in `phase-outputs/PHASE-4-CONTEXT.md`.</context_budget>

<parallel_tool_calls>
Read inputs in parallel: `phase-outputs/ANSWERS.md`, `phase-outputs/INVENTORY.md`, `phase-outputs/PHASE-3-NOTES.md`, `jetson/ARCHITECTURE.md`, `jetson/harness/settings.json`, `jetson/harness/skills/README.md`, `jetson/harness/agents/README.md`, `jetson/evaluations/pre-filter.md`, `jetson/evaluations/deep-eval.md`, `foundation/02-architectural-principles.md`, `foundation/03-seed-evaluation-methodology.md`, relevant sections of `research/Claude_Architecture.md`. Also read Mac equivalents if Mac has built.
</parallel_tool_calls>

<use_parallel_tool_calls>
When deep-evaluating multiple seed candidates, run integration tests in parallel where candidates do not share state. Subagent invocations for parallel deep-eval are appropriate.
</use_parallel_tool_calls>

<scope>
Apply only to:
- `jetson/harness/skills/` (writes: one directory per skill)
- `jetson/harness/agents/` (writes: one markdown file per agent)
- `jetson/harness/settings.json` (updates: `mcpServers` block, `permissions.allow` entries)
- `jetson/evaluations/deep-eval.md` (updates: extension-layer integration outcomes)
- `phase-outputs/PHASE-4-CONTEXT.md` (writes)
- `phase-outputs/PHASE-4-NOTES.md` (writes: rationale per skill, agent, MCP server)

Do not modify `foundation/`, `research/`, `jetson/prompts/`, `jetson/harness/CLAUDE.md`, `jetson/harness/rules/`, `jetson/harness/hooks/`, `jetson/ARCHITECTURE.md`, or `jetson/README.md`.
</scope>

## What to do

### Skills

For each capability the model needs that does not already exist as a Claude Code built-in or as an MCP tool, write a skill in `jetson/harness/skills/<skill-name>/`. Same discipline as Mac.

`<NEEDS-JETSON-PORT-VALIDATION>` per skill: any skill ported from Mac is verified to function on ARM64 Linux:

- Executable bodies use commands available on Ubuntu (no `pbcopy`, `osascript`, `launchctl`).
- Path conventions are POSIX-compliant.
- Any compiled binaries shipped with the skill have ARM64 Linux builds.
- Any Python dependencies have ARM64 wheels or compile from source on Jetson.

Pre-filter survivors that land in the extension layer include configuration repos (`obra/superpowers`, `affaan-m/everything-claude-code`, `disler/claude-code-hooks-mastery`). For each, the deep-eval decision in `jetson/evaluations/deep-eval.md` records whether to adopt wholesale, cherry-pick, or reject.

### Subagent definitions

For each subagent role the harness needs, write a markdown file in `jetson/harness/agents/`. The Phase 5 Reviewer is the most consequential agent. Other agents: inventory subagent for Phase 1, domain-specific reviewers if Phase 2 elected, test-writer if Phase 2 elected.

`<NEEDS-JETSON-PORT-VALIDATION>` per agent: agents ported from Mac that invoke specific tools verify those tools are on Jetson under expected names. Agent definitions are mostly platform-agnostic; the verification is checking that the allowed-tools list resolves to actually-installed tools on this platform.

### MCP server allowlist

For each MCP server Phase 1 inventoried and Phase 4 deep-evaluated, decide whether to allowlist. Each allowlisted server lands in `jetson/harness/settings.json` under `mcpServers` with invocation, explicit tool subset, network egress posture, version pin.

Default posture: deny. Allowlisting is a positive decision.

`<NEEDS-JETSON-PORT-VALIDATION>` per MCP server: ARM64 Linux availability of the server binary or runtime. If the server is npm-based and JavaScript, usually portable. If Go binary, verify ARM64 Linux build. If Python, verify ARM64 wheels for dependencies.

### Deep-evaluate extension-layer seeds

Phase 1 pre-filtered. Phase 4 deep-evaluates survivors that touch the extension layer. Candidates from `foundation/03-seed-evaluation-methodology.md`. For each, run the three exercises plus the Jetson architecture-validation check per `jetson/evaluations/deep-eval.md` format.

### Anti-overengineering block

Adopting an entire seed repo because some of it looks useful is the common trap. Each skill, each agent, each MCP server is a separate decision. Cherry-pick.

Do not write skills for capabilities Claude Code already exposes as built-in tools. Skills wrapping built-ins are cache-prefix pollution.

Do not register MCP servers Rock will not actually use on Jetson.

Do not add `permissions.allow` rules to widen access for convenience.

<investigate_before_answering>
Before adopting a skill from an external repo, read the skill's body and the tools it requires. README is not evidence.

Before allowlisting an MCP server, read the server's tool list and source code where available. Pre-trust audit applies.

Before recording an agent definition, verify model selection against QC.4a cache economics.

Before resolving a `<NEEDS-JETSON-PORT-VALIDATION>` marker, run the actual verification on Jetson. Inference from Mac validation is not evidence for ARM64 Linux.
</investigate_before_answering>

## Deliverables

- Skill directories in `jetson/harness/skills/`.
- Agent definitions in `jetson/harness/agents/`.
- Updated `jetson/harness/settings.json` with MCP allowlist and extension-layer `permissions.allow`.
- Updated `jetson/evaluations/deep-eval.md`.
- `phase-outputs/PHASE-4-NOTES.md`.
- `phase-outputs/PHASE-4-CONTEXT.md`.

## Verification

Before reporting complete:

- `python3 -c "import json; json.load(open('jetson/harness/settings.json'))"` parses.
- `find jetson/harness/skills -name 'SKILL.md' | wc -l` reports skill count.
- `find jetson/harness/agents -name '*.md' | wc -l` reports agent count.
- For each skill with executable body, run language-appropriate SAST on Jetson and record.
- For each MCP server, verify the invocation starts cleanly, lists tools, stops cleanly. Do not register a server that does not start.
- `bash scripts/drift-check.sh` returns 0.

Report counts and line counts.

## Anti-overengineering reminder

Phase 4 is where seeds expand the cached prefix. The instinct to adopt useful-looking things is strong. The discipline that keeps the harness lean: reject components that *would be nice to have* and only adopt components that *close a gap Phase 2 named*.

Ambiguous deep-eval results prefer rejection. Post-launch revision cadence is the appeal mechanism.
