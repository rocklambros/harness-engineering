# Harness Guide

The technical reference for the harness across all three platforms. Read this after you understand the foundation docs and have picked a platform section. For end-user quickstart and daily operation, see `USER_GUIDE.md`.

## What the harness is

A configured Claude Code environment that enforces a Quality Contract through five layers (project CLAUDE.md, settings.json, deterministic rules, advisory skills, hooks and agents) and a three-layer security stack (pre-generation guidance, commit-time hardening, post-generation validation).

The harness is built, not adopted. Each platform section reproduces the same capability surface using platform-appropriate tools. Cross-platform parity is the non-negotiable AP.3.

## The five layers

The architecture is documented in each platform's `ARCHITECTURE.md`. The shape is identical across platforms.

Layer 1 is the project-level CLAUDE.md (`{platform}/harness/CLAUDE.md`). Advisory. Under 200 lines. Seven sections: Role, code standards, security rules, core constraints, things that break, operational, status.

Layer 2 is `settings.json` (`{platform}/harness/settings.json.template`). Deterministic. Configures permission modes, hook registrations, and trust-boundary policy.

Layer 3 is the deterministic rules in `{platform}/harness/rules/`. Path deny lists, command deny lists, secret patterns. Consumed by hooks, not interpreted by Claude.

Layer 4 is the skills in `{platform}/harness/skills/`. Advisory but lazy-loaded. The `security-review` skill is the primary one. On the Mac reference build it is fully populated with ten pattern files matching its `SKILL.md` manifest. Jetson and Windows carry the scaffold with identical structure, pending hardware validation.

Layer 5 is the hooks and agents in `{platform}/harness/hooks/` and `{platform}/harness/agents/`. Hooks are deterministic. Agents are advisory and delegate-driven.

## The three-layer security stack

The security architecture cuts across Layers 4 and 5. Same composition on every platform.

**Layer 1 of the security stack** (pre-generation guidance) lives in `{platform}/harness/skills/security-review/`. Loads lazily based on file type. Content informed by the Arcanum-Sec sec-context taxonomy (CC BY 4.0, attribution preserved). Surfaces high-frequency anti-patterns before code is written.

**Layer 2 of the security stack** (commit-time hardening) lives in `{platform}/harness/hooks/post-tool-use-semgrep.sh`. Runs Semgrep on every Write or Edit and feeds findings back to Claude in the same session. Implements the SecureForge Appendix C pattern (MIT, Liu et al. 2026, arXiv:2605.08382). The paper measures a ~48% CWE-rate reduction from this layer alone.

**Layer 3 of the security stack** (post-generation validation) lives in `.pre-commit-config.yaml` at repo root. Same Semgrep tool, different invocation context. Supplemented by gitleaks for secrets, shellcheck for hook scripts, and the optional secondary scanners documented in each platform's `evaluations/deep-eval.md`.

Removing any of the three security layers weakens the others. The composition is binding per AP.2.

## Cross-platform tool equivalency

The capability is identical on every platform. The tool may differ.

| Capability | macOS | Jetson AGX Orin | Windows |
| --- | --- | --- | --- |
| SAST engine | Semgrep (native) | Semgrep (native) | Semgrep in WSL2 |
| Secret scanning | gitleaks (native) | gitleaks (native) | gitleaks in WSL2 |
| Shell linting | shellcheck (native) | shellcheck (native) | shellcheck in WSL2 |
| Hook scripts | bash | bash | bash in WSL2 |
| Python runtime | Homebrew-managed | Tegra Python | WSL2 Python |
| Package manager | Homebrew | apt + Jetson SDK | WSL2 apt + Chocolatey for Windows-native dependencies |

The WSL2 decision on Windows is documented in `windows/ARCHITECTURE.md` and pending hardware validation. The native Windows alternatives (Semgrep for Windows is incomplete on some rule packs as of build time) were evaluated and rejected for parity reasons.

## Build sequence

