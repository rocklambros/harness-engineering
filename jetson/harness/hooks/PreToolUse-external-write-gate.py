#!/usr/bin/env python3
"""
Hook: PreToolUse-external-write-gate
Event: PreToolUse
Purpose: Ask for explicit confirmation on writes outside the working directory.

Threat: foundation/02-architectural-principles.md AP.11 (reversibility weights
        friction). Writes outside the working directory are not reversible
        from version control. Friction must match the reversibility class.

Decision: Mandatory deterministic enforcement of AP.11. Not threat-elected
          in Phase 2; the principle is foundation-level (applies to every phase),
          not threat-elected (per-phase). Matches the Phase 3 prompt's explicit
          mandatory-hook list.

Exemption: Four classes are exempt because AP.11's "not reversible from
           version control" rationale does not apply to them.

           Class 1: Claude Code's own managed, regenerable write stores. Written
           on most sessions, not project source, not irreversible. Gating them
           produces high-frequency prompts that train reflexive approval and
           erode the gate's signal for writes that matter. The class today:
             a. Auto-memory: Markdown files under
                ~/.claude/projects/<project>/memory/, for any project, not
                only the session's own. Operator decision, October 31,
                2026: cross-repo work writes a sibling project's memory as
                a matter of course. Markdown only, matching the scope of
                Claude Code's own protected-path exception for these
                directories, so a script dropped in a memory directory
                still asks. Residual risk: a memory file is read into that
                project's next session, so an injected write is a
                cross-session persistence path. Recorded in foundation/01
                under T.3.
             b. Plan files: ~/.claude/plans/...
           Both are judged on resolved paths so a symlink planted under
           plans/ or memory/ cannot carry the exemption into hooks/.
           Everything else under ~/.claude/ stays gated (settings.json, mcp.json,
           hooks/, skills/, agents/, CLAUDE.md, audited-hashes.json, etc.).
           Custom plansDirectory or autoMemoryDirectory overrides outside these
           default paths are not auto-detected; if you set them, extend
           is_claude_code_managed_store accordingly.

           Class 2: Scratch roots: /tmp, $TMPDIR, and on macOS the per-user
           temp directory that `getconf DARWIN_USER_TEMP_DIR` reports
           (/var/folders/<xx>/<hash>/T, which realpaths to /private/var/
           folders/.../T). World-writable or per-user scratch, cleaned by the
           OS, not under version control: the AP.11 "not reversible from
           version control" rationale does not apply. Operator decision,
           October 30, 2026: create, read, and update under /tmp and the
           per-user temp directory through the Read, Write, Edit, and
           NotebookEdit tools never prompt, in every mode including
           --dangerously-skip-permissions, where allow rules have no effect
           and this hook's "ask" is the one remaining prompt source for file
           tools. Deletes go through Bash and follow the permission mode;
           PreToolUse-bash-deny-rm-protected-paths.py lets the glob form of
           these same roots pass as scratch cleanup. The getconf lookup
           closes the gap that motivated the decision: when Claude Code
           starts without $TMPDIR in its environment (Desktop app, launchd,
           some IDE launchers) the per-user T/ tree was not recognized and
           every write there asked. An earlier revision of this decision
           exempted the whole of /private. Measured on October 30, 2026,
           that root also covered persistent per-user application state
           (/var/folders/.../0, C, X) and world-writable system directories
           (/var/db/mds, /var/db/DiagnosticsReporter, /var/OOPJit), none of
           which the scratch rationale fits, so the root was narrowed to the
           three scratch directories above. /var/tmp stays gated: it
           survives reboot, so the ephemeral rationale is weaker. Writes
           under a scratch root to a .git tree, to a pre-trust name
           (.claude, .mcp.json, .claude.json, CLAUDE.md, CLAUDE.local.md),
           or into ~/.claude or $CLAUDE_CONFIG_DIR are not exempt and fall
           through to the later classes. Those files load or run in the
           next session that opens the directory (foundation/01 Threat
           actors #3 and #5), and the scratchpad is where untrusted archives
           are unpacked. Detection realpaths both the candidate write target
           and each root before comparing, so macOS (/tmp -> /private/tmp,
           /var -> /private/var symlinks) and Linux/WSL2 (real directories)
           collapse to the same check. $TMPDIR is read from the hook's
           environment, which the operator controls. A root that resolves to
           /, to $HOME, or to any ancestor of $HOME is ignored so a bad
           value cannot widen the exemption to the whole disk. Trade-off:
           scratch directories are a known prompt-injection landing zone
           (drop a payload, race a setuid binary, plant a fake socket), so
           this widens the indirect-injection blast radius by the size of
           the per-user temp tree. The exemption stays a realpath prefix
           match, no glob.

           Class 3: Git worktrees of the repository containing cwd. A worktree
           shares the .git common dir with cwd, so writes to it are reversible
           through the same repository. The AP.11 rationale does not hold.
           Detection: enumerate `git worktree list --porcelain` from cwd once,
           realpath each worktree path, and check whether the candidate write
           target is at or under any of them. State-independent of the target
           path, so writes to not-yet-existing subdirectories of a worktree
           (the common case when Claude creates new files) still exempt
           correctly. Any subprocess or resolution failure falls through to
           ask (safe default). Same-repo worktrees are exempt in full,
           including their .claude/ and CLAUDE.md, because they share cwd's
           history and review path.

           Class 4: The working tree of any other git repository (other repos,
           their worktrees, submodules). A tracked file there is exactly as
           reversible as one inside cwd, so gating it only depends on where
           the session happened to start. Multi-repo sessions paid a prompt
           per write for no AP.11 benefit. Detection: realpath the
           target, walk up to the nearest existing directory, and ask
           `git rev-parse --show-toplevel` from there. Four carve-outs stay
           gated because a write there executes or loads code in some later
           session rather than changing reviewable source:
             a. Claude Code config roots (~/.claude and $CLAUDE_CONFIG_DIR).
                ~/.claude is commonly its own git repo, so without this
                carve-out the rule would exempt hooks/ and settings.json.
             b. Repositories rooted at / or at $HOME or any ancestor of it
                (a dotfiles repo would otherwise exempt the whole home dir).
             c. Anything under a .git path component (.git/hooks runs code on
                the next commit, .git/config can set core.hooksPath).
             d. Pre-trust config of the other repo: any .claude/ directory,
                .mcp.json, .claude.json, CLAUDE.md, or CLAUDE.local.md. These
                load or run in whatever session opens that repo
                (foundation/01 T.3 and T.5). Name matching is
                case-insensitive because the default macOS filesystem is.
             e. Trees whose contents this harness deploys or CI runs: any
                hooks/, rules/, agents/, skills/, or scripts/ component, and
                .github/workflows/. The harness's own hook sources live in
                another git repository on this disk, and the deploy script
                copies them into ~/.claude/hooks, so an unprompted edit there
                becomes an unprompted edit of the live gate at the next
                deploy. The same names are refused under scratch roots.
           Trade-off: an indirect prompt injection can now edit ordinary
           source in any repo on disk without a prompt. The edit surfaces as a
           git diff, which is only a control if someone reads it before
           committing. Gitignored and untracked files in those repos are
           covered too, same as inside cwd. GIT_* variables are stripped from
           the git subprocess environment so an inherited GIT_DIR or
           GIT_WORK_TREE cannot redirect repository discovery.

The working-directory check runs on resolved paths: a symlink inside the
working tree that points outside it (vendor/sdk -> ~/.claude/hooks) does not
carry the inside-cwd exemption to its target.

Verify (allow, inside cwd):
    echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"./local.txt\"},\"cwd\":\"$PWD\"}" | \
        python3 PreToolUse-external-write-gate.py
    # exit 0, empty stdout

Verify (ask, outside cwd):
    echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"/tmp/external.txt\"},\"cwd\":\"$PWD\"}" | \
        python3 PreToolUse-external-write-gate.py
    # exit 0, stdout: hookSpecificOutput with permissionDecision=ask

Verify (allow, any project's auto-memory Markdown):
    echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$HOME/.claude/projects/-Users-x-other-repo/memory/MEMORY.md\"},\"cwd\":\"$PWD\"}" | \
        python3 PreToolUse-external-write-gate.py
    # exit 0, empty stdout

Verify (ask, non-Markdown in an auto-memory directory):
    echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$HOME/.claude/projects/-Users-x-other-repo/memory/run.sh\"},\"cwd\":\"$PWD\"}" | \
        python3 PreToolUse-external-write-gate.py
    # exit 0, stdout: hookSpecificOutput with permissionDecision=ask

Verify (allow, plan file):
    echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$HOME/.claude/plans/foo.md\"},\"cwd\":\"$PWD\"}" | \
        python3 PreToolUse-external-write-gate.py
    # exit 0, empty stdout

Verify (allow, /tmp write):
    echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"/tmp/scratch.txt\"},\"cwd\":\"$PWD\"}" | \
        python3 PreToolUse-external-write-gate.py
    # exit 0, empty stdout (also passes for /private/tmp/scratch.txt on macOS)

Verify (ask, /var/tmp write):
    echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"/var/tmp/scratch.txt\"},\"cwd\":\"$PWD\"}" | \
        python3 PreToolUse-external-write-gate.py
    # exit 0, stdout: hookSpecificOutput with permissionDecision=ask

Verify (allow on macOS, per-user temp with $TMPDIR unset):
    echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$(getconf DARWIN_USER_TEMP_DIR)x.txt\"},\"cwd\":\"$PWD\"}" | \
        env -u TMPDIR python3 PreToolUse-external-write-gate.py
    # exit 0, empty stdout

Verify (ask, pre-trust name under a scratch root):
    echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"/tmp/clone/.claude/settings.json\"},\"cwd\":\"$PWD\"}" | \
        python3 PreToolUse-external-write-gate.py
    # exit 0, stdout: hookSpecificOutput with permissionDecision=ask

Verify (ask, /private outside the scratch roots):
    echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"/private/var/db/x.txt\"},\"cwd\":\"$PWD\"}" | \
        python3 PreToolUse-external-write-gate.py
    # exit 0, stdout: hookSpecificOutput with permissionDecision=ask

Verify (full matrix):
    python3 -I mac/harness/hooks/tests/test_external_write_gate.py \
        mac/harness/hooks/PreToolUse-external-write-gate.py

Verify (allow, sibling worktree of same repo):
    # In a repo with a worktree at ../sibling-wt added via `git worktree add`:
    echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"../sibling-wt/x.txt\"},\"cwd\":\"$PWD\"}" | \
        python3 PreToolUse-external-write-gate.py
    # exit 0, empty stdout

Verify (allow, $TMPDIR write):
    echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"${TMPDIR%/}/scratch.txt\"},\"cwd\":\"$PWD\"}" | \
        python3 PreToolUse-external-write-gate.py
    # exit 0, empty stdout

Verify (allow, file in an unrelated repo):
    # With another clone at ../other-repo:
    echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"../other-repo/src/new/x.py\"},\"cwd\":\"$PWD\"}" | \
        python3 PreToolUse-external-write-gate.py
    # exit 0, empty stdout

Verify (ask, pre-trust config in an unrelated repo):
    echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"../other-repo/.claude/settings.json\"},\"cwd\":\"$PWD\"}" | \
        python3 PreToolUse-external-write-gate.py
    # exit 0, stdout: hookSpecificOutput with permissionDecision=ask

Verify (ask, ~/.claude even when it is a git repo):
    echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$HOME/.claude/hooks/x.py\"},\"cwd\":\"$PWD\"}" | \
        python3 PreToolUse-external-write-gate.py
    # exit 0, stdout: hookSpecificOutput with permissionDecision=ask

Owner: harness-engineering (Phase 3, 2026-05-11; worktree exemption 2026-05-23;
       /tmp exemption 2026-05-25; any-repo and $TMPDIR exemptions 2026-09-26;
       per-user temp root, pre-trust guard, and fail-closed exits 2026-10-30)
"""

