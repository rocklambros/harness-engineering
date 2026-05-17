# Hooks

The deterministic enforcement scripts that Claude Code invokes on specific events. Hooks are the highest-confidence policy enforcement surface in the harness. Per AP.1, anything that must not be bypassed lives here, not in CLAUDE.md.

All hooks fail closed per AP.8: if the script errors, the action is blocked rather than silently allowed.

## Hooks in this directory

| File | Event | Purpose |
| --- | --- | --- |
| `post-tool-use-semgrep.sh` | PostToolUse on Write, Edit, MultiEdit | Commit-time hardening. Runs Semgrep on the changed file and surfaces findings to the model. Implements SecureForge Appendix C (R.2.1). |
| `pre-tool-use-shell-audit.sh` | PreToolUse on Bash | Logs shell invocations to `~/.claude-harness/shell-audit.log`. Audit only, does not block. |
| `session-start.sh` | SessionStart | Runs drift check and Claude Code version check. Surfaces issues but does not block. |
| `pre-compact-preserve.sh` | PreCompact | Writes active phase state to a preservation file so context survives compaction. |

## Dependencies

Each hook requires:

`jq` for parsing the hook payload JSON. Install with `brew install jq` on macOS.

`semgrep` for the post-tool-use hook. The runtime hook uses a dedicated pipx environment pinned to a known version. Install it with `pipx install semgrep==1.162.0`. The hook prepends the pipx bin directory to PATH so a conda or Homebrew Python cannot shadow it. The post-generation pre-commit layer pins its own Semgrep mirror separately in `.pre-commit-config.yaml`. The two layers are independent and do not have to share a version.

`shellcheck` for the drift check verification. Install with `brew install shellcheck`.

If any dependency is missing, the relevant hook exits non-zero with a clear error message. The harness fails closed.

## Logs

All hooks write to `~/.claude-harness/`. The directory is created on first invocation.

`hook.log` is the canonical event log. Append-only. Each line is tab-separated: timestamp, severity, message.

`shell-audit.log` is the dedicated shell-audit log. Same format, separate file to keep shell history reviewable independently.

The logs are not rotated automatically. Set up `logrotate` if log volume becomes an issue.

## Adding new hooks

New hooks land in this directory with the same naming convention: `{event}-{purpose}.sh` for clarity.

Each new hook is registered in `harness/settings.json.template`.

Each new hook is referenced in this README's table and gets a Quality Contract trace in the script header comment.

Hook scripts pass `shellcheck` cleanly. The drift check verifies this at pre-commit.
