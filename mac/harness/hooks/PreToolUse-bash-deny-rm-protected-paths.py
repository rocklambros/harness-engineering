#!/usr/bin/env python3
"""
Hook: PreToolUse-bash-deny-rm-protected-paths
Event: PreToolUse
Purpose: Deny rm and rmdir invocations whose target is a protected path:
         the filesystem root, any direct child of it, the home directory,
         any per-user home under /Users or /home, the macOS real locations
         under /private, mounted volumes, the session's working directory
         and its ancestors, the Claude Code config root and the files that
         make it enforce anything, and the credential stores under home.
         Trailing-slash and glob forms of each count.

Threat: foundation/02-architectural-principles.md AP.11 (reversibility weights
        friction) and foundation/01-threat-model.md T.2 (prompt injection
        through agent inputs). A recursive rm against one of these paths is
        unrecoverable without a filesystem backup, and an injected
        instruction chooses its own target.

Decision: The bash-deny-rm-rf-root rule set was believed to cover root-
          prefixed paths through the `:*` suffix. Claude Code reads `:*` as
          a trailing space-wildcard, so `Bash(rm -rf /:*)` matches the bare
          `rm -rf /` and `rm -rf / x` and nothing else. Verified October 30,
          2026 on Claude Code 2.1.314: `rm -rf /tmp/<nonexistent>` and
          `rm -rf ~/<nonexistent>` both ran under the three rules. A Bash
          rule glob cannot say "this path but not its children", which is
          the distinction the harness needs (deny `rm -rf ~`, allow
          `rm -rf ~/proj/build`). That is a hook's job per AP.1. The rules
          stay as the deterministic floor for the bare spellings. This hook
          carries flag permutations, trailing slashes, globs, relative
          targets, cd-rebased targets, wrappers, and inline scripts.

          Claude Code has its own critical-path check for rm. It covers the
          root, every top-level directory, home, and the working directory
          with its parents, but it prompts (a two-minute countdown in a
          terminal under auto and bypassPermissions, a denial in the Desktop
          app unless a PermissionRequest hook allows) rather than denies, it
          does not cover /private/<name>, credential stores, or the config
          root, and its mounted-drive half can be switched off from the
          launch environment. The harness wants a deny that holds in every
          mode. What still relaxes this hook: a hook registration without
          `onFailure: "block"` (the harness sets it), `disableAllHooks` in a
          project settings file or `--settings`, `--bare` on a `-p` run
          (which skips hook discovery), and a mod that handles tool.check on
          a non-enterprise login.

Protected (after ~, ~user, $HOME, ${HOME} expansion, cd tracking,
relative-to-cwd resolution, /System/Volumes/Data prefix stripping, and
case folding on case-insensitive filesystems):
  /                        the root, also spelled /System/Volumes/Data
  /<name>                  any direct child of the root (/usr, /etc, /tmp,
                           /private, /Users, /home, ...)
  /private/<name>          the macOS real locations of /etc, /tmp, /var
  /Users/<name>            a per-user home on macOS
  /home/<name>             a per-user home on Linux
  $HOME                    the current home, whatever its path
  /Volumes/<drive>, /System/Volumes/<volume>, /media/<user>,
  /media/<user>/<drive>, /mnt/<name>, /run/media/<user>/<drive>
                           mounted volumes (a subset of the shapes Claude
                           Code's mounted-drive prompt lists)
  /mnt/<drive>/Users/<name>
                           a Windows profile seen from WSL2
  <cwd> and its ancestors  the session's working directory. Removing it
                           breaks the session and, at a repo root, deletes
                           the working tree with its unpushed commits. The
                           glob of an ancestor (`rm -rf ../*`, `../.*`)
                           denies too, since `../.*` reaches `../.git`.
  ~/.ssh ~/.gnupg ~/.aws/credentials ~/.aws/config ~/.kube/config
  ~/.config/gh ~/.config/gcloud ~/Library/Keychains
                           credential stores. Any rm under these denies,
                           recursive or not. A `cache` or `logs` directory
                           under one passes (`~/.aws/sso/cache`,
                           `~/.kube/cache` are routine resets).
  ~/.claude (or $CLAUDE_CONFIG_DIR), everything under it except the
  cleanup paths listed in CONFIG_CLEANUP_OK (plugin cache, project
  transcripts and memory, shell snapshots, logs, todos, statsig, debug,
  __pycache__), ~/.claude.json, and the directory this hook runs from
                           the files that make this harness enforce
                           anything or that record what the session
                           trusts. Any rm of these denies.
  <any of the above>/      trailing slash
  <any of the above>/*     glob wipe of the directory's contents, where the
                           glob is any last component containing * ? [ or {
                           (so ~/.*, ~/{*,.*}, and ~/?* all count)

A protected directory denies when the rm is recursive (-r, -R,
--recursive, including combined short flags such as -rf, -fr, -Rf, -rfv),
when the command is rmdir, or when the target is the glob form (a
non-recursive `rm -f ~/*` still deletes every regular file at the top of
a home). The glob form is the deepest non-glob ancestor: `~/*`, `~/.*`,
`~/**/*`, and `~/*/*` are all the glob form of home. A non-recursive rm
of a directory fails in the shell on its own. Credential stores and the
config files above deny on any rm, and so does a glob of a directory
that contains one (`~/Library/*` reaches Keychains). `unlink`, `shred`,
and `srm` are removers too. `mv` is judged on its sources, since moving
`~/.ssh` into scratch is worse than deleting it. `find` with `-delete`
or an `-exec rm` is judged on its start paths as a glob of each, so
`find . -name '*.pyc' -delete` passes and `find ~ -delete` denies. A
target that is an unresolved variable or a command substitution
(`$DIR/*`, `"${HOME%/}"`, `"$(echo ~)"`) denies when the rm is recursive
or a glob: the hook cannot see the value, and the one case it can,
`$TMPDIR`, `$PWD`, and a variable bound by `for X in <literals>` on the
same line, is resolved first.

Four deliberate exceptions. The glob form of a scratch root (/tmp,
/private/tmp, $TMPDIR, the per-user temp directory) passes, so
`rm -rf /tmp/*` and `rm -rf /tmp/*.log` are scratch cleanup, while
`rm -rf /tmp` (the directory itself) still denies. The glob form of the
session cwd itself passes (`rm -rf ./*` and `rm -rf *` in a build
directory empty it without removing it), while `rm -rf .` denies and the
glob of any ancestor denies. `git rm` is not rm: it touches the index and
tracked files, which the repository recovers, so `git rm -r --cached .`
passes. An rm that follows a remote or container program (ssh, docker,
podman, nerdctl, kubectl, oc, lima, limactl) runs on another filesystem
and passes. The scratch roots are the same set
PreToolUse-external-write-gate.py exempts.

Scope: children of protected paths are not gated. `rm -rf /tmp/build`,
`rm -rf ~/proj/node_modules`, and `rm -rf ~/.claude/plugins/cache/x` pass
through to the permission mode in force. Scoped cleanup is the everyday
case the harness must not tax.

Parsing: heredoc bodies are removed first so a document that quotes a
dangerous command (this file, the rule docs) can be written through a
heredoc. The command is split into simple commands on the chain operators
outside quotes, the contents of $(...) and backtick substitutions are
added as further segments, and each segment is tokenized with shlex. If
the quotes never balance the split is redone with quotes ignored, so a
stray apostrophe cannot hide a chained rm, `r''m` is seen as `rm`
because the check runs on tokens, `RM` and `/bin/RM` fold to `rm` on a
case-insensitive filesystem, and a brace list `{rm,-rf,~}` is expanded.
Every token position is inspected, so any wrapper (sudo, doas, env,
nice -n 5, timeout 10, caffeinate, setsid, ionice, command, exec,
/bin/rm) is seen through without an allowlist. `cd` and `pushd` segments
move the directory that later relative targets resolve against, `cd`
alone goes home, `cd -` goes back, a cd inside a parenthesized subshell
does not leak out, and a cd target the hook cannot resolve ($X,
backticks) makes any later `.`, `..`, or glob target deny. An inline
script passed to sh, bash, zsh, dash, or ksh with -c, a here-string into
a shell, a pipe into a shell (the previous segment's tokens are scanned
as scripts), an `eval` argument, an `alias` value, and the contents of
$(...), backtick, <(...), and >(...) substitutions (balanced, nested) are
scanned recursively. More than three levels of nesting denies. A `<<`
inside quotes or arithmetic is not a heredoc, and a heredoc with no
terminator is scanned rather than stripped. An `xargs` remover is judged
on the previous segment's tokens as globs. Out of scope: deletion by a
program this hook does not know (python, rsync --delete, git clean), and
an unquoted `echo rm -rf ~`, which denies as a false positive. The
Claude Code critical-path check and the OS are the backstops.

Failure handling: any exception, a payload that is not JSON, or an
unreadable cwd exits 2 with the reason on stderr, which Claude Code treats
as a block. The settings registration adds `"onFailure": "block"` (Claude
Code 2.1.295 or later) so a hook that cannot start blocks as well. Both
halves are needed: the exit code covers errors inside the script, the
registration covers errors before it. A deny also exits 2 rather than
printing a JSON decision: the permissions reference states that a
blocking hook takes precedence over allow rules, and exit 2 routes the
same way as a JSON deny. The registration also sets a 10 second timeout
so a hung mount cannot hold a tool call for the 600 second default.

Autonomous mode: HARNESS_AUTONOMOUS_MODE is ignored. This is a destructive-
class hook alongside external-write-gate, git-push-force, and
cached-prefix-write-gate.

Verify: tests/test_bash_deny_rm_protected_paths.py in this directory runs
the full matrix against the hook:
    python3 -I mac/harness/hooks/tests/test_bash_deny_rm_protected_paths.py \
        mac/harness/hooks/PreToolUse-bash-deny-rm-protected-paths.py

Spot checks:
    echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf ~/proj/build && rm -rf /tmp/x"},"cwd":"/Users/x/proj"}' | \
        python3 -I PreToolUse-bash-deny-rm-protected-paths.py
    # exit 0, empty stdout
    echo '{"tool_name":"Bash","tool_input":{"command":"cd .. && rm -rf *"},"cwd":"/Users/x/proj"}' | \
        python3 -I PreToolUse-bash-deny-rm-protected-paths.py
    # exit 2, stderr names the resolved target /Users/x

Owner: harness-engineering (October 30, 2026)
"""