import json
import os
import subprocess
import sys

WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}

# git rev-parse is fast (<20 ms typical) but we cap it so a wedged git
# never blocks the gate. Failure-mode is fall-through to ask, not allow.
_GIT_TIMEOUT_SEC = 2

# Class 4 carve-out d: basenames that load or run code in whichever session
# opens the other repo. Compared lowercased (case-insensitive APFS).
_PRE_TRUST_NAMES = {
    ".claude",
    ".mcp.json",
    ".claude.json",
    "claude.md",
    "claude.local.md",
}
# Carve-out e: directory components whose contents this harness deploys or
# CI runs (hook sources, rule docs, agents, skills, deploy scripts, workflow
# definitions). A write there changes what a later session enforces.
_EXECUTABLE_TREES = {"hooks", "rules", "agents", "skills", "scripts", "workflows"}


def _loads_or_runs_later(path: str) -> bool:
    parts = path.split(os.sep)
    for idx, part in enumerate(parts):
        lowered = part.lower()
        if lowered == ".git" or lowered in _PRE_TRUST_NAMES:
            return True
        if lowered in _EXECUTABLE_TREES and (
            lowered != "workflows" or (idx > 0 and parts[idx - 1].lower() == ".github")
        ):
            return True
    return False


def _is_at_or_under(path: str, root: str) -> bool:
    return path == root or path.startswith(root.rstrip(os.sep) + os.sep)


