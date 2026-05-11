# bash-deny-dangerously-skip-permissions

## Pattern

```
Bash(claude --dangerously-skip-permissions:*)
Bash(:*--dangerously-skip-permissions*)
```

Two entries to catch the canonical form and any wrapped invocation (e.g., `env FOO=bar claude --dangerously-skip-permissions`). The second pattern matches the flag anywhere in the command.

## Threat addressed

`foundation/02-architectural-principles.md` Principle 1 (hooks enforce, CLAUDE.md advises). `--dangerously-skip-permissions` bypasses the entire deterministic layer. The advisory text in `mac/harness/CLAUDE.md` already names this as "not an acceptable tradeoff," and Phase 2 Q9 elected to remove `skipDangerousModePermissionPrompt: true` from the rebuilt `~/.claude/settings.json` so bypass invocations carry a confirmation dialog. The deny rule is the deterministic floor under both.

Also `foundation/01-threat-model.md` Threat actors #6 (compromised or hostile MCP server) and #1 (prompt injection): both rely on the permission system catching the call; bypass mode disables the system entirely.

## Why deny, not ask

The whole point of bypass mode is to skip prompts. Asking via deny-fires-ask-dialog defeats the user's intent. Outright deny is the right cost: legitimate bypass use cases (no-internet sandboxes per `claude --help`) are rare, deliberate, and worth the friction of removing this rule for one session.

## Test

Positive:
```
echo '{"tool_name":"Bash","tool_input":{"command":"claude --dangerously-skip-permissions"}}'
echo '{"tool_name":"Bash","tool_input":{"command":"env DEBUG=1 claude --dangerously-skip-permissions --resume"}}'
```

Negative:
```
echo '{"tool_name":"Bash","tool_input":{"command":"claude --help"}}'
```

## Provenance

Phase 3, 2026-05-11. Foundation: Principle 1, Phase 2 Q9, project root CLAUDE.md "Things that break" §`--dangerously-skip-permissions`.
