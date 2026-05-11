# bash-deny-dangerously-skip-permissions

## Pattern

```
Bash(claude --dangerously-skip-permissions:*)
```

One entry catches the canonical direct invocation. Wrapped invocations (e.g., `env FOO=bar claude --dangerously-skip-permissions`) are NOT matched by this pattern; v2.1.x's `Bash(prefix:glob)` form requires a literal command-head prefix (per Claude_Architecture.md §5.1 example `Bash(prefix:npm)` and the observed live patterns `Bash(Git:*)`, `Bash(gh:*)`, `Bash(rm:*)` in Phase 1 INVENTORY). An empty-prefix attempt at wildcard matching is unsupported by available evidence.

Residual risk for wrapped invocations: the auto-mode classifier (default mode `auto` per Phase 2 Q1) handles them under its 0.4% false-positive rate. Post-launch revision may add a PreToolUse hook that scans full Bash command content for the literal `--dangerously-skip-permissions` substring; the current calibrated-minimum posture does not include it.

## Threat addressed

`foundation/02-architectural-principles.md` Principle 1 (hooks enforce, CLAUDE.md advises). `--dangerously-skip-permissions` bypasses the entire deterministic layer. The advisory text in `mac/harness/CLAUDE.md` already names this as "not an acceptable tradeoff," and Phase 2 Q9 elected to remove `skipDangerousModePermissionPrompt: true` from the rebuilt `~/.claude/settings.json` so bypass invocations carry a confirmation dialog. The deny rule is the deterministic floor under both.

Also `foundation/01-threat-model.md` Threat actors #6 (compromised or hostile MCP server) and #1 (prompt injection): both rely on the permission system catching the call; bypass mode disables the system entirely.

## Why deny, not ask

The whole point of bypass mode is to skip prompts. Asking via deny-fires-ask-dialog defeats the user's intent. Outright deny is the right cost: legitimate bypass use cases (no-internet sandboxes per `claude --help`) are rare, deliberate, and worth the friction of removing this rule for one session.

## Test

Positive (matches the single pattern):
```
echo '{"tool_name":"Bash","tool_input":{"command":"claude --dangerously-skip-permissions"}}'
echo '{"tool_name":"Bash","tool_input":{"command":"claude --dangerously-skip-permissions --resume"}}'
```

Not matched (residual risk, falls to auto-mode classifier):
```
echo '{"tool_name":"Bash","tool_input":{"command":"env DEBUG=1 claude --dangerously-skip-permissions"}}'
```

Negative (does not fire):
```
echo '{"tool_name":"Bash","tool_input":{"command":"claude --help"}}'
```

## Provenance

Phase 3, 2026-05-11. Foundation: Principle 1, Phase 2 Q9, project root CLAUDE.md "Things that break" §`--dangerously-skip-permissions`.