Every platform follows the same six-phase build sequence. Phase 0 establishes goals. Phases 1-5 build progressively from discovery to deterministic enforcement to advisory guidance to integration.

Phase 0 produces `phase-outputs/PHASE_0_GOALS.md`. Concrete success criteria, scope boundaries, out-of-scope decisions.

Phase 1 produces `phase-outputs/INVENTORY.md`, `CONFLICTS.md`, and `QUESTIONS.md`. Read-only discovery. Plan mode.

Phase 2 produces `phase-outputs/ANSWERS.md` and updates `ARCHITECTURE.md`. Architecture interview via `AskUserQuestion`. Last read-only phase.

Phase 3 produces the deterministic layer: `harness/CLAUDE.md`, `settings.json.template`, `rules/*`, `hooks/*`, and the wired pre-commit config. The PostToolUse Semgrep hook lands here.

Phase 4 produces the extension layer: `skills/*` (including `security-review` populated with pattern content), `agents/*`.

Phase 5 wires it all, runs the integration test, finalizes documentation, and produces the release commit. Uses the writer/reviewer subagent pattern.

The phase prompts in `{platform}/prompts/` are runnable Claude Code instructions. Each is self-contained and references the foundation docs and the relevant `ARCHITECTURE.md` section.

## Hook event coverage

The Mac reference build registers hooks on six Claude Code events. The adopter template `mac/harness/settings.json.template` and the Jetson template carry the same registrations with `{{REPO_ROOT}}` paths. Windows is a scaffold that registers none (see `windows/ARCHITECTURE.md`).

`PreToolUse` on Bash fires five hooks in order: `PreToolUse-bash-cap-subcommands.py` (deny above 30 chained subcommands), `PreToolUse-supply-chain-bash-checks.py` (ask on unpinned installs and `curl|sh`), `PreToolUse-git-push-force-ask.py` (ask on force pushes), `PreToolUse-bash-deny-rm-protected-paths.py` (deny recursive removal of protected paths), and on the Mac reference build `PreToolUse-no-ai-attribution.sh` (deny AI attribution in commit text). The template also runs `pre-tool-use-shell-audit.sh` first for audit logging.

`PreToolUse` on Write, Edit, MultiEdit, and NotebookEdit fires `PreToolUse-external-write-gate.py` (ask on writes outside the recoverable set) and `PreToolUse-cached-prefix-write-gate.py` (ask on writes to the cached-prefix files).

`PostToolUse` on Write, Edit, and MultiEdit fires `post-tool-use-semgrep.sh` for commit-time hardening.

`SessionStart` fires `session-start.sh` (drift check and version check), `SessionStart-audit-claude-config.py` (flag an unaudited in-repo settings or `.mcp.json` hash and instruct the session to stop), and `SessionStart-audit-plugin-updates.py` (flag plugin code that differs from its reviewed baseline).

`Stop` fires `Stop-prune-session-logs.py` (90-day transcript retention).

`PreCompact` fires `pre-compact-preserve.sh` to preserve active phase state across compaction.

`ConfigChange` on `project_settings` and `local_settings` fires `ConfigChange-audit-claude-config.py`, which blocks an in-repo settings change from taking effect until its hash is in the audited-hash registry. This is the event that can block, where SessionStart can only flag, so a `disableAllHooks: true` written into `.claude/settings.json` during a session never applies.

Coverage is informed by the Liu et al. reverse engineering of Claude Code v2.1.x (R.1.1), which enumerates 12-21 events depending on count method. The events registered here are the ones with explicit harness dependencies.

### Which hooks fail closed