import json
import os
import re
import shlex
import subprocess
import sys

REMOVERS = {"rm", "rmdir", "unlink", "shred", "srm"}
NON_RECURSIVE_REMOVERS = {"unlink", "shred", "srm"}
SHELLS = {"sh", "bash", "zsh", "dash", "ksh"}
CD_COMMANDS = {"cd", "pushd"}
# Programs after which a following rm runs on another filesystem.
REMOTE_PROGRAMS = {
    "ssh",
    "docker",
    "podman",
    "nerdctl",
    "kubectl",
    "oc",
    "lima",
    "limactl",
}
# Direct children of these are per-user homes, or for /private the real
# locations of /etc, /tmp, and /var on macOS. Compared case-blind everywhere.
HOME_PARENTS = {"users", "home", "private"}
CREDENTIAL_STORES = (
    ".ssh",
    ".gnupg",
    ".aws/credentials",
    ".aws/config",
    ".kube/config",
    ".config/gh",
    ".config/gcloud",
    "Library/Keychains",
)
_CREDENTIAL_PASS_COMPONENTS = {"cache", "logs"}
# Under the config root, only these are routine cleanup. Everything else
# loads, runs, or records trust.
CONFIG_CLEANUP_OK = (
    "plugins/cache",
    "projects",
    "shell-snapshots",
    "statsig",
    "todos",
    "logs",
    "debug",
)
_GLOB_CHARS = set("*?[{")
_DATA_VOLUME = "/System/Volumes/Data"
_MAX_DEPTH = 3
_ALWAYS_DENY = {"credential store", "config file", "config root"}
_FIND_DELETERS = {"-delete", "-exec", "-execdir", "-ok", "-okdir", "-fprint"}


