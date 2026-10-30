# bash-deny-rm-rf-root

## Pattern

```
Bash(rm -rf /:*)
Bash(rm -rf ~)
Bash(rm -rf ~/:*)
Bash(rm -rf $HOME:*)
Bash(rm -rf $HOME/)
Bash(rm -rf ${HOME}:*)
Bash(rm -rf ${HOME}/)
Bash(rm -rf /Users:*)
Bash(rm -rf /Users/:*)
Bash(rm -rf /home:*)
Bash(rm -rf /home/:*)
```

These rules are the deterministic floor for the bare spellings only. Claude Code reads a `:*` suffix as a trailing space-wildcard, the same as `Bash(rm -rf / *)`, so `Bash(rm -rf /:*)` matches `rm -rf /` and `rm -rf / x` and nothing else. It does not match `rm -rf /Users/...` or `rm -rf /etc/...`. A rule with no `*` matches one exact command. A `*` inside the pattern matches any text including `/`, so `Bash(rm -rf /Users/*)` would also deny `rm -rf /Users/x/proj/build`, the scoped cleanup the harness must keep allowing. No rule shape can say "this path but not its children".

An earlier revision of this file claimed the `:*` form covered root-prefixed paths and dropped a `/Users/` pattern as redundant on that basis. Verified wrong on October 30, 2026 against Claude Code 2.1.314: `rm -rf /tmp/<nonexistent>` and `rm -rf ~/<nonexistent>` both ran under the three original rules.

## The hook that carries the rest

`PreToolUse-bash-deny-rm-protected-paths.py` denies `rm` and `rmdir` whose target resolves to a protected path. The protected set is the filesystem root (also spelled `/System/Volumes/Data`), every direct child of the root, every `/Users/<name>`, `/home/<name>`, and `/private/<name>`, `$HOME`, mounted volumes (`/Volumes/<drive>`, `/System/Volumes/<volume>`, `/media/<user>`, `/media/<user>/<drive>`, `/mnt/<name>`, `/run/media/<user>/<drive>`), the session's working directory and its ancestors, the credential stores under home (`.ssh`, `.gnupg`, `.aws`, `.kube`, `.config/gh`, `.config/gcloud`, `Library/Keychains`), and the parts of `~/.claude` that make the harness enforce anything (the root, `hooks/`, `rules/`, `settings.json`, `settings.local.json`, `CLAUDE.md`, `audited-hashes.json`). Trailing-slash and glob forms count, where a glob is any last component containing `*`, `?`, `[`, or `{`, so `~/.*` and `~/{*,.*}` are the glob form of home.

A protected directory denies when the rm is recursive (`-r`, `-R`, `--recursive`, combined flags such as `-fr` and `-Rfv`), when the command is `rmdir`, or when the target is a glob. Credential stores and the config files deny on any rm. The hook sees through wrappers (`sudo`, `doas`, `env`, `nice -n 5`, `timeout 10`, `caffeinate`, `setsid`, `/bin/rm`, `RM`, a brace list `{rm,-rf,~}`) by inspecting every token position, follows `cd` and `pushd` across chained segments so `cd .. && rm -rf *` resolves against the parent, treats a `cd` it cannot resolve as making any later `.`, `..`, or glob target deny, scans nested `$(...)`, backtick, `<(...)`, and `>(...)` substitutions, `eval` arguments, `alias` values, here-strings, and pipes into a shell, binds `for X in <literals>` variables, resolves `$HOME`, `$TMPDIR`, and `$PWD`, and denies a recursive rm whose target is a variable or substitution it cannot resolve. A glob at any depth is the glob form of its deepest literal ancestor, so `~/**/*` and `~/*/*` are home. `mv` is judged on its sources, `find` with `-delete` or `-exec rm` on its start paths as globs, and `unlink`, `shred`, and `srm` count as removers. Heredoc bodies are stripped first, only where the operator sits outside quotes and a terminator exists, so a document that quotes a dangerous command can be written. Case folding applies on macOS, Windows, and WSL2, where `/users/<name>` is the same directory as `/Users/<name>`.

Four deliberate exceptions. The glob form of a scratch root passes (`rm -rf /tmp/*` and `rm -rf /tmp/*.log` are cleanup) while `rm -rf /tmp` denies. The glob form of the session cwd itself passes (`rm -rf ./*` in a build directory empties it) while `rm -rf .` and the glob of any ancestor deny. `git rm` passes, since it touches the index and tracked files, which the repository recovers. An rm that follows `ssh`, `docker`, `podman`, `nerdctl`, `kubectl`, `oc`, or `lima` runs on another filesystem and passes. A `cache` or `logs` directory under a credential store passes (`~/.aws/sso/cache`, `~/.kube/cache`), and under `~/.claude` only the plugin cache, project transcripts and memory, shell snapshots, logs, todos, statsig, and debug trees pass.