Claude Code treats a hook that cannot start, times out, exits with a code other than 0 or 2, or prints invalid JSON as a non-blocking error: the action goes ahead unless the registration sets `"onFailure": "block"`, a key that exists from 2.1.295. The harness applies that flag to its five destructive-class hooks (the write gate, the cached-prefix gate, the force-push gate, the rm deny, and the ConfigChange audit), runs them in exec form under `python3 -I` with a 10 second timeout so nothing in the hooks directory or on `PYTHONPATH` can shadow the standard library and a hung mount cannot hold a call, and the three newest also exit 2 on any internal error. Drift check 6 (`scripts/check-hook-registrations.py`) proves every source registers the same harness hooks with these settings. Every other hook fails open on purpose. A stalled Semgrep run or a supply-chain false positive costs a re-run. A stalled destructive gate must cost a block. The version floor is recorded as `_claude_code_hook_onfailure_floor` in `settings.json` for the QC.5 re-evaluation on a minor bump.

## The deterministic gates

Two hooks and the permission rules decide, before any model judgment, which file writes and which removals need a human. Both hooks apply AP.11: friction scales with how hard the action is to undo.

### Writes: the external-write gate

A write inside the working directory passes. Outside it, the gate stays silent for four classes and asks for everything else.

Claude Code's own managed stores pass: Markdown files under `~/.claude/projects/<project>/memory/`, for any project rather than only the session's own, and plan files under `~/.claude/plans/`. They are regenerable and written on most sessions. Cross-repo work writes a sibling project's memory as a matter of course, which is the operator decision of October 31, 2026. The exemption is Markdown only, the same scope Claude Code gives its own protected-path exception there, so a script dropped into a memory directory still asks.

Scratch roots pass: `/tmp`, `$TMPDIR`, and on macOS the per-user temp directory that `getconf DARWIN_USER_TEMP_DIR` reports (`/var/folders/<xx>/<hash>/T`). The `getconf` lookup matters because a session launched from the Desktop app or launchd has no `$TMPDIR`. These directories are OS-cleaned and never under version control. `/var/tmp` is not a scratch root because it survives reboot. The whole of `/private` is not a scratch root either: it also holds persistent per-user application state and world-writable system directories, which an October 30, 2026 premortem measured before the exemption was narrowed.

Worktrees of the current repository pass in full, because they share the repository's history and review path.

Ordinary source in any other git working tree passes, because a tracked file there is as recoverable as one in the working directory.

Four things are never exempt, in any class: anything under a `.git` component, the pre-trust names `.claude`, `.mcp.json`, `.claude.json`, `CLAUDE.md`, and `CLAUDE.local.md`, the user-level config root `~/.claude` (or `$CLAUDE_CONFIG_DIR`) outside the managed stores, and repositories rooted at `/` or at home. Those paths load or run code in a later session, so a write there gets a prompt even under a scratch root.

The permission rules carry the scratch decision in the modes that honor allow rules (`Read` and `Edit` on `//tmp/**`, `//private/tmp/**`, and `//var/folders/*/*/T/**` in both spellings), and deny writes to `//etc/**`, `//private/etc/**`, `~/.ssh/**`, and the secret-file globs in every mode. Deny rules win over allow rules and over hook decisions.

### Removals: the rm protected-paths deny

A Bash rule can deny `rm -rf /` but cannot say "this directory but not its children", so the Bash side is a hook. `PreToolUse-bash-deny-rm-protected-paths.py` denies `rm` and `rmdir` whose target resolves to the filesystem root (also spelled `/System/Volumes/Data`), any top-level directory, any `/Users/<name>`, `/home/<name>`, or `/private/<name>`, `$HOME`, a mounted volume (`/Volumes/<drive>`, `/media/<user>`, `/mnt/<name>`, `/run/media/<user>/<drive>`), the session's working directory or any ancestor of it, a credential store under home (`.ssh`, `.gnupg`, `.aws`, `.kube`, `.config/gh`, `.config/gcloud`, `Library/Keychains`), or the parts of `~/.claude` that make the harness enforce anything. Trailing-slash and glob forms count, including dot-globs such as `~/.*`.

