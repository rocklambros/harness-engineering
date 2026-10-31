# Hooks

The deterministic enforcement scripts that Claude Code invokes on specific events. Hooks are the highest-confidence policy enforcement surface in the harness. Per AP.1, anything that must not be bypassed lives here, not in CLAUDE.md.

Hooks fail closed per AP.8 where the registration says so, and nowhere else. Claude Code treats a hook that cannot start, times out, exits with a code other than 0 or 2, or prints invalid JSON as a non-blocking error unless the registration sets `onFailure: "block"`, a key that exists from 2.1.295. The five destructive-class hooks (`PreToolUse-external-write-gate.py`, `PreToolUse-cached-prefix-write-gate.py`, `PreToolUse-git-push-force-ask.py`, `PreToolUse-bash-deny-rm-protected-paths.py`, `ConfigChange-audit-claude-config.py`) carry that key, run under `python3 -I` so a planted module in the hooks directory or a `PYTHONPATH` entry cannot shadow the standard library, and the three newest also exit 2 on any internal error, so both halves of the failure surface block. The advisory and noisy hooks (shell audit, Semgrep feedback, subcommand cap, supply-chain checks, session-start audits, log pruning) fail open by design: a false positive there costs a re-run, while a stall there would wedge every tool call.

## Hooks in this directory

The table lists every hook the reference build registers plus the template-only shell hooks. Tests for the three newest hooks live in `tests/` and run with `python3 -I tests/<test>.py <hook>`.

| File | Event | Purpose |
| --- | --- | --- |
| `post-tool-use-semgrep.sh` | PostToolUse on Write, Edit, MultiEdit | Commit-time hardening. Runs Semgrep on the changed file and surfaces findings to the model. Implements SecureForge Appendix C (R.2.1). |
| `pre-tool-use-shell-audit.sh` | PreToolUse on Bash | Logs shell invocations to `~/.claude-harness/shell-audit.log`. Audit only, does not block. |
| `session-start.sh` | SessionStart | Runs drift check and Claude Code version check. Surfaces issues but does not block. |
| `pre-compact-preserve.sh` | PreCompact | Writes active phase state to a preservation file so context survives compaction. |
| `SessionStart-audit-plugin-updates.py` | SessionStart | Flags enabled plugins whose installed files differ from the reviewed baseline in `~/.claude/plugin-audit/`, with a file-level diff that lists code and instruction changes first. Flags, does not block, because plugins load before SessionStart hooks run. Record a reviewed baseline with `--acknowledge <plugin-id> --note "<review>"`. Traces to T.5 and T.7. |
| `PreToolUse-bash-cap-subcommands.py` | PreToolUse on Bash | Denies a Bash call with more than 30 chained subcommands (hard cap 49 under `HARNESS_AUTONOMOUS_MODE=1`), the Adversa.ai 2026 bypass class where per-subcommand deny checks stop firing above 50. Traces to T.4. |
| `PreToolUse-supply-chain-bash-checks.py` | PreToolUse on Bash | Asks on unpinned installs (`npx -y`, `@latest`, unpinned `pip install`, `uvx --from git+` without a ref) and `curl|sh` patterns. Silenced by `HARNESS_AUTONOMOUS_MODE=1` with a forensic log line. Traces to T.5. |
| `PreToolUse-git-push-force-ask.py` | PreToolUse on Bash | Asks on every `git push --force`, `-f`, or `--force-with-lease`. Destructive class: `onFailure: block`, runs under `python3 -I`, ignores the autonomous flag. Traces to AP.11. |
| `PreToolUse-bash-deny-rm-protected-paths.py` | PreToolUse on Bash | Denies `rm` and `rmdir` whose target resolves to the filesystem root, a top-level directory, a home, a mounted volume, the session cwd or an ancestor, a credential store, or the config files that make the harness enforce anything. Sees through wrappers, `cd` chains, globs at any depth including dot-globs, nested substitutions, here-strings, pipes into a shell, `eval`, `for` loops, and `sh -c`. Judges `mv` on its sources, `find -delete` on its start paths, and `unlink` and `shred` as removers. Glob forms of scratch roots and of cwd itself pass; `git rm` and an rm after a remote program pass. Destructive class: `onFailure: block`, `python3 -I`, exits 2 on any internal error. Rationale in `rules/bash-deny-rm-rf-root.md`. Traces to AP.11 and T.2. |
| `PreToolUse-external-write-gate.py` | PreToolUse on Write, Edit, MultiEdit, NotebookEdit | Asks on writes outside cwd except four exempt classes: Claude Code's own managed stores (any project's auto-memory Markdown, plans), scratch roots (`/tmp`, `$TMPDIR`, the per-user temp directory from `getconf`), worktrees of cwd's repo, and ordinary source in any other git working tree. Pre-trust names (`.claude`, `.mcp.json`, `CLAUDE.md`, `.git`) are never exempt. Destructive class: `onFailure: block`, `python3 -I`, exits 2 on error. Traces to AP.11, T.2, T.3. |
| `PreToolUse-cached-prefix-write-gate.py` | PreToolUse on Write, Edit, MultiEdit, NotebookEdit | Asks on writes to the cached-prefix set: any `CLAUDE.md` under cwd, `foundation/`, and the user-level `@import` targets in `~/.claude`. Destructive class: `onFailure: block`, `python3 -I`. Traces to T.3. |
| `SessionStart-audit-claude-config.py` | SessionStart | Flags a session whose in-repo `.claude/settings.json`, `.claude/settings.local.json`, or `.mcp.json` hash is not in `~/.claude/audited-hashes.json` and instructs the model to stop. A SessionStart hook cannot block, so the first load is a detective control. `ConfigChange-audit-claude-config.py` blocks the mid-session case. Traces to T.5 and T.7 (CVE-2025-59536 class). |
| `Stop-prune-session-logs.py` | Stop | Removes session transcripts older than 90 days from `~/.claude/projects/`. Traces to QC.4b. |
| `ConfigChange-audit-claude-config.py` | ConfigChange on project_settings and local_settings | Blocks an in-repo `.claude/settings.json` or `settings.local.json` change from taking effect until its sha256 is in `~/.claude/audited-hashes.json`, the same registry the SessionStart audit reads. Closes the mid-session `disableAllHooks: true` path. Logs each decision to `~/.claude/logs/config-change-gate.log` because Claude Code surfaces nothing for a blocked change. Destructive class: `onFailure: block`, `python3 -I`, exits 2 on error. Traces to T.3 and T.7. |

