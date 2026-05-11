# filesystem-deny-write-secrets

## Pattern

```
Write(**/.env)
Write(**/.env.*)
Write(**/secrets/**)
Write(**/.secrets/**)
Write(**/credentials.json)
Edit(**/.env)
Edit(**/.env.*)
Edit(**/secrets/**)
Edit(**/.secrets/**)
Edit(**/credentials.json)
```

Glob patterns over file paths for the Write and Edit tools. The same patterns repeat for both tools because Claude Code matches tool-name-then-input.

## Threat addressed

`foundation/01-threat-model.md` Assets #2 (secrets) and Threat actors #1 (prompt injection). A prompt-injection payload that asks the model to "save these credentials" must not land in a file under harness defenses.

The pattern surface is calibrated to the documented Phase 1 finding: Phase 1 surfaced plaintext Hetzner API tokens in `~/.claude/mcp.json` and plaintext Neon Postgres URLs in `ai_governance_toolkit_website/.claude/settings.local.json`. Both wrote to non-`.env` paths, so additional protection layers belong to the schemas of those specific tools (settings files are read-only as far as Write tool is concerned; the writes happened via Claude Code accepting `Bash(DEV_DATABASE_URL=...)` permission grants, not via Write). Phase 4 evaluates secret-store integration for MCP credentials.

## Why deny, not ask

`.env` and `secrets/` files have a single legitimate write path: a deliberate `cp .env.example .env` or equivalent template-fill action. The model rarely needs to write these directly. When it does, Rock removes the rule for the session.

## Pattern syntax caveat

Claude Code v2.1.x's deny-rule glob support for Write/Edit path matching is documented in `permissions.ts` but the exact glob dialect (whether `**/.env.*` matches `.env.local`) is not visible from `claude --help`. If runtime testing during Phase 5 polish reveals the patterns are not honored as written, the fallback is the `PreToolUse-external-write-gate` hook extended to include in-cwd secret paths. The rule file documents the intent regardless of the runtime substrate.

## Test

Positive (these should be denied if the runtime honors the glob):
```
echo '{"tool_name":"Write","tool_input":{"file_path":"./.env"}}'
echo '{"tool_name":"Write","tool_input":{"file_path":"./.env.local"}}'
echo '{"tool_name":"Edit","tool_input":{"file_path":"./secrets/api-key.txt"}}'
echo '{"tool_name":"Write","tool_input":{"file_path":"./credentials.json"}}'
```

Negative:
```
echo '{"tool_name":"Write","tool_input":{"file_path":"./README.md"}}'
echo '{"tool_name":"Write","tool_input":{"file_path":"./src/main.py"}}'
```

## Provenance

Phase 3, 2026-05-11. Foundation: Assets #2, Threat actors #1. Phase 1 inventory items #1 and #3 informed the pattern scope.