The hook resolves what it can know for certain and treats everything else as unresolved: `~`, `~user`, `$HOME`, `$TMPDIR` from its own environment, `$PWD` as tracked through `cd`, `pushd`, `builtin cd`, and `command cd`, a variable bound by `for X in <literals>` on the same line, a `${X:-word}` default, relative paths against the tracked cwd, and `( ... )` groups and substitutions with their own directory state, case-folded spellings on macOS and WSL2, wrappers in any position (`sudo`, `timeout`, `nice -n 5`, `/bin/rm`, `RM`), brace lists, nested `$(...)`, backtick, `<(...)` and `>(...)` substitutions, `eval`, `alias` values, here-strings, pipes into a shell, and `sh -c` scripts. A glob at any depth is the glob form of its deepest literal ancestor, so `~/**/*` is home. A name the command assigns, exports, unsets, reads, or binds anywhere is unresolved for the whole command, and `source`, `.`, or `eval` makes every name unresolved, because the shell would expand the new value and the hook cannot see it. Modifiers other than `:-` (`${X%/*}`, `${X:+~}`), positional and special parameters (`$1`, `"$@"`), `~+` and `~-`, and a `cd` whose effect is conditional or depends on `popd` or `CDPATH` are unresolved too. A recursive rm whose target is unresolved denies rather than guesses. A non-recursive one denies when its literal tail lands on a credential store or config file, or when the command spells one. `mv` is judged on its sources, `find` with `-delete` or `-exec rm` on its start paths, and `unlink` and `shred` count as removers. Heredoc bodies are stripped first, only where the operator sits outside quotes, so documentation that quotes a dangerous command can still be written. A body fed to a shell (`bash <<EOF`, `cat <<EOF | sh`) is a script and is scanned.

Four forms pass on purpose. The glob of a scratch root (`rm -rf /tmp/*`) is cleanup, while the root itself (`rm -rf /tmp`) denies. The glob of the session cwd itself (`rm -rf ./*` in a build directory) empties it, while `rm -rf .` and the glob of any ancestor (`rm -rf ../*`) deny. `git rm` touches the index, which the repository recovers. An rm after `ssh`, `docker`, `kubectl`, or `podman` runs on another filesystem. Children of protected paths pass to the permission mode: `rm -rf ~/proj/build` runs.

The rule layer keeps the bare spellings as a floor (`Bash(rm -rf /:*)`, `Bash(rm -rf ~)`, `Bash(rm -rf $HOME:*)`, `Bash(rm -rf /Users:*)`, and their variants) because a deny rule costs nothing and holds even if the hook is removed. The rationale and the full protected set are in `mac/harness/rules/bash-deny-rm-rf-root.md`.

Claude Code's own critical-path check still runs behind the hook. It prompts with a two-minute countdown in a terminal under `auto` and `bypassPermissions`, denies in the Desktop app unless a `PermissionRequest` hook allows, and covers the root, every top-level directory, home, and the working directory with its parents. The hook exists because a prompt is not a deny, because the native set does not include `/private/<name>`, credential stores, or the config root, because the native parser does not read `eval`, here-strings, or pipes into a shell, and because the native check applies to `rm` and `rmdir` only, so `mv`, `unlink`, `shred`, and `find -delete` have no native backstop.

### Unattended runs

Claude Code states that `--bare`, which skips hook discovery, will become the default for `-p` runs. A scheduled or scripted session that relied on auto-discovery would then start with no gates. `scripts/claude-unattended.sh` is the launcher for those runs: it checks `claude --version` against the fail-closed floor and the pinned minor range, confirms the settings file registers every destructive-class hook with `onFailure: block`, runs each gate once on empty input to prove the interpreter and the script start, and then executes `claude -p --settings ~/.claude/settings.json` with the arguments you passed. A precondition failure exits 2 before anything runs, which is the cheap failure. The expensive one, a dead gate blocking every call, is what the probe prevents.

```bash
scripts/claude-unattended.sh "Summarize the open issues" --permission-mode default
HARNESS_SETTINGS=/path/to/settings.json scripts/claude-unattended.sh "..."
```