## Dependencies

Each hook requires:

`jq` for parsing the hook payload JSON. Install with `brew install jq` on macOS.

`semgrep` for the post-tool-use hook. The runtime hook uses a dedicated pipx environment pinned to a known version. Install it with `pipx install semgrep==1.162.0`. The hook prepends the pipx bin directory to PATH so a conda or Homebrew Python cannot shadow it. The post-generation pre-commit layer pins its own Semgrep mirror separately in `.pre-commit-config.yaml`. The two layers are independent and do not have to share a version.

`shellcheck` for the drift check verification. Install with `brew install shellcheck`.

If any dependency is missing, the relevant hook exits non-zero with a clear error message. Whether that blocks the action depends on the registration: the five destructive-class hooks block, the rest report and continue.

## Logs

All hooks write to `~/.claude-harness/`. The directory is created on first invocation.

`hook.log` is the canonical event log. Append-only. Each line is tab-separated: timestamp, severity, message.

`shell-audit.log` is the dedicated shell-audit log. Same format, separate file to keep shell history reviewable independently.

The logs are not rotated automatically. Set up `logrotate` if log volume becomes an issue.

## Adding new hooks

New hooks land in this directory with the same naming convention: `{event}-{purpose}.sh` for clarity.

Each new hook is registered in `mac/harness/settings.json` (the Mac reference build's source of truth, absolute `${CLAUDE_PROJECT_DIR}` paths) and in `settings.json.template` (what adopters and `scripts/deploy-harness.sh` render, `{{REPO_ROOT}}` paths). The reference file carries the harness hooks plus two MemPalace hooks personal to the Mac build. The template carries the harness hooks plus the four template-only shell hooks (`post-tool-use-semgrep.sh`, `pre-tool-use-shell-audit.sh`, `session-start.sh`, `pre-compact-preserve.sh`). The live `~/.claude/settings.json` on the reference host adds its own extras (attribution, backup, watermark, and security-reminder hooks) and is the system of record for that host. `scripts/check-hook-registrations.py`, drift check 6, proves the three agree and names the allowed extras. A destructive-class hook gets `"onFailure": "block"`, the exec form under `python3 -I`, and a 10 second timeout.

Each new hook is referenced in this README's table and gets a Quality Contract trace in the script header comment.

Hook scripts pass `shellcheck` cleanly. The drift check verifies this at pre-commit.