def _is_wsl() -> bool:
    try:
        with open("/proc/version", encoding="utf-8") as f:
            return "microsoft" in f.read().lower()
    except OSError:
        return False


_CASE_FOLD = sys.platform in ("darwin", "win32", "cygwin") or _is_wsl()

# A heredoc operator and its terminator word, matched only at a position the
# quote-aware scanner has already judged to be outside quotes.
_HEREDOC_WORD = re.compile(r"<<-?\s*(?:'([^']*)'|\"([^\"]*)\"|([^\s;&|<>]+))")
_ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
_BRACE_LIST = re.compile(r"^\{([^{}]*,[^{}]*)\}$")
_VAR = re.compile(
    r"^\$(?:\{([A-Za-z_][A-Za-z0-9_]*)[^}]*\}|([A-Za-z_][A-Za-z0-9_]*))(.*)$"
)


def _fold(path: str) -> str:
    return path.lower() if _CASE_FOLD else path


def _same(a: str, b: str) -> bool:
    return _fold(a) == _fold(b)


def _at_or_under(path: str, root: str) -> bool:
    p, r = _fold(path), _fold(root).rstrip(os.sep)
    return p == r or p.startswith(r + os.sep)


def _realpath(path: str) -> str:
    try:
        return os.path.realpath(path)
    except OSError:
        return path


