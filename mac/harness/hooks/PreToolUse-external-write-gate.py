#!/usr/bin/env python3
"""
Hook: PreToolUse-external-write-gate
Event: PreToolUse
Purpose: Ask for explicit confirmation on writes outside the working directory.

Threat: foundation/02-architectural-principles.md Principle 3 (reversibility-
        weighted risk). Writes outside the working directory are not reversible
        from version control. Friction must match the reversibility class.

Decision: Mandatory deterministic enforcement of Principle 3. Not threat-elected
          in Phase 2; the principle is foundation-level (applies to every phase),
          not threat-elected (per-phase). Matches the Phase 3 prompt's explicit
          mandatory-hook list.

Exemption: Two classes are exempt because Principle 3's "not reversible from
           version control" rationale does not apply to them.

           Class 1: Claude Code's own managed, regenerable write stores. Written
           on most sessions, not project source, not irreversible. Gating them
           produces high-frequency prompts that train reflexive approval and
           erode the gate's signal for writes that matter. The class today:
             a. Auto-memory: ~/.claude/projects/<encoded-cwd>/memory/...
             b. Plan files: ~/.claude/plans/...
           Everything else under ~/.claude/ stays gated (settings.json, mcp.json,
           hooks/, skills/, agents/, CLAUDE.md, audited-hashes.json, etc.).
           Custom plansDirectory or autoMemoryDirectory overrides outside these
           default paths are not auto-detected; if you set them, extend
           is_claude_code_managed_store accordingly.

           Class 2: The system ephemeral tmp directories: /tmp and the per-user
           $TMPDIR (macOS /var/folders/.../T/). World-writable or per-user
           scratch, cleaned by the OS, not under version control: the
           Principle 3 "not reversible from version control" rationale does
           not apply. Detection realpaths both the candidate write target and
           each tmp root before comparing, so macOS (/tmp -> /private/tmp,
           /var -> /private/var symlinks) and Linux/WSL2 (real directories)
           collapse to the same check. /var/tmp is intentionally NOT exempted:
           it survives reboot, so the ephemeral rationale is weaker, and
           writes there stay gated. $TMPDIR is read from the hook's
           environment, which the operator controls. A $TMPDIR that resolves
           to /, to $HOME, or to any ancestor of $HOME is ignored so a bad
           value cannot widen the exemption to the whole disk. Trade-off:
           tmp directories are a known prompt-injection landing zone (drop a
           payload, race a setuid binary, plant a fake socket), so this widens
           the indirect-injection blast radius. The exemption is scoped
           tightly (realpath prefix match, no glob) to keep the widening
           narrow.

           Class 3: Git worktrees of the repository containing cwd. A worktree
           shares the .git common dir with cwd, so writes to it are reversible
           through the same repository. The Principle 3 rationale does not hold.
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
           per write for no Principle 3 benefit. Detection: realpath the
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
                .mcp.json, CLAUDE.md, or CLAUDE.local.md. These load or run in
                whatever session opens that repo (foundation/01 Threat actors
                #3 and #5). Name matching is case-insensitive because the
                default macOS filesystem is.
           Trade-off: an indirect prompt injection can now edit ordinary
           source in any repo on disk without a prompt. The edit surfaces as a
           git diff, which is only a control if someone reads it before
           committing. Gitignored and untracked files in those repos are
           covered too, same as inside cwd. GIT_* variables are stripped from
           the git subprocess environment so an inherited GIT_DIR or
           GIT_WORK_TREE cannot redirect repository discovery.

Verify (allow, inside cwd):
    echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"./local.txt\"},\"cwd\":\"$PWD\"}" | \
        python3 PreToolUse-external-write-gate.py
    # exit 0, empty stdout

Verify (ask, outside cwd):
    echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"/tmp/external.txt\"},\"cwd\":\"$PWD\"}" | \
        python3 PreToolUse-external-write-gate.py
    # exit 0, stdout: hookSpecificOutput with permissionDecision=ask

Verify (allow, auto-memory store):
    echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$HOME/.claude/projects/x/memory/MEMORY.md\"},\"cwd\":\"$PWD\"}" | \
        python3 PreToolUse-external-write-gate.py
    # exit 0, empty stdout

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
       /tmp exemption 2026-05-25; any-repo and $TMPDIR exemptions 2026-09-26)
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
_PRE_TRUST_NAMES = {".claude", ".mcp.json", "claude.md", "claude.local.md"}


def _is_at_or_under(path: str, root: str) -> bool:
    return path == root or path.startswith(root.rstrip(os.sep) + os.sep)


def _is_home_or_ancestor(real_dir: str, home_real: str) -> bool:
    # A root this broad would turn a narrow exemption into the whole disk.
    return real_dir == os.sep or _is_at_or_under(home_real, real_dir)


def _tmp_roots() -> list:
    # Realpath each tmp root once at import. Resolves macOS /tmp ->
    # /private/tmp and /var -> /private/var so writes via either spelling hit
    # the same check. On Linux/WSL2 these are real directories and realpath
    # is a no-op. A root that fails to resolve or resolves too broadly is
    # dropped, and writes there fall through to ask.
    home_real = os.path.realpath(os.path.expanduser("~"))
    roots = []
    for candidate in ("/tmp", os.environ.get("TMPDIR", "")):
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


_TMP_ROOTS = _tmp_roots()


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
    rel_parts = os.path.relpath(real_target, top_real).split(os.sep)
    for part in rel_parts:
        lowered = part.lower()
        if lowered == ".git" or lowered in _PRE_TRUST_NAMES:
            return False
    return True


def is_ephemeral_tmp(abs_path: str) -> bool:
    # True iff abs_path is at or under a realpath'd tmp root (/tmp, $TMPDIR).
    # Realpath on the candidate defeats symlink tricks that could otherwise
    # spoof membership (e.g. a symlink at /tmp/foo pointing to /etc).
    # /var/tmp is intentionally NOT covered: it persists across reboots and
    # the ephemeral rationale does not hold there.
    if not _TMP_ROOTS:
        return False
    try:
        real_target = os.path.realpath(abs_path)
    except OSError:
        return False
    return any(_is_at_or_under(real_target, root) for root in _TMP_ROOTS)


def is_claude_code_managed_store(abs_path: str, home: str) -> bool:
    # Class: Claude Code's own managed, regenerable write stores. See the
    # Exemption note in the module header. Today: auto-memory under
    # ~/.claude/projects/<encoded-cwd>/memory/ and plan files under
    # ~/.claude/plans/. Everything else under ~/.claude/ stays gated.
    claude_root = os.path.join(home, ".claude")
    # Plan files: ~/.claude/plans/... (Claude Code default plansDirectory).
    plans_root = os.path.join(claude_root, "plans")
    if abs_path == plans_root or abs_path.startswith(plans_root + os.sep):
        return True
    # Auto-memory: ~/.claude/projects/<one-segment>/memory/...
    projects_root = os.path.join(claude_root, "projects")
    if abs_path.startswith(projects_root + os.sep):
        rel = os.path.relpath(abs_path, projects_root)
        parts = rel.split(os.sep)
        if len(parts) >= 2 and parts[1] == "memory":
            return True
    return False


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
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
    # Inside cwd if the common path with cwd equals cwd.
    try:
        common = os.path.commonpath([abs_path, abs_cwd])
    except ValueError:
        # Cross-drive on Windows or unrelated paths.
        common = ""
    if common == abs_cwd:
        return 0
    if is_claude_code_managed_store(abs_path, home):
        return 0
    if is_ephemeral_tmp(abs_path):
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
                f"'{abs_cwd}'. Principle 3 (reversibility) requires explicit "
                f"confirmation."
            ),
        }
    }
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
