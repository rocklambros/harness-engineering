# filesystem-deny-write-secrets

## Pattern

```
Edit(**/.env)
Edit(**/.env.*)
Edit(**/secrets/**)
Edit(**/.secrets/**)
Edit(**/credentials.json)
```

Glob patterns over file paths. `Edit(path)` is the only rule shape Claude Code matches for the Write, Edit, and NotebookEdit tools. A `Write(path)` rule is accepted by the settings loader but never matches a tool call, so the five `Write(...)` entries an earlier revision listed here were dead weight and were removed on October 30, 2026. `Edit` rules apply to every built-in tool that edits files, with no version floor. A `Read(path)` deny on the same path would also block Edit and Write (the Write half requires Claude Code 2.1.228 or later), but not NotebookEdit, so `Edit` stays the rule of record.

## Threat addressed

`foundation/01-threat-model.md` T.6 (credential and secret exposure) and T.2 (prompt injection through agent inputs). A prompt-injection payload that asks the model to "save these credentials" must not land in a file under harness defenses.

The pattern surface is calibrated to the documented Phase 1 finding: Phase 1 surfaced plaintext Hetzner API tokens in `~/.claude/mcp.json` and plaintext Neon Postgres URLs in `ai_governance_toolkit_website/.claude/settings.local.json`. Both wrote to non-`.env` paths, so additional protection layers belong to the schemas of those specific tools (settings files are read-only as far as Write tool is concerned; the writes happened via Claude Code accepting `Bash(DEV_DATABASE_URL=...)` permission grants, not via Write). Phase 4 evaluates secret-store integration for MCP credentials.

## Why deny, not ask

`.env` and `secrets/` files have a single legitimate write path: a deliberate `cp .env.example .env` or equivalent template-fill action. The model rarely needs to write these directly. When it does, Rock removes the rule for the session.

## Pattern syntax caveat

Claude Code checks file permissions against `Edit(path)` and `Read(path)` rules only. Rules written for `Write`, `NotebookEdit`, `Glob`, or `MultiEdit` are accepted and never matched (Claude Code permissions reference, read October 30, 2026 against 2.1.314). The `**` glob dialect is the standard one, so `**/.env.*` matches `.env.local` at any depth. If a future runtime stops honoring these patterns, the fallback is the `PreToolUse-external-write-gate` hook extended to include in-cwd secret paths. The rule file documents the intent regardless of the runtime substrate.

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

Phase 3, May 11, 2026. Foundation: T.6, T.2. Phase 1 inventory items #1 and #3 informed the pattern scope. Revised October 30, 2026: dead `Write(...)` entries removed, matching semantics documented.