def _scratch_roots(home: str) -> list:
    # The same set PreToolUse-external-write-gate.py exempts: /tmp, $TMPDIR,
    # and on macOS the per-user temp directory from getconf, which does not
    # depend on $TMPDIR being set. A root that resolves to /, to home, or
    # to an ancestor of home is dropped so a bad value cannot widen the
    # glob exemption to the whole disk.
    home_real = _realpath(home)
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
        real = _realpath(candidate)
        if real == os.sep or _at_or_under(home_real, real) or real in roots:
            continue
        roots.append(real)
    return roots


def _find_heredoc(text: str):
    # Locate the first heredoc operator outside quotes. A << inside quotes
    # or directly after a digit or identifier (1<<3, $((x<<2))) is not a
    # heredoc. Returns (operator start, body start, terminator) or None.
    in_single = in_double = False
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == "\\" and not in_single and i + 1 < n:
            i += 2
            continue
        if c == "'" and not in_double:
            in_single = not in_single
        elif c == '"' and not in_single:
            in_double = not in_double
        elif (
            c == "<"
            and not in_single
            and not in_double
            and text.startswith("<<", i)
            and not text.startswith("<<<", i)
            and (i == 0 or text[i - 1] != "<")
            and (i == 0 or text[i - 1].isspace() or text[i - 1] in ";|&(")
        ):
            m = _HEREDOC_WORD.match(text, i)
            if m:
                return i, m.end(), (m.group(1) or m.group(2) or m.group(3) or "")
        i += 1
    return None


def _strip_heredocs(cmd: str) -> str:
    # Remove each heredoc body (and its operator) so quoted prose is never
    # mistaken for a command. A body whose terminator never appears is left
    # in place and scanned: that is deny-biased, and a real heredoc always
    # closes.
    out = cmd
    while True:
        found = _find_heredoc(out)
        if not found:
            return out
        op_start, op_end, term = found
        body_start = out.find("\n", op_end)
        if body_start < 0:
            out = out[:op_start] + " " + out[op_end:]
            continue
        pos = body_start + 1
        end = None
        while pos <= len(out):
            nl = out.find("\n", pos)
            line = out[pos:] if nl < 0 else out[pos:nl]
            if line.strip() == term:
                end = len(out) if nl < 0 else nl
                break
            if nl < 0:
                break
            pos = nl + 1
        if end is None:
            out = out[:op_start] + " " + out[op_end:]
            continue
        out = out[:op_start] + " " + out[end:]


def _substitutions(text: str) -> list:
    # Contents of $(...), <(...), >(...) with balanced parentheses, plus
    # backtick spans. Nested forms are returned at their outer level and
    # the recursive scan reaches the inner ones.
    found = []
    i, n = 0, len(text)
    while i < n:
        if text[i] == "`":
            j = text.find("`", i + 1)
            if j < 0:
                break
            found.append(text[i + 1 : j])
            i = j + 1
            continue
        if (
            text[i] in "$<>"
            and text.startswith("(", i + 1)
            and not text.startswith("((", i + 1)
        ):
            depth, j = 0, i + 1
            while j < n:
                if text[j] == "(":
                    depth += 1
                elif text[j] == ")":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            if j < n:
                found.append(text[i + 2 : j])
                i = j + 1
                continue
        i += 1
    return found


def _split_segments(cmd: str) -> list:
    # Split on chain operators outside quotes. If the quotes never balance,
    # the shell would reject the command or read it differently than this
    # scanner did, so the split is redone with quotes ignored. That keeps
    # the scanner deny-biased: a removal behind a stray apostrophe is seen.
    segments, balanced = _split_quoted(cmd, honor_quotes=True)
    if not balanced:
        segments, _ = _split_quoted(cmd, honor_quotes=False)
    return segments