def _is_home_or_ancestor(real_dir: str, home_real: str) -> bool:
    # A root this broad would turn a narrow exemption into the whole disk.
    return real_dir == os.sep or _is_at_or_under(home_real, real_dir)


def _scratch_roots() -> list:
    # Realpath each scratch root once at import. Resolves macOS /tmp ->
    # /private/tmp and /var -> /private/var so writes via either spelling hit
    # the same check. On Linux/WSL2 /tmp is a real directory and realpath is
    # a no-op. The per-user temp directory comes from getconf on macOS so
    # the exemption holds when $TMPDIR is absent from the environment. A
    # root that fails to resolve or resolves too broadly is dropped, and
    # writes there fall through to the later classes.
    home_real = os.path.realpath(os.path.expanduser("~"))
    candidates = ["/tmp", os.environ.get("TMPDIR", "")]
    if sys.platform == "darwin":
        try:
            out = subprocess.run(
                ["getconf", "DARWIN_USER_TEMP_DIR"],
                capture_output=True,
                text=True,
                timeout=1,
                check=True,
            ).stdout.strip()
            candidates.append(out)
        except (subprocess.SubprocessError, OSError):
            pass
    roots = []
    for candidate in candidates:
        if not candidate or not os.path.isabs(candidate):
            continue
        try:
            real = os.path.realpath(candidate)
        except OSError:
            continue
        if _is_home_or_ancestor(real, home_real) or real in roots:
            continue
        roots.append(real)
    return roots