### Rolling back a gate

A gate that misfires in an unattended run needs a path shorter than "edit the user settings by hand". On the Mac reference host the live `~/.claude` is a git repository with a backup remote, so the previous hook bodies and registrations are one checkout away:

```bash
git -C ~/.claude log --oneline -5 -- settings.json hooks/
git -C ~/.claude checkout <sha> -- settings.json hooks/PreToolUse-bash-deny-rm-protected-paths.py
```

To run one session with a single gate unregistered while keeping the other three, pass a settings override at launch rather than editing the file: `claude --settings '{"hooks":{"PreToolUse":[...]}}'` with the suspect entry left out. `disableAllHooks: true` is the wrong tool for this: it removes every control at once, including the audit hook. On the Mac, after any hook deploy, run `~/.claude/hooks/backup-config.sh` so the backup never lags the live gates.

On Jetson, `~/.claude` is not a git repository and `backup-config.sh` does not exist. Take a tar snapshot before each deploy and restore from it:

```bash
tar -czf ~/backups/claude-config-$(date +%F).tgz -C ~ .claude/settings.json .claude/hooks
tar -xzf ~/backups/claude-config-2026-10-30.tgz -C ~
```

### Testing the gates

The three gates ship with a committed matrix each under `mac/harness/hooks/tests/`. Each case pipes a real hook payload through the hook as a subprocess and checks the exit code and output, so the matrix exercises the entry point the runtime uses. Run them from the repo root after any change to a gate, and after a Claude Code minor bump. The Jetson copies under `jetson/harness/hooks/tests/` are byte-identical and run the same way against the deployed hooks:

```bash
python3 -I mac/harness/hooks/tests/test_external_write_gate.py mac/harness/hooks/PreToolUse-external-write-gate.py
python3 -I mac/harness/hooks/tests/test_bash_deny_rm_protected_paths.py mac/harness/hooks/PreToolUse-bash-deny-rm-protected-paths.py
python3 -I mac/harness/hooks/tests/test_configchange_audit_claude_config.py mac/harness/hooks/ConfigChange-audit-claude-config.py
```

## Versioning posture

The harness pins to a Claude Code minor-version range. The pinned range is documented in each platform's `harness/CLAUDE.md` status section.

Minor-version bumps trigger Quality Contract re-evaluation per QC.5:

The cache TTL behavior is re-checked. The March 2026 regression is the canonical example of why this matters.

Hook event coverage is verified against the current event list.

The SecureForge methodology is optionally re-run against representative workload to see whether the model's failure distribution has shifted enough to refresh the `security-review` skill.

Patch-version bumps do not trigger formal re-evaluation but are noted in the `JOURNEY.md` entry that covers the bump.

## How to update the harness

Updates are commits. Each commit follows the AP.5 template: phase or topic, Context, Decision, Why, Tradeoff.

The Why field cites the Quality Contract property or threat ID that justifies the change. The drift check verifies these citations resolve.

Cross-platform changes land as one commit when possible, with the rationale showing the equivalent change on each platform.

A change that affects only one platform is suspect and gets extra scrutiny per AP.3. Single-platform divergence requires an explicit rationale that survives review.

## Adopting the harness in a project

The harness ships in `{platform}/harness/`. To adopt it in a project:

Copy `{platform}/harness/` to the target project's repo root.

Copy the appropriate `settings.json.template` to `.claude/settings.json` and replace `{{REPO_ROOT}}` with the absolute path to the target project.

Copy `.pre-commit-config.yaml` and run `pre-commit install`.

Run the project's existing tests, then verify the wiring with `pre-commit run --all-files`, `./scripts/drift-check.sh`, and `shellcheck harness/hooks/*.sh`. These are the same checks `USER_GUIDE.md` Step 4 walks through.

The full adoption walkthrough is in `USER_GUIDE.md`.