def _split_quoted(cmd: str, honor_quotes: bool):
    # Mirrors the scanner in PreToolUse-bash-cap-subcommands. A lone & is a
    # background operator unless it belongs to a redirection (2>&1, &>).
    # Returns ([(segment, is_subshell, is_pipe_sink)], quotes_balanced).
    segments = []
    buf = []
    in_single = in_double = False
    pipe_sink = False
    i, n = 0, len(cmd)

    def flush(next_is_pipe: bool):
        nonlocal buf, pipe_sink
        segments.append(("".join(buf), pipe_sink))
        buf = []
        pipe_sink = next_is_pipe

    while i < n:
        c = cmd[i]
        if c == "\\" and not in_single and i + 1 < n:
            buf.append(c)
            buf.append(cmd[i + 1])
            i += 2
            continue
        if honor_quotes and c == "'" and not in_double:
            in_single = not in_single
        elif honor_quotes and c == '"' and not in_single:
            in_double = not in_double
        if not in_single and not in_double:
            if cmd.startswith("&&", i) or cmd.startswith("||", i):
                flush(False)
                i += 2
                continue
            if c == "|":
                flush(True)
                i += 1
                continue
            if c in ";\n":
                flush(False)
                i += 1
                continue
            if c == "&":
                prev_redirect = i > 0 and cmd[i - 1] in "<>"
                next_redirect = i + 1 < n and cmd[i + 1] == ">"
                if not prev_redirect and not next_redirect:
                    flush(False)
                    i += 1
                    continue
        buf.append(c)
        i += 1
    segments.append(("".join(buf), pipe_sink))
    cleaned = []
    for seg, sink in segments:
        subshell = seg.lstrip().startswith("(")
        text = seg.strip(" \t()")
        # A brace group `{ cmd; }` is delimiter noise. A brace list
        # `{rm,-rf,~}` is a token the tokenizer expands, so it keeps its
        # braces: only a `{` followed by whitespace and a `}` preceded by
        # whitespace or `;` are stripped.
        if text.startswith("{") and (len(text) == 1 or text[1].isspace()):
            text = text[1:].lstrip()
        if text.endswith("}") and (
            len(text) == 1 or text[-2].isspace() or text[-2] == ";"
        ):
            text = text[:-1].rstrip()
        text = text.strip(" \t")
        if text:
            cleaned.append((text, subshell, sink))
    return cleaned, not (in_single or in_double)


def _tokenize(segment: str) -> list:
    try:
        tokens = shlex.split(segment, posix=True)
    except ValueError:
        # Unbalanced quotes: fall back to whitespace so the check still runs.
        tokens = [t.strip("\"'") for t in segment.split()]
    expanded = []
    for tok in tokens:
        m = _BRACE_LIST.match(tok)
        if m:
            expanded.extend(part for part in m.group(1).split(",") if part)
        else:
            expanded.append(tok)
    # Leading VAR=value assignments are not the program.
    while expanded and _ASSIGNMENT.match(expanded[0]):
        expanded = expanded[1:]
    return expanded


def _prog(tok: str) -> str:
    return _fold(os.path.basename(tok))


class _State:
    # The directory later relative targets resolve against, plus the
    # variables a `for X in a b c` on the same line binds. cwd None means a
    # cd the hook could not resolve happened, which makes later `.`, `..`,
    # and glob targets deny.
    def __init__(self, cwd: str):
        self.cwd = cwd
        self.prev = None
        self.vars = {}

    def copy(self):
        d = _State(self.cwd)
        d.prev = self.prev
        d.vars = dict(self.vars)
        return d


def _expand(target: str, home: str) -> str:
    t = target
    if t == "~" or t.startswith("~/"):
        return home + t[1:]
    if t.startswith("~"):
        # ~user. Unknown accounts stay spelled with the tilde.
        return os.path.expanduser(t)
    for var in ("${HOME}", "$HOME"):
        if t == var or t.startswith(var + "/"):
            return home + t[len(var) :]
    return t


def _unresolvable(path: str) -> bool:
    return path.startswith("~") or "$" in path or "`" in path


def _apply_cd(tokens: list, where: _State, home: str) -> bool:
    if not tokens or _prog(tokens[0]) not in CD_COMMANDS:
        return False
    args = [a for a in tokens[1:] if not (a.startswith("-") and a != "-")]
    if not args:
        new = home
    elif args[0] == "-":
        new = where.prev if where.prev is not None else where.cwd
    else:
        t = _expand(args[0], home)
        if _unresolvable(t) or (where.cwd is None and not os.path.isabs(t)):
            new = None
        else:
            new = os.path.normpath(
                t if os.path.isabs(t) else os.path.join(where.cwd, t)
            )
    where.prev, where.cwd = where.cwd, new
    return True


