# mcp-deny-server-prefix-default

## Pattern

The default posture is **no MCP deny rule** in `permissions.deny`. Phase 4 owns the allowlist; the absence of any `mcp__*` entry combined with explicit `mcpServers` registrations means only allowlisted servers' tools reach the model's pool.

This file documents the design decision rather than carrying a pattern. The Phase 3 prompt example proposed `mcp__server-prefix` denies for unallowlisted servers, but Claude Code's deny-first ordering (foundation/01 cited from Claude_Architecture.md §5.2) means a blanket `mcp__*` deny would override any narrower `mcp__context7` allow Phase 4 might add. The mechanism is structural, not rule-based.

## Threat addressed

`foundation/01-threat-model.md` Threat actors #6 (compromised or hostile MCP server). Each registered MCP server is a permission grant covering its full tool surface.

## Why no rule

Per Claude_Architecture.md §5.2 `toolMatchesRule()`: "A broad deny ('deny all shell commands') cannot be overridden by a narrow allow ('allow npm test')." A blanket `mcp__*` deny would block every MCP server, including Phase 4 allowlist entries. The correct mechanism is allowlist-by-default-empty via `mcpServers`:

```json
"mcpServers": {}    // Phase 4 adds entries; unlisted servers have no presence
```

Unallowlisted MCP servers do not get registered, do not appear in `getAllBaseTools()`, and never reach the model's tool pool. The deny-first evaluation engine is the wrong layer for this; the tool pool assembly layer (§6.2 step 4) is the right one.

Phase 4 may add per-server deny rules for specific tools within an allowlisted server (e.g., allow `mcp__sentry` but deny `mcp__sentry__delete_project`). Those are narrow denies under broader allows and the deny-first ordering works correctly there.

## Test

Positive (an unlisted MCP server's tools never reach the model):
- Verified via `mcpServers: {}` in `mac/harness/settings.json` plus Phase 4's allowlist additions. The verification is observational at runtime: an MCP tool whose server is not in `mcpServers` does not appear in `/context` tool listings.

Negative (allowlisted servers reach the model):
- Phase 4's allowlist entries with their explicit `command` and `args` define the surface. Each addition is a recorded permission grant per `foundation/03-seed-evaluation-methodology.md`.

## Provenance

Phase 3, 2026-05-11. Foundation: Threat actors #6, Principle 2. Phase 4 owns the allowlist.
