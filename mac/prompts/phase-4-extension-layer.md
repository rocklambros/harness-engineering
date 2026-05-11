# Phase 4 — Extension Layer

<role>
You are writing the extension layer of the Mac harness: the skills, the subagent definitions, the MCP server allowlist with per-server tool filtering, and any extension-layer integrations that survived pre-filter. Phase 3 produced the determinism. Phase 4 produces the capability surface that the model uses to get work done within that determinism.

Skills are the model's vocabulary for capabilities the runtime exposes. Subagents are the model's vocabulary for delegation. MCP servers are the model's vocabulary for external tool surfaces. Each is a permission grant; the discipline is least-privilege per Principle 2 in `foundation/02-architectural-principles.md`.
</role>

<effort>xhigh</effort>

<mode>default mode. Phase 4 writes skill files, agent files, and updates the MCP allowlist in settings.json.</mode>

<thinking>adaptive</thinking>

<context_budget>Run /context at start and end. Phase 4 reads the Phase 3 output and the foundation, then writes the extension layer. Skill descriptions sit in the cached prefix discovery flow; the QC.4b cap is tight. Record start, end, and delta in `phase-outputs/PHASE-4-CONTEXT.md`.</context_budget>

<parallel_tool_calls>
Read inputs in parallel at the start: `phase-outputs/ANSWERS.md`, `phase-outputs/INVENTORY.md`, `phase-outputs/PHASE-3-NOTES.md`, `mac/ARCHITECTURE.md`, `mac/harness/settings.json`, `mac/harness/skills/README.md`, `mac/harness/agents/README.md`, `mac/evaluations/pre-filter.md`, `mac/evaluations/deep-eval.md`, `foundation/02-architectural-principles.md`, `foundation/03-seed-evaluation-methodology.md`, and the relevant sections of `research/Claude_Architecture.md` (§6 skills and tools, §8 subagents).
</parallel_tool_calls>

<use_parallel_tool_calls>
When deep-evaluating multiple seed candidates, run their integration tests in parallel where the candidates do not share state. Subagent invocations for parallel deep eval are appropriate here.
</use_parallel_tool_calls>

<scope>
Apply only to:
- `mac/harness/skills/` (writes: one directory per skill, with `SKILL.md` and any supporting files)
- `mac/harness/agents/` (writes: one markdown file per agent definition)
- `mac/harness/settings.json` (updates: the `mcpServers` block with the populated allowlist; the `permissions.allow` array for any tool the extension layer requires)
- `mac/evaluations/deep-eval.md` (updates: integration results for extension-layer seeds)
- `phase-outputs/PHASE-4-CONTEXT.md` (writes)
- `phase-outputs/PHASE-4-NOTES.md` (writes: rationale paragraphs per skill, agent, and MCP server)

Do not modify `foundation/`, `research/`, `mac/prompts/`, `mac/harness/CLAUDE.md`, `mac/harness/rules/`, `mac/harness/hooks/`, `mac/ARCHITECTURE.md`, or `mac/README.md`. Do not change deny rules or hooks from Phase 3 unless a Phase 4 finding requires it; if a Phase 3 change is required, record the rationale in `PHASE-4-NOTES.md` and explicitly note the Phase 3 file modified.
</scope>

## What to do

### Skills

For each capability the model needs that does not already exist as a Claude Code built-in or as an MCP tool, write a skill in `mac/harness/skills/<skill-name>/`. The discipline:

- The skill description in the front-matter is what drives discovery. Spend the time to write a description that the model can actually route on. Vague descriptions cause the SkillTool to miss the skill on the prompts that should hit it. Overly specific descriptions cause false-positive routing.
- The `allowedTools` field is the skill's tool-pool subset. Start with the minimum. Add tools only when the skill cannot function without them.
- Skills with executable bodies (`scripts/`) pass language-appropriate SAST per QC.1.
- Skills that register hooks dynamically declare the hook events in the front-matter.

Pre-filter survivors that land in the extension layer include configuration repos (`obra/superpowers`, `affaan-m/everything-claude-code`, `disler/claude-code-hooks-mastery`). For each, the deep-eval decision in `mac/evaluations/deep-eval.md` records whether to adopt the skills wholesale, cherry-pick, or reject. The skills that get adopted land in `mac/harness/skills/` with their original attribution and any modifications recorded.

### Subagent definitions

For each subagent role the harness needs, write a markdown file in `mac/harness/agents/`. The Phase 5 Reviewer is the most consequential agent; it is defined here and loaded by Phase 5 to audit Phase 5's own output. Other agents the harness may need:

- An inventory subagent for Phase 1 (write the definition here even though Phase 1 already ran; codify the role for future revisions).
- Domain-specific reviewers (security review, SSDF compliance review) if Phase 2 elected.
- A test-writer subagent if Phase 2 elected.