def _expand_variables(raw: str, where: _State, ctx: dict):
    # Returns a list of candidate targets, or None when the value cannot be
    # known. $HOME, $TMPDIR, $PWD, and for-bound variables resolve; a
    # ${NAME%...} modifier is treated as $NAME since the modified value is
    # at most the whole; anything else, and any command substitution, is
    # unknown.
    if "`" in raw or "$(" in raw:
        return None
    m = _VAR.match(raw)
    if not m:
        return [raw]
    name = m.group(1) or m.group(2)
    rest = m.group(3)
    if name == "HOME":
        return [ctx["home"] + rest]
    if name == "PWD":
        return [ctx["session_cwd"] + rest]
    if name == "TMPDIR" and os.environ.get("TMPDIR"):
        return [os.environ["TMPDIR"].rstrip("/") + rest]
    if name in where.vars:
        return [v + rest for v in where.vars[name]]
    return None


def _normalize(target: str, where: _State, home: str):
    # Returns (path, is_glob). path is "~" for an unknown account's bare
    # home, None when the target is a child of an unknown account's home or
    # relative to an unresolved cwd (callers decide), else an absolute
    # normalized path. The glob form of a directory is the deepest
    # non-glob ancestor of a target that contains a glob character.
    if len(target) > 1 and target.endswith("/"):
        target = target.rstrip("/") or target
    t = _expand(target, home)
    if target.startswith("~") and target != "~" and not target.startswith("~/"):
        if "/" not in target:
            return ("~", False)
        if t.startswith("~"):
            return (None, False)
    is_glob = False
    if t in ("*", ".*"):
        is_glob, t = True, "."
    elif t not in ("/", ""):
        absolute = t.startswith("/")
        parts = [p for p in t.split("/") if p]
        kept = []
        for part in parts:
            if any(c in _GLOB_CHARS for c in part):
                is_glob = True
                break
            kept.append(part)
        if is_glob:
            t = ("/" if absolute else "") + "/".join(kept)
            if not t:
                t = "/" if absolute else "."
    if not os.path.isabs(t):
        if where.cwd is None:
            if (
                is_glob
                or t in (".", "..")
                or t.startswith("../")
                or t.startswith("./..")
            ):
                return ("<unresolved cwd>", True)
            return (None, False)
        t = os.path.join(where.cwd, t)
    t = "/" + t.lstrip("/")
    t = os.path.normpath(t)
    if _same(t, _DATA_VOLUME):
        t = "/"
    elif _at_or_under(t, _DATA_VOLUME):
        t = t[len(_DATA_VOLUME) :]
    return (t, is_glob)


def _protected_reason(path, is_glob, ctx):
    # Returns a short category string, or None when the path is not
    # protected. Categories in _ALWAYS_DENY deny on any rm.
    home, session_cwd, config_root = ctx["home"], ctx["session_cwd"], ctx["config_root"]
    if path == "~" or path == "<unresolved cwd>":
        return "home"
    if path is None:
        return None
    real = _realpath(path)
    if is_glob and any(_same(real, r) for r in ctx["scratch_roots"]):
        return None
    if path == "/":
        return "filesystem root"
    parts = path.strip("/").split("/")
    fp = [p.lower() for p in parts]
    for rel in CREDENTIAL_STORES:
        store = os.path.join(home, rel)
        if _at_or_under(path, store):
            if any(p.lower() in _CREDENTIAL_PASS_COMPONENTS for p in parts):
                break
            return "credential store"
        # Removing or globbing a directory that holds a credential file
        # (rm -rf ~/.aws, rm -rf ~/Library/*) reaches the credential. Home
        # itself is judged on its own below.
        if _at_or_under(store, path) and not _at_or_under(home, path):
            return "credential store"
    if _same(path, config_root):
        return "config root"
    if _at_or_under(path, config_root):
        rel = os.path.relpath(real, _realpath(config_root)) if real else ""
        relf = _fold(rel)
        if "__pycache__" in relf.split(os.sep):
            return None
        if any(
            relf == _fold(ok) or relf.startswith(_fold(ok) + os.sep)
            for ok in CONFIG_CLEANUP_OK
        ):
            return None
        return "config file"
    if _same(path, os.path.join(home, ".claude.json")) or _at_or_under(
        path, ctx["hook_dir"]
    ):
        return "config file"
    if len(parts) == 1:
        return "top-level directory"
    if len(parts) == 2 and fp[0] in HOME_PARENTS:
        return "home"
    if fp[0] == "mnt" and len(parts) == 4 and fp[2] == "users":
        return "home"
    if fp[0] == "volumes" and len(parts) == 2:
        return "mounted volume"
    if fp[:2] == ["system", "volumes"] and len(parts) <= 3:
        return "mounted volume"
    if fp[0] == "media" and len(parts) in (2, 3):
        return "mounted volume"
    if fp[0] == "mnt" and len(parts) == 2:
        return "mounted volume"
    if fp[:2] == ["run", "media"] and len(parts) in (3, 4):
        return "mounted volume"
    if _same(path, home) or _same(real, _realpath(home)):
        return "home"
    if _same(path, session_cwd):
        # The glob of cwd empties it and leaves it standing: routine
        # build cleanup. The directory itself is protected.
        return None if is_glob else "working directory"
    ancestor = os.path.dirname(session_cwd)
    while True:
        if _same(path, ancestor):
            return "working directory ancestor"
        parent = os.path.dirname(ancestor)
        if parent == ancestor:
            break
        ancestor = parent
    return None