_SCRATCH_ROOTS = _scratch_roots()


def _git(args: list, cwd: str):
    # Returns stdout, or None on any failure (caller falls through to ask).
    # GIT_* is stripped so an inherited GIT_DIR or GIT_WORK_TREE cannot
    # point discovery at a repo other than the one on disk at cwd.
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    try:
        result = subprocess.run(
            ["git", "-C", cwd, *args],
            capture_output=True,
            text=True,
            timeout=_GIT_TIMEOUT_SEC,
            check=True,
            env=env,
        )
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        return None
    return result.stdout


def extract_path(tool_input: dict) -> str:
    for key in ("file_path", "notebook_path", "path"):
        v = tool_input.get(key)
        if v:
            return v
    return ""


def is_in_repo_worktree(abs_path: str, abs_cwd: str) -> bool:
    # True iff abs_path is at or under any worktree of cwd's repo.
    # Single git call from cwd: works even when the candidate path's parent
    # does not exist yet (the common Write-new-file case that earlier
    # common-dir-comparison logic missed). Realpath on both sides defeats
    # symlink tricks that could otherwise spoof membership.
    if not os.path.isdir(abs_cwd):
        return False
    stdout = _git(["worktree", "list", "--porcelain"], abs_cwd)
    if stdout is None:
        return False
    try:
        real_target = os.path.realpath(abs_path)
    except OSError:
        return False
    for line in stdout.splitlines():
        if not line.startswith("worktree "):
            continue
        wt_raw = line[len("worktree ") :].strip()
        if not wt_raw:
            continue
        try:
            wt_real = os.path.realpath(wt_raw)
        except OSError:
            continue
        if real_target == wt_real or real_target.startswith(wt_real + os.sep):
            return True
    return False


def is_in_any_git_worktree(abs_path: str, home: str) -> bool:
    # Class 4. True iff abs_path is inside some git working tree and outside
    # every carve-out listed in the module header.
    try:
        real_target = os.path.realpath(abs_path)
        home_real = os.path.realpath(home)
        config_roots = [os.path.realpath(os.path.join(home, ".claude"))]
        if os.environ.get("CLAUDE_CONFIG_DIR"):
            config_roots.append(os.path.realpath(os.environ["CLAUDE_CONFIG_DIR"]))
    except OSError:
        return False
    if any(_is_at_or_under(real_target, root) for root in config_roots):
        return False
    # The target is usually a file that does not exist yet, often in a
    # directory that does not exist yet. Ask git from the nearest real parent.
    probe = real_target
    while not os.path.isdir(probe):
        parent = os.path.dirname(probe)
        if parent == probe:
            return False
        probe = parent
    stdout = _git(["rev-parse", "--show-toplevel"], probe)
    if not stdout or not stdout.strip():
        return False
    try:
        top_real = os.path.realpath(stdout.strip())
    except OSError:
        return False
    if _is_home_or_ancestor(top_real, home_real):
        return False
    if not _is_at_or_under(real_target, top_real) or real_target == top_real:
        return False
    if _loads_or_runs_later(os.path.relpath(real_target, top_real)):
        return False
    return True


