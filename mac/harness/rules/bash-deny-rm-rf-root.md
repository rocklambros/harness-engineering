# bash-deny-rm-rf-root

## Pattern

```
Bash(rm -rf /:*)
Bash(rm -rf /*)
Bash(rm -rf $HOME:*)
Bash(rm -rf ~/:*)
Bash(rm -rf /Users/:*)
```

Five patterns cover the canonical destructive forms: literal root, root with paths, variable-expanded home, tilde home, and the macOS Users root. The patterns target the highest-impact cases; broader `rm -rf` denies would block legitimate scoped cleanup that the harness needs (build directories, temp folders inside cwd).

## Threat addressed

`foundation/02-architectural-principles.md` Principle 3 (reversibility-weighted risk). `rm -rf` against the root, home, or `/Users` tree is unrecoverable without filesystem backup. Even `rm -rf /` against an unprivileged account on macOS destroys the user's accessible files.

Also `foundation/01-threat-model.md` Threat actors #1 (prompt injection): a prompt-injection payload that constructs an `rm -rf` against a model-generated path can chain into this if not gated.

## Why deny, not ask

The legitimate use case for `rm -rf /` is zero. For `rm -rf $HOME` it is also zero in a daily-driver context. Denying outright costs nothing because the model never legitimately needs these forms; if Rock has a genuine need, manual approval via the deny-override flow is the correct path.

Scoped `rm -rf /path/inside/cwd/` is not blocked by these patterns. The `PreToolUse-external-write-gate` hook does NOT cover Bash invocations (it gates Write/Edit/MultiEdit/NotebookEdit), so `rm -rf` against paths outside cwd that don't match the specific patterns here will pass through to interactive approval under default mode. Phase 5 may extend coverage if a specific failure mode justifies the additional surface.

## Test

Positive:
```
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /"}}'
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf ~/"}}'
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf $HOME"}}'
```

Negative:
```
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf node_modules"}}'
echo '{"tool_name":"Bash","tool_input":{"command":"rm /tmp/log.txt"}}'
```

## Provenance

Phase 3, 2026-05-11. Foundation: Principle 3, Threat actors #1.