def _judge_targets(
    targets: list, recursive: bool, where: _State, ctx: dict, force_glob: bool = False
):
    for raw in targets:
        candidates = _expand_variables(raw, where, ctx)
        if candidates is None:
            if recursive or force_glob or any(c in _GLOB_CHARS for c in raw):
                return (raw, "<unresolved variable>", "unresolved variable target")
            continue
        for cand in candidates:
            path, is_glob = _normalize(cand, where, ctx["home"])
            is_glob = is_glob or force_glob
            reason = _protected_reason(path, is_glob, ctx)
            if reason and (recursive or is_glob or reason in _ALWAYS_DENY):
                return (raw, path, reason)
    return None


def _split_options(args: list, recursive_flags: bool):
    recursive = False
    targets = []
    options_done = False
    for arg in args:
        if not options_done:
            if arg == "--":
                options_done = True
                continue
            if arg.startswith("--"):
                if recursive_flags and arg == "--recursive":
                    recursive = True
                continue
            if arg.startswith("-") and len(arg) > 1:
                if recursive_flags and ("r" in arg[1:] or "R" in arg[1:]):
                    recursive = True
                continue
        targets.append(arg)
    return recursive, targets


def _check_removal(args: list, prog: str, where: _State, ctx: dict):
    recursive, targets = _split_options(args, recursive_flags=True)
    if prog == "rmdir":
        recursive = True
    if prog in NON_RECURSIVE_REMOVERS:
        recursive = False
    return _judge_targets(targets, recursive, where, ctx)


def _check_move(args: list, where: _State, ctx: dict):
    _, operands = _split_options(args, recursive_flags=False)
    if len(operands) < 2:
        return None
    return _judge_targets(operands[:-1], True, where, ctx)


def _check_find(args: list, where: _State, ctx: dict):
    # Start paths come before the first predicate. A -delete or an -exec
    # that runs a remover makes each start path the glob form of itself.
    paths = []
    for arg in args:
        if arg.startswith("-") or arg in ("(", "!"):
            break
        paths.append(arg)
    deletes = "-delete" in args or "-fprint" in args
    for i, arg in enumerate(args):
        if (
            arg in ("-exec", "-execdir", "-ok", "-okdir")
            and i + 1 < len(args)
            and _prog(args[i + 1]) in REMOVERS
        ):
            deletes = True
    if not deletes:
        return None
    return _judge_targets(paths or ["."], True, where, ctx, force_glob=True)


