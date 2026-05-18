# bash-deny-dangerously-skip-permissions

## Pattern

```
Bash(claude --dangerously-skip-permissions:*)
```

One entry catches the canonical direct invocation. Wrapped invocations (e.g., `env FOO=bar claude --dangerously-skip-permissions`) are NOT matched by this pattern; v2.1.x's `Bash(prefix:glob)` form requires a literal command-head prefix (per Claude_Architecture.md §5.1 example `Bash(prefix:npm)` and the observed live patterns `Bash(Git:*)`, `Bash(gh:*)`, `Bash(rm:*)` in Phase 1 INVENTORY). An empty-prefix attempt at wildcard matching is unsupported by available evidence.

Residual risk for wrapped invocations: the auto-mode classifier (default mode `auto` per Phase 2 Q1) handles them under its 0.4% false-positive rate. Post-launch revision may add a PreToolUse hook that scans full Bash command content for the literal `--dangerously-skip-permissions` substring; the current calibrated-minimum posture does not include it.

## Threat addressed

`foundation/02-architectural-principles.md` Principle 1 (hooks enforce, CLAUDE.md advises). A *model-proposed* `--dangerously-skip-permissions` invocation would let the model escalate to bypass mode by itself, defeating the entire deterministic layer. The advisory text in `mac/harness/CLAUDE.md` names model-proposed bypass as a path the harness keeps closed; this deny rule is the deterministic floor under it.

Also `foundation/01-threat-model.md` Threat actors #6 (compromised or hostile MCP server) and #1 (prompt injection): both rely on the permission system catching the call. A model that could invoke `claude --dangerously-skip-permissions` from a Bash tool call could re-launch itself in bypass mode and turn a single injected instruction into a privilege escalation. The rule prevents that path.

## Out of scope

Operator-initiated bypass at session start (the operator typing `claude --dangerously-skip-permissions` into a terminal directly) is a separate decision the harness permits. Phase 2 Q9 was narrowed 2026-05-11 to apply the deny rule to model-proposed invocations only; `skipDangerousModePermissionPrompt: true` in `~/.claude/settings.json` is the documented expected state for the operator-initiated case. The runtime persists that key when the bypass-mode warning dialog is dismissed with the don't-ask-again affordance, so the key returning after deletion is the runtime working as designed under operator-initiated bypass, not a defect.

The residual risk under operator-initiated bypass — prompt injection in tool returns reaching shell without confirmation — lands on the operator and is accepted as a documented exception in `foundation/01-threat-model.md`.

## Why deny, not ask

For model-proposed invocations, the whole point of bypass mode is to skip prompts; asking via deny-fires-ask-dialog defeats the intent and costs nothing if the operator wanted bypass mode they would launch the session that way themselves. Outright deny is the right cost. Operator-initiated bypass remains available via terminal launch; the rule does not block that path.

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

Phase 3, 2026-05-11. Foundation: Principle 1, Phase 2 Q9 (narrowed 2026-05-11 to model-proposed-only), project root CLAUDE.md "Things that break" §`--dangerously-skip-permissions`.