def is_scratch_root(abs_path: str, home: str) -> bool:
    # True iff abs_path is at or under a realpath'd scratch root and is not
    # a file that loads or runs in a later session. Realpath on the
    # candidate defeats symlink tricks that could otherwise spoof membership
    # (e.g. a symlink at /tmp/foo pointing to ~/.ssh). The pre-trust check
    # reuses the Class 4 carve-out names so a clone unpacked under /tmp gets
    # the same treatment as a clone anywhere else.
    if not _SCRATCH_ROOTS:
        return False
    try:
        real_target = os.path.realpath(abs_path)
        config_roots = [os.path.realpath(os.path.join(home, ".claude"))]
        if os.environ.get("CLAUDE_CONFIG_DIR"):
            config_roots.append(os.path.realpath(os.environ["CLAUDE_CONFIG_DIR"]))
    except OSError:
        return False
    if any(_is_at_or_under(real_target, root) for root in config_roots):
        return False
    if _loads_or_runs_later(real_target):
        return False
    return any(_is_at_or_under(real_target, root) for root in _SCRATCH_ROOTS)


def is_claude_code_managed_store(abs_path: str, home: str) -> bool:
    # Class: Claude Code's own managed, regenerable write stores. See the
    # Exemption note in the module header. Today: Markdown files in any
    # auto-memory directory under ~/.claude/projects/<project>/memory/, and
    # plan files under ~/.claude/plans/. Both are compared on resolved paths
    # so a planted symlink cannot carry the exemption elsewhere.
    #
    # Operator decision, October 31, 2026: any project's memory directory,
    # not only the current session's. Cross-repo work (the master's program
    # coursework, the cxbom repositories) writes memory for a sibling
    # project as a matter of course, and gating that produced a prompt on
    # ordinary work. The scoping that landed the day before is withdrawn.
    #
    # The exemption covers Markdown only, which is the same scope Claude
    # Code gives its own protected-path exception for these directories.
    # Memory files are Markdown, so the restriction costs nothing here, and
    # a script or a binary dropped into a memory directory still asks.
    claude_root = os.path.realpath(os.path.join(home, ".claude"))
    try:
        real = os.path.realpath(abs_path)
    except OSError:
        return False
    plans_root = os.path.join(claude_root, "plans")
    if _is_at_or_under(real, plans_root):
        return True
    projects_root = os.path.join(claude_root, "projects")
    if _is_at_or_under(real, projects_root) and real != projects_root:
        parts = os.path.relpath(real, projects_root).split(os.sep)
        # <project>/memory/<file>.md, at any depth below memory/.
        if (
            len(parts) >= 3
            and parts[1] == "memory"
            and parts[-1].lower().endswith(".md")
        ):
            return True
    return False


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        sys.stderr.write(
            f"PreToolUse-external-write-gate: payload is not JSON ({exc}). Blocked per AP.8.\n"
        )
        return 2
    if data.get("tool_name") not in WRITE_TOOLS:
        return 0
    tool_input = data.get("tool_input", {}) or {}
    raw_path = extract_path(tool_input)
    if not raw_path:
        return 0
    cwd = data.get("cwd") or os.getcwd()
    home = os.path.expanduser("~")
    abs_cwd = os.path.abspath(cwd)
    if os.path.isabs(raw_path):
        abs_path = os.path.abspath(raw_path)
    else:
        abs_path = os.path.abspath(os.path.join(abs_cwd, raw_path))
    # Inside cwd if the resolved target's common path with the resolved cwd
    # is cwd. Resolving both sides keeps a symlink planted inside the
    # working tree (vendor/sdk -> ~/.claude/hooks) from carrying the
    # exemption to wherever it points.
    try:
        real_cwd = os.path.realpath(abs_cwd)
        real_path = os.path.realpath(abs_path)
        common = os.path.commonpath([real_path, real_cwd])
    except (ValueError, OSError):
        # Cross-drive on Windows or unrelated paths.
        common = ""
    if common == real_cwd:
        return 0
    if is_claude_code_managed_store(abs_path, home):
        return 0
    if is_scratch_root(abs_path, home):
        return 0
    if is_in_repo_worktree(abs_path, abs_cwd):
        return 0
    if is_in_any_git_worktree(abs_path, home):
        return 0
    out = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": (
                f"Write target '{abs_path}' is outside the working directory "
                f"'{abs_cwd}'. AP.11 (reversibility) requires explicit "
                f"confirmation."
            ),
        }
    }
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001  fail closed per AP.8
        sys.stderr.write(
            f"PreToolUse-external-write-gate failed: {exc!r}. Blocked per AP.8.\n"
        )
        sys.exit(2)