def _check_tokens(
    tokens: list,
    where: _State,
    ctx: dict,
    depth: int,
    prev_tokens: list,
    pipe_sink: bool,
):
    if _apply_cd(tokens, where, ctx["home"]):
        return None
    if len(tokens) >= 3 and tokens[0] == "for" and tokens[2] == "in":
        where.vars[tokens[1]] = [
            t.rstrip(";") for t in tokens[3:] if t.rstrip(";") and t not in ("do", ";")
        ]
        return None
    if tokens and tokens[0] == "alias":
        for tok in tokens[1:]:
            if "=" in tok:
                hit = scan(tok.split("=", 1)[1], ctx, depth + 1, where.copy())
                if hit:
                    return hit
        return None
    remote = False
    for i, tok in enumerate(tokens):
        prog = _prog(tok)
        if prog in REMOTE_PROGRAMS:
            remote = True
            continue
        if prog == "eval":
            return scan(" ".join(tokens[i + 1 :]), ctx, depth + 1, where.copy())
        if prog in SHELLS:
            rest = tokens[i + 1 :]
            for j, t in enumerate(rest):
                is_c = t == "-c" or (
                    t.startswith("-") and not t.startswith("--") and "c" in t[1:]
                )
                if is_c and j + 1 < len(rest):
                    return scan(rest[j + 1], ctx, depth + 1, where.copy())
                if t == "<<<" and j + 1 < len(rest):
                    return scan(rest[j + 1], ctx, depth + 1, where.copy())
            # A shell reading its script from a pipe runs whatever the
            # previous segment printed. Scan that segment's tokens, each
            # on its own and all of them joined, so both `echo 'rm -rf ~'`
            # and `printf 'rm -rf %s' ~` are seen.
            if pipe_sink and not any(not t.startswith("-") for t in rest):
                for script in [*prev_tokens[1:], " ".join(prev_tokens[1:])]:
                    hit = scan(script, ctx, depth + 1, where.copy())
                    if hit:
                        return hit
            continue
        if prog == "xargs" and pipe_sink:
            sink = [_prog(t) for t in tokens[i + 1 :]]
            if any(s in REMOVERS for s in sink):
                hit = _judge_targets(prev_tokens[1:], True, where, ctx, force_glob=True)
                if hit:
                    return hit
            continue
        if prog == "mv" and not remote:
            hit = _check_move(tokens[i + 1 :], where, ctx)
            if hit:
                return hit
            continue
        if prog == "find" and not remote:
            hit = _check_find(tokens[i + 1 :], where, ctx)
            if hit:
                return hit
            continue
        if prog in REMOVERS:
            if remote or (i > 0 and _prog(tokens[i - 1]) == "git"):
                continue
            hit = _check_removal(tokens[i + 1 :], prog, where, ctx)
            if hit:
                return hit
    return None


def scan(cmd: str, ctx: dict, depth: int = 0, where: _State = None):
    # Returns (raw target, resolved path, reason) for the first protected
    # removal, or None.
    if depth > _MAX_DEPTH:
        return ("<nested>", "<nested>", "nesting beyond three levels")
    if where is None:
        where = _State(ctx["session_cwd"])
    cleaned = _strip_heredocs(cmd)
    segments = _split_segments(cleaned)
    for inner in _substitutions(cleaned):
        segments.extend((seg, True, sink) for seg, _, sink in _split_segments(inner))
    prev_tokens = []
    for segment, subshell, pipe_sink in segments:
        tokens = _tokenize(segment)
        hit = _check_tokens(
            tokens,
            where.copy() if subshell else where,
            ctx,
            depth,
            prev_tokens,
            pipe_sink,
        )
        if hit:
            return hit
        prev_tokens = tokens
    return None


def _block(reason: str) -> int:
    sys.stderr.write(reason + "\n")
    return 2


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        return _block(
            f"PreToolUse-bash-deny-rm-protected-paths: payload is not JSON ({exc}). Blocked per AP.8."
        )
    if data.get("tool_name") != "Bash":
        return 0
    cmd = (data.get("tool_input", {}) or {}).get("command", "")
    if not cmd:
        return 0
    home = os.path.abspath(os.path.expanduser("~"))
    config_root = os.path.abspath(
        os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(home, ".claude")
    )
    ctx = {
        "home": home,
        "session_cwd": os.path.abspath(data.get("cwd") or os.getcwd()),
        "config_root": config_root,
        "hook_dir": os.path.dirname(os.path.abspath(__file__)),
        "scratch_roots": _scratch_roots(home),
    }
    hit = scan(cmd, ctx)
    if not hit:
        return 0
    raw, path, reason = hit
    if reason.startswith("working directory"):
        advice = "Empty it with `rm -rf ./*` or run the removal from its parent, naming the directory."
    elif reason == "unresolved variable target":
        advice = "Spell the target as a literal path so the hook can judge it."
    else:
        advice = (
            "Scoped cleanup below a protected path passes: name the child path instead."
        )
    return _block(
        f"rm target '{raw}' resolves to '{path}', a protected path ({reason}). "
        f"Denied by PreToolUse-bash-deny-rm-protected-paths (AP.11 reversibility, "
        f"foundation/01 T.2, mac/harness/rules/bash-deny-rm-rf-root.md). {advice}"
    )


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001  fail closed per AP.8
        sys.exit(
            _block(
                f"PreToolUse-bash-deny-rm-protected-paths failed: {exc!r}. Blocked per AP.8."
            )
        )
