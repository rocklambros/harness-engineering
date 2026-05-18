# bash-deny-sudo

## Pattern

```
Bash(sudo:*)
```

Matches any Bash command starting with `sudo`. The harness has no legitimate need for root privileges; package installs use Homebrew (no sudo), user-scope pip and npm (no sudo), and ad-hoc commands stay in the user's home and the working directory.

## Threat addressed

`foundation/02-architectural-principles.md` Principle 2 (least privilege). Root execution expands the blast radius of any tool invocation by orders of magnitude. The 0.4% false-positive rate of the auto-mode classifier (Hughes 2026) becomes a different problem at root: a single mis-approval rewrites system files.

Also `foundation/01-threat-model.md` Threat actors #1 (prompt injection via files and tool returns). A prompt-injection payload that lands a sudo command in the model's context can do significantly more damage at root than at user level.

## Why deny, not ask

The legitimate-sudo case in a Claude Code session is rare enough that a deny + Rock-removes-temporarily is the right friction. The `ask` alternative ends up at the same place (Rock approves or denies in dialog) with worse semantics: the model learns that sudo is approvable, which trains it toward future sudo invocations.

## Test

Positive:

```
echo '{"tool_name":"Bash","tool_input":{"command":"sudo apt-get install foo"}}'
echo '{"tool_name":"Bash","tool_input":{"command":"sudo -E env"}}'
```

Negative:

```
echo '{"tool_name":"Bash","tool_input":{"command":"echo not_sudo_just_a_string"}}'
```

## Provenance

Phase 3, 2026-05-11. Foundation: Principle 2, Threat actors #1.
