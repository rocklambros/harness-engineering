# rules/

Static permission rules for Claude Code. Each rule is a deny pattern or allow pattern that the Claude Code permission system evaluates at tool-pool assembly time and at every tool invocation.

Rules live here so that Phase 3 (deterministic layer) can write them as small, focused files with rationale comments, then Phase 5 wires them into `mac/harness/settings.json` through the `permissions.deny` and `permissions.allow` arrays.

## Naming convention

`<scope>-<verb>.md` per rule. Examples: `bash-deny.md`, `filesystem-write-outside-cwd.md`, `mcp-server-allowlist.md`.

Each file holds the rule pattern, the threat or policy it addresses, the citation in `foundation/01-threat-model.md` or `foundation/02-architectural-principles.md`, and the test that verifies the rule actually fires.

## Security posture

Deny-first. A broad deny beats a narrow allow per Claude_Architecture.md §5.2 (`permissions.ts`, `toolMatchesRule()`). Server-prefix patterns (`mcp__server`) strip whole tool families from the model's view before invocation.

Rules are deterministic. They run regardless of model mood, context-window pressure, or prompt design. The advisory equivalent in `harness/CLAUDE.md` reinforces rules but does not substitute for them (Principle 1 in `foundation/02-architectural-principles.md`).

## Phase coverage

Phase 3 populates this directory based on the threats Phase 2 elected to enforce in the deterministic layer. Phase 5 audits each rule against the threat model and the Quality Contract through the Writer/Reviewer subagent pattern.