Children of protected paths pass through to the permission mode in force: `rm -rf ~/proj/build`, `rm -rf /tmp/x`, `rm -rf ~/.claude/plugins/cache/x`. Under `bypassPermissions` that means they run.

Out of scope, by design: deletion by a program the hook does not know (`python`, `rsync --delete`, `git clean`), listed as known gaps in the test matrix so a change in either direction is noticed, and an unquoted `echo rm -rf ~`, which denies as a false positive. Claude Code's critical-path check and the OS are the backstops.

Claude Code's own critical-path check covers a similar set but behaves differently. In a terminal under `auto` or `bypassPermissions` it prompts with a two-minute countdown and then denies. In the Desktop app and the VS Code chat panel it denies unless a `PermissionRequest` hook allows. It covers the root, every top-level directory, home, and the working directory with its parents. It does not cover `/private/<name>`, credential stores, or the config root, its parser does not read `eval`, here-strings, or pipes into a shell, it applies to `rm` and `rmdir` only, and its mounted-drive half is switched off by `CLAUDE_CODE_DISABLE_MOUNTED_DRIVE_RM_PROMPT=1`. The launch-time variable `CLAUDE_CODE_EVEN_MORE_DANGEROUSLY_SKIP_PERMISSIONS=1` is documented to turn the whole check off in `bypassPermissions`, and is also documented to have no effect while any deny or ask rule targets Bash, Edit, or Read, which this harness ships, so that escape is closed here by the rule layer's existence.

What still relaxes the hook: a hook registration without `onFailure: "block"` (the harness sets it on all four destructive-class hooks and the hook exits 2 on any internal error), `disableAllHooks: true` in a project settings file or a `--settings` file, and a mod that handles `tool.check` on a session without managed settings or an enterprise login. The hook ignores `HARNESS_AUTONOMOUS_MODE`.

## Threat addressed

`foundation/02-architectural-principles.md` AP.11 (reversibility weights friction). `rm -rf` against the root, a top-level directory, a home, a mounted volume, the working directory, or a credential store is unrecoverable without filesystem backup. Even `rm -rf /` against an unprivileged account on macOS destroys the user's accessible files.

`foundation/01-threat-model.md` T.2 (prompt injection through agent inputs): a prompt-injection payload that constructs an `rm -rf` against a model-generated path chooses its own target, which is why the protected set is wider than the bare spellings.

## Why deny, not ask

The legitimate use case for `rm -rf /` is zero. For `rm -rf $HOME` it is also zero in a daily-driver context. Denying outright costs nothing because the model never legitimately needs these forms. If Rock has a genuine need, the terminal is the correct path.

The `PreToolUse-external-write-gate` hook does NOT cover Bash invocations (it gates Write, Edit, MultiEdit, and NotebookEdit). This rule and its hook are the Bash side.

## Test

The automated record runs from the repo root:

```
python3 -I mac/harness/hooks/tests/test_bash_deny_rm_protected_paths.py mac/harness/hooks/PreToolUse-bash-deny-rm-protected-paths.py
```

Rule layer, positive (expected to be refused by the settings rules alone. Verify in a live `default`-mode session by reading the rules back in `/permissions` and attempting each, since a pipe test cannot exercise the rule layer):

```
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /"}}'
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf ~"}}'
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf $HOME"}}'
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /Users"}}'
```

Hook layer, positive (the rules miss these, the hook exits 2):

```
echo '{"tool_name":"Bash","tool_input":{"command":"rm -fr /usr"},"cwd":"/Users/x/proj"}'
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf ~/.*"},"cwd":"/Users/x/proj"}'
echo '{"tool_name":"Bash","tool_input":{"command":"cd .. && rm -rf *"},"cwd":"/Users/x/proj"}'
echo '{"tool_name":"Bash","tool_input":{"command":"timeout 10 rm -rf ~"},"cwd":"/Users/x/proj"}'
echo '{"tool_name":"Bash","tool_input":{"command":"rm ~/.ssh/id_rsa"},"cwd":"/Users/x/proj"}'
```

Negative (both layers pass):

```
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf node_modules"},"cwd":"/Users/x/proj"}'
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /tmp/*"},"cwd":"/Users/x/proj"}'
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf ~/proj/build"},"cwd":"/Users/x/proj"}'
echo '{"tool_name":"Bash","tool_input":{"command":"cd build && rm -rf ./*"},"cwd":"/Users/x/proj"}'
```

## Provenance

Phase 3, May 11, 2026. Foundation: AP.11, T.2. Revised October 30, 2026: matching semantics corrected, bare-spelling rules extended, enforcement moved to `PreToolUse-bash-deny-rm-protected-paths.py`, protected set widened after an adversarial premortem reproduced bypasses through wrappers, `cd`, dot-globs, mounted volumes, case folding, and the config root.