Each agent definition specifies: role, model and effort defaults, allowed-tools subset, when-to-spawn guidance per the Opus 4.7 instruction discipline, and verification criteria the parent uses.

### MCP server allowlist

For each MCP server Phase 1 inventoried and Phase 4 deep-evaluated, decide whether to allowlist. Each allowlisted server lands in `mac/harness/settings.json` under `mcpServers` with:

- The server invocation (command, args, env where applicable).
- The explicit tool subset enabled (no wildcard tool surface).
- The network egress posture documented in `PHASE-4-NOTES.md`.
- The version pin recorded.

Default posture is deny. Allowlisting an MCP server is a positive decision with rationale, not a default.

### Deep-evaluate extension-layer seeds

Phase 1 pre-filtered. Phase 4 deep-evaluates the survivors that touch the extension layer. The candidates from `foundation/03-seed-evaluation-methodology.md`:

- `obra/superpowers`: deep-eval as a skill collection.
- `affaan-m/everything-claude-code`: deep-eval as a configuration reference.
- `disler/claude-code-hooks-mastery`: most of this is Phase 3 territory; the extension-layer pieces deep-eval here.
- `cosai-oasis/project-codeguard`: pre-1.0; integrate in a shape that allows future swap.
- MemPalace: deep-eval as a memory tool against alternatives.
- Serena: deep-eval as a language-server-protocol integration against alternatives.
- Any others surfaced in Phase 1 inventory.

For each, run the three exercises (nominal task, edge case, no-op cost) and record the outcome in `mac/evaluations/deep-eval.md`.

### Anti-overengineering block

A common Phase 4 trap: adopting an entire seed repo because some of it looks useful. Each skill, each agent, each MCP server is a separate decision. Cherry-pick. The seeds are reference, not template.

Do not write skills for capabilities Claude Code already exposes as built-in tools. The 19 always-included tools (Claude_Architecture.md §6.2) cover most file and shell operations. A skill that wraps a built-in tool just to add an opinionated description is cache-prefix pollution, not capability.

Do not register MCP servers that Rock will not actually use. Each server's tools sit in the cache prefix discovery flow whether or not they get invoked. Idle tools cost cache footprint and instruction-following degradation per HumanLayer's analysis.

Do not add `permissions.allow` rules to widen access for the convenience of a Phase 4 component. The deny-first posture means tools the harness needs get explicitly allowed; tools the harness does not need stay denied. If a skill or agent requires a tool that is currently denied, the rationale lands in `PHASE-4-NOTES.md` and the allow entry is added to `settings.json` with a back-reference to the rationale.

<investigate_before_answering>
Before adopting a skill from an external repo, read the skill's body and the tools it requires. A README description is not evidence of what the skill actually does.

Before allowlisting an MCP server, read the server's documented tool list and its source code where available. Pre-trust audit applies here: an MCP server registered without source review is exactly the threat surface CVE-2025-59536 exploited.

Before recording an agent definition, verify the model selection against QC.4a. Same-family parent and subagent share cache; cross-family does not. If a Haiku subagent is being defined under an Opus parent, name the cache-economy tradeoff in the definition.
</investigate_before_answering>

## Deliverables

- Skill directories in `mac/harness/skills/`, each with `SKILL.md` and supporting files.
- Agent definitions in `mac/harness/agents/`, one markdown file per agent.
- Updated `mac/harness/settings.json` with the MCP allowlist and any extension-layer `permissions.allow` entries.
- Updated `mac/evaluations/deep-eval.md` with extension-layer integration outcomes.
- `phase-outputs/PHASE-4-NOTES.md` with rationale per skill, agent, and MCP server.
- `phase-outputs/PHASE-4-CONTEXT.md`.

## Verification

Before reporting complete:

- `python3 -c "import json; json.load(open('mac/harness/settings.json'))"` parses cleanly.
- `find mac/harness/skills -name 'SKILL.md' | wc -l` reports the skill count.
- `find mac/harness/agents -name '*.md' | wc -l` reports the agent count.
- For each skill with an executable body, run the language-appropriate SAST and record results in `PHASE-4-NOTES.md`.
- For each MCP server, verify the invocation works in isolation (start the server, list its tools, stop it) and record in `PHASE-4-NOTES.md`. Do not register a server that does not start cleanly.
- `bash scripts/drift-check.sh` returns 0. The cached-prefix discipline still holds.

Report the artifact paths, skill count, agent count, MCP server count, and the line counts.

## Anti-overengineering reminder

Phase 4 is where seeds expand into the cached prefix. The instinct to adopt useful-looking things is strong. The discipline that keeps the harness lean is to reject components that *would be nice to have* and only adopt components that *close a gap Phase 2 named*.

When a candidate's deep-eval result is ambiguous, prefer rejection. The post-launch revision cadence is the appeal mechanism; a rejected candidate can come back when the signals change. An adopted candidate that turns out wrong costs revisions to remove.
