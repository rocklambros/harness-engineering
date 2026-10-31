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
(`$DIR/*`, `"${HOME%/}"`, `"$(echo ~)"`, `./$X`, `$1`) denies when the rm
is recursive or a glob: the hook cannot see the value. `$HOME`, `$TMPDIR`
from the hook's environment, `$PWD` after cd tracking, and a variable
bound by `for X in <literals>` on the same line resolve, plain or with a
`:-` default (both values are judged). Any other modifier (`%`, `#`, `/`,
`:+`, `!`) can yield an unrelated path, an ancestor included, so it is
unresolved. A plain reference later in the word (`./$d`, `$S/$x`)
resolves the same way. In a flat command (no block, loop, or function),
a name assigned exactly once as its own statement with a literal value
(`S=/tmp/x`, `D=$S/run-$$`, `t=$(mktemp -d)`, a template only with
-t) binds where that statement
runs, so `S=/tmp/x; rm -rf $S/y` judges /tmp/x/y and a use before the
assignment stays unknown. `$CLAUDE_PROJECT_DIR` resolves from the hook's
environment like `$TMPDIR`. Any other name the command assigns, exports,
unsets, reads, or binds anywhere (`X=`, `unset X`, `read X`, `printf -v X`, `${X:=}`, `declare X`,
`for HOME in`) is unresolved for the whole command, and a rebound HOME
makes `~` judged both under the real home and under / (`~/x` with an
unknown HOME), unless its tail ends a protected path. `export
PATH="$HOME/bin:$PATH"` only reads HOME. `source`, `.`, or `eval` in
command position, outside quotes, can set any name, so every name is
unresolved in that command, and
`env -u X` unsets X for the program it runs. A non-recursive rm of an
unresolved target denies when its literal tail, placed under home or
under /, lands on a credential store or config file (`$X/.ssh/id_rsa`),
or when the command text spells a credential store or the config root
anywhere (`X=~/.ssh/*; rm -f $X`). Otherwise `rm -f "$tmp"` passes, and
so does `rm -f $X/settings.json`: the hook cannot tell which directory
the variable names.

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

Parsing: one lexer reads quotes, `$'...'`, escapes, and word-initial `#`
comments the way bash does, and every scanner below uses it. Heredoc
bodies are removed first so a document that quotes a
dangerous command (this file, the rule docs) can be written through a
heredoc. The delimiter is compared with its quotes and backslashes
removed, as bash compares it, and a << inside an open (( is a shift. A
body whose owning line feeds it to a shell, or to eval, source, or . in
command position (`bash <<EOF`, `cat <<EOF | sh`), is a script and is
scanned. The rest of
the operator line stays, so `cat <<EOF; rm -rf ~` is seen. The command is
split into simple commands on the chain operators outside quotes,
parentheses, and backticks. A `( ... )` group and each $(...), <(...),
>(...), or backtick body is scanned as a unit with its own copy of the
directory state, so `(cd /; rm -rf *)` judges `*` against `/`. More than
32 nested groups deny. A function, case arm, trap, coproc, select, eval,
source, ., or script on stdin makes the cwd and every name unknown from
that segment on. A trap action and the -c argument of script, su,
runuser, or flock are scanned as scripts, as is a <(...) handed to a
shell or source. xargs with a recursive remover denies unless its
targets come from a pipe the hook can read. A remote program (ssh,
docker) exempts what follows only in command position and, for a
container, without a bind mount, and a recursive remover inside a
container with a bind mount denies. `env -S` and `--split-string`
arguments are scanned as command lines. A heredoc written to a file that
a shell, source, or . later runs in the same command is scanned. xargs
input is read from echo and printf arguments, or as globs of find and ls
start paths. A command over 512 KB or 200 heredocs denies outright. Each segment is tokenized with shlex. If
the quotes never balance the split is redone with quotes ignored, so a
stray apostrophe cannot hide a chained rm, `r''m` is seen as `rm`
because the check runs on tokens, `RM` and `/bin/RM` fold to `rm` on a
case-insensitive filesystem, and a brace list `{rm,-rf,~}` is expanded.
Every token position is inspected, so any wrapper (sudo, doas, env,
nice -n 5, timeout 10, caffeinate, setsid, ionice, command, exec,
/bin/rm) is seen through without an allowlist. `cd` and `pushd` segments
move the directory that later relative targets resolve against, `cd`
alone goes home, `cd -` goes back, a cd inside a parenthesized subshell
does not leak out, and `builtin cd` and `command cd` count as cd. A cd
the hook cannot resolve ($X, backticks, a rebound HOME, a relative target
under CDPATH, `popd`, or a cd after `if`, `then`, `while`, or `!` whose
effect is conditional) makes any later `.`, `..`, or glob target deny,
and a recursive relative target named like a real top-level directory
(`usr`) deny. `~+`, `~-`, and `~N` are unresolved. An inline
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
SHELLS = {"sh", "bash", "zsh", "dash", "ksh", "mksh", "ash", "yash", "posh"}
SHELLS |= {"csh", "tcsh", "fish"}
# Programs that hand their -c argument to a shell: `script -qc 'cmd'`.
C_RUNNERS = {"script", "su", "runuser", "flock"}
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
_MAX_GROUPS = 32
_MAX_CANDIDATES = 256
_MAX_COMMAND = 512 * 1024
_MAX_HEREDOCS = 200
_XARGS_PRODUCERS = {"echo", "printf", "find", "ls"}
_RECURSIVE = re.compile(r"--recursive|-[A-Za-z]*[rR][A-Za-z]*")
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
_HEREDOC_WORD = re.compile(r"<<-?\s*((?:'[^']*'|\"[^\"]*\"|\\.|[^\s;&|<>'\"\\])+)")
_ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
_BRACE_LIST = re.compile(r"^\{([^{}]*,[^{}]*)\}$")
_VAR = re.compile(
    r"^\$(?:\{([A-Za-z_][A-Za-z0-9_]*)([^}]*)\}|([A-Za-z_][A-Za-z0-9_]*))(.*)$"
)
# Ways a command gives a name a value the hook cannot follow. Matched over
# the raw text and over each segment's unquoted tokens (`export T""MPDIR=~`)
# at every nesting level, so a match inside a quoted string only costs a
# deny. Every pattern is linear: the hook has a 10 second budget.
_REBIND = re.compile(
    r"\b([A-Za-z_][A-Za-z0-9_]*)(?:\[[^\]\n]{0,64}\])?\+?="
    r"|\$\{([A-Za-z_][A-Za-z0-9_]*):?="
    r"|\bprintf\s+-v\s*([A-Za-z_][A-Za-z0-9_]*)"
    r"|\b(?:for|select)\s+(HOME|PWD|TMPDIR|CDPATH)\b"
    r"|\blet\s+([A-Za-z_][A-Za-z0-9_]*)"
    r"|\(\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?:[-+*/%&|^]|<<|>>)?=(?!=)"
)
_REBIND_CMD = re.compile(
    r"(?<![\w/.-])(?:unset|read|readarray|mapfile|getopts|export|declare|typeset"
    r"|local|readonly)\s([^;&|\n]*)"
)
_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_WRITTEN_NAME = re.compile(r"(?<![$\w{])[A-Za-z_][A-Za-z0-9_]*")
# `source`, `.`, and `eval` in command position can set any name, so every
# name counts as rebound. `env -u NAME` unsets one for the program it runs.
_CMD_POS = (
    r"(?:^|[;&|(!{\n]|\b(?:then|do|else|elif|if|while|until|builtin|command"
    r"|time|exec)\b)\s*"
)
_REBIND_SOURCE = re.compile(_CMD_POS + r"(?:source|\.|eval)\s")
# A name the hook cannot read: `export "$n=~"`, `printf -v "$n"`,
# `declare -n r=$n`.
_REBIND_ALL = re.compile(
    r"(?:^|[\s;&|(])[^\s=;&|()]*\$[^\s=;&|()]*="
    r"|\bprintf\s+(?:-\S+\s+)*-v\s*[\"']?\$"
    r"|\b(?:declare|typeset|local)\s[^;&|\n]*-\w*n\w*\s[^;&|\n]*\$"
)
# Constructs that can move the directory or set names where this scanner
# does not follow: functions, case arms, traps, coprocesses, select, eval,
# source, and a script read from stdin. Any of them makes the cwd and every
# name unknown from that segment on. _apply_cd handles the directory stack.
_OPAQUE = re.compile(
    _CMD_POS + r"(?:source|\.|eval|trap|coproc|select|case|function|alias)\s"
    r"|[A-Za-z_][\w-]*\s*\(\s*\)"
    r"|/dev/stdin|/dev/fd/"
)
_ENV_CALL = re.compile(r"\benv\s[^;&|\n]*")
_ENV_UNSET = re.compile(r"(?:^|\s)(?:-u|--unset)[=\s]?\s*([A-Za-z_][A-Za-z0-9_]*)")
# Leading words that do not change what a following cd does, and the
# subset that makes the cd conditional, so the hook cannot know whether
# the directory changed.
_CD_PREFIX = {"builtin", "command", "time", "!", "if", "then", "else", "elif"}
_CD_PREFIX |= {"do", "while", "until"}
_CD_CONDITIONAL = _CD_PREFIX - {"builtin", "command", "time"}


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


_ACTIVE, _QUOTED, _COMMENT = 0, 1, 2


def _lex(text: str):
    # Per-character state the way bash reads it: _ACTIVE syntax, _QUOTED
    # text (inside '...', "...", $'...', or after a backslash), or a
    # _COMMENT from a word-initial # to the end of the line. Every scanner
    # below reads this one view, so a `#` or a `$'\''` cannot make the hook
    # and bash disagree about where a quote ends. Returns (states,
    # quotes_balanced).
    n = len(text)
    states = [_QUOTED] * n
    quote = None
    i = 0
    while i < n:
        c = text[i]
        if quote == "'":
            quote = None if c == "'" else quote
            i += 1
            continue
        if quote == "$'":
            if c == "\\":
                i += 2
                continue
            quote = None if c == "'" else quote
            i += 1
            continue
        if c == "\\":
            i += 2
            continue
        if quote == '"':
            quote = None if c == '"' else quote
            i += 1
            continue
        if c == "'":
            ansi = i > 0 and text[i - 1] == "$" and states[i - 1] == _ACTIVE
            quote = "$'" if ansi else "'"
        elif c == '"':
            quote = '"'
        elif c == "#" and (
            i == 0 or (text[i - 1] in " \t\n;&|()" and states[i - 1] == _ACTIVE)
        ):
            j = text.find("\n", i)
            j = n if j < 0 else j
            states[i:j] = [_COMMENT] * (j - i)
            i = j
            continue
        else:
            states[i] = _ACTIVE
        i += 1
    return states, quote is None


def _in_arithmetic(text: str, i: int) -> bool:
    # `$(( 1 << X ))` shifts. An unclosed (( earlier on the line means the
    # << is arithmetic, and reading it as a heredoc would hide the lines
    # after it as a body.
    line = text[text.rfind("\n", 0, i) + 1 : i]
    return line.count("((") > line.count("))")


def _find_heredoc(text: str):
    # Locate the first heredoc operator in active syntax. A << inside
    # quotes or a comment, or directly after a digit or identifier (1<<3,
    # $((x<<2))), is not a heredoc. Returns (operator start, operator end,
    # terminator, strips_tabs) or None. The terminator is the delimiter
    # word with its quotes and backslashes removed, as bash compares it.
    states, _ = _lex(text)
    for i, c in enumerate(text):
        if (
            c == "<"
            and states[i] == _ACTIVE
            and text.startswith("<<", i)
            and not text.startswith("<<<", i)
            and (i == 0 or text[i - 1] != "<")
            and (i == 0 or text[i - 1].isspace() or text[i - 1] in ";|&(")
            and not _in_arithmetic(text, i)
        ):
            m = _HEREDOC_WORD.match(text, i)
            if m:
                word = m.group(1)
                term = re.sub(r"[\"'\\]", "", word)
                return i, m.end(), term, text.startswith("<<-", i)
    return None


_TRANSPARENT = {"sudo", "doas", "env", "nice", "nohup", "command", "exec", "time"}
_TRANSPARENT |= {"caffeinate", "setsid", "ionice", "stdbuf"}


def _is_remote(tokens: list, i: int) -> bool:
    # A remote or container program in command position runs what follows
    # on another filesystem. As an option argument (`sudo -g docker`,
    # `env -u ssh`) it is only a word, and a bind mount (`docker run -v
    # ~:/h`) puts this filesystem inside the container.
    prog = _prog(tokens[i])
    if prog not in REMOTE_PROGRAMS:
        return False
    prev = _prog(tokens[i - 1]) if i > 0 else None
    behind_timeout = i > 1 and _prog(tokens[i - 2]) == "timeout"
    if i > 0 and prev not in _TRANSPARENT and not behind_timeout:
        # `flock ssh rm -rf ~` locks a file named ssh and runs rm here.
        return False
    if prog in ("docker", "podman", "nerdctl"):
        mounts = ("-v", "--volume", "--mount")
        return not any(t.startswith(mounts) for t in tokens[i + 1 :])
    return True


def _feeds_shell(line: str) -> bool:
    # True when the line that owns a heredoc runs its body: `bash <<EOF`,
    # `cat <<EOF | sh`, `eval "$(cat <<EOF`. A remote program in command
    # position first (`ssh host bash <<EOF`) runs it on another filesystem.
    words = [w.strip("\"'") for w in re.split(r"[\s;&|()`$]+", line) if w]
    for i, word in enumerate(words):
        if _is_remote(words, i):
            return False
        if _prog(word) in SHELLS:
            return True
    # eval, source, and . only in command position: `git add . && git
    # commit -F - <<EOF` does not run its message.
    return _REBIND_SOURCE.search(_mask_quotes(line)) is not None


def _strip_heredocs(cmd: str, fed: list = None, written: dict = None) -> str:
    # Remove each heredoc body (and its operator) so quoted prose is never
    # mistaken for a command. A body whose terminator never appears is left
    # in place and scanned: that is deny-biased, and a real heredoc always
    # closes. A body the owning line feeds to a shell is a script, so it is
    # appended to `fed` for the caller to scan.
    out = cmd
    while True:
        found = _find_heredoc(out)
        if not found:
            return out
        op_start, op_end, term, strips_tabs = found
        body_start = out.find("\n", op_end)
        if body_start < 0:
            out = out[:op_start] + " " + out[op_end:]
            continue
        pos = body_start + 1
        end = None
        while pos <= len(out):
            nl = out.find("\n", pos)
            line = out[pos:] if nl < 0 else out[pos:nl]
            if (line.lstrip("\t") if strips_tabs else line) == term:
                end = len(out) if nl < 0 else nl
                break
            if nl < 0:
                break
            pos = nl + 1
        if end is None:
            out = out[:op_start] + " " + out[op_end:]
            continue
        line_start = out.rfind("\n", 0, op_start) + 1
        owner = out[line_start:body_start]
        if owner.rstrip().endswith(("|", "&&", "||", "\\")):
            # `cat <<EOF |` with `bash` on the line after the body.
            nxt = out.find("\n", end + 1)
            owner += " " + out[end + 1 : len(out) if nxt < 0 else nxt]
        if fed is not None and _feeds_shell(owner):
            fed.append(out[body_start + 1 : pos])
        elif written is not None:
            target = re.search(r">\s*([^\s;&|<>]+)", owner)
            if target:
                written[target.group(1).strip("\"'")] = out[body_start + 1 : pos]
        out = out[:op_start] + " " + out[op_end:body_start] + out[end:]


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


def _split_segments(cmd: str):
    # Split on chain operators outside quotes. If the quotes, parentheses,
    # or backticks never balance, the shell would reject the command or
    # read it differently than this scanner did, so the split is redone
    # with quotes ignored, and the caller treats the cwd and every name as
    # unknown. That keeps the scanner deny-biased: a removal behind a stray
    # apostrophe is seen and judged against no known directory. Returns
    # (segments, balanced).
    segments, balanced = _split_quoted(cmd, honor_quotes=True)
    if not balanced:
        segments, _ = _split_quoted(cmd, honor_quotes=False)
    return segments, balanced


def _split_quoted(cmd: str, honor_quotes: bool):
    # Mirrors the scanner in PreToolUse-bash-cap-subcommands. A lone & is a
    # background operator unless it belongs to a redirection (2>&1, &>).
    # With quotes honored, a separator inside ( ), $( ), or backticks does
    # not split, so a group keeps its own cd state: `(cd /; rm -rf *)` is
    # one segment that scan() judges as a unit. Returns
    # ([(segment, is_subshell, is_pipe_sink, raw)], balanced).
    n = len(cmd)
    if honor_quotes:
        states, balanced = _lex(cmd)
    else:
        states, balanced = [_ACTIVE] * n, True
    segments = []
    buf = []
    in_tick = False
    nest = 0
    pipe_sink = False

    def flush(next_is_pipe: bool, newline: bool = False):
        nonlocal buf, pipe_sink
        if newline and not "".join(buf).strip():
            # A blank line after `|` or `&&` continues the pipeline.
            return
        segments.append(("".join(buf), pipe_sink))
        buf = []
        pipe_sink = next_is_pipe

    i = 0
    while i < n:
        c = cmd[i]
        if states[i] == _COMMENT:
            i += 1
            continue
        if states[i] == _ACTIVE and honor_quotes:
            if c == "`":
                in_tick = not in_tick
            elif c == "(":
                nest += 1
            elif c == ")":
                # `case x in a)` closes nothing.
                nest = max(0, nest - 1)
        if states[i] == _ACTIVE and not in_tick and nest == 0:
            if cmd.startswith("&&", i) or cmd.startswith("||", i):
                flush(False)
                i += 2
                continue
            if c == "|":
                flush(True)
                i += 1
                continue
            if c in ";\n":
                flush(False, newline=c == "\n")
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
        text = _clean_segment(seg)
        if text:
            cleaned.append((text, seg.lstrip().startswith("("), sink, seg))
    return cleaned, balanced and not in_tick and not nest


def _clean_segment(seg: str) -> str:
    text = seg.strip(" \t()")
    # A brace group `{ cmd; }` is delimiter noise. A brace list
    # `{rm,-rf,~}` is a token the tokenizer expands, so it keeps its
    # braces: only a `{` followed by whitespace and a `}` preceded by
    # whitespace or `;` are stripped.
    if text.startswith("{") and (len(text) == 1 or text[1].isspace()):
        text = text[1:].lstrip()
    if text.endswith("}") and (len(text) == 1 or text[-2].isspace() or text[-2] == ";"):
        text = text[:-1].rstrip()
    return text.strip(" \t")


def _groups(raw: str):
    # Every `( ... )` group in the segment that is not a substitution
    # ($(, <(, >() or an array literal (a=( )), wherever it sits:
    # `(cd /; rm -rf *)`, `time -p ( ... )`, `coproc ( ... )`. Each runs in
    # a subshell, so its cd and removals share one state. Returns (bodies,
    # raw with the groups blanked) so the caller still judges the rest of
    # the segment and its substitutions.
    states, _ = _lex(raw)
    bodies, spans = [], []
    depth, start = 0, None
    for j, c in enumerate(raw):
        if states[j] != _ACTIVE:
            continue
        if c == "(":
            if depth == 0:
                start = None if j > 0 and raw[j - 1] in "$<>=" else j
            depth += 1
        elif c == ")" and depth:
            depth -= 1
            if depth == 0 and start is not None:
                if raw[start + 1 : j].strip():
                    bodies.append(raw[start + 1 : j])
                spans.append((start, j))
    rest = raw
    for s, e in reversed(spans):
        rest = rest[:s] + " " * (e - s + 1) + rest[e + 1 :]
    return bodies, rest


def _tokenize(segment: str) -> list:
    try:
        tokens = shlex.split(segment, posix=True)
    except ValueError:
        # Unbalanced quotes: fall back to whitespace so the check still runs.
        tokens = [t.strip("\"'") for t in segment.split()]
    expanded = []
    for tok in tokens:
        if "<<<" in tok[1:]:
            # `bash<<<'rm -rf ~'` is a shell reading a here-string.
            head, tail = tok.split("<<<", 1)
            expanded.extend([head, "<<<" + tail])
            continue
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


def _rebound(text: str) -> set:
    names = set()
    for m in _REBIND.finditer(text):
        names.update(g for g in m.groups() if g)
    for m in _REBIND_CMD.finditer(text):
        # `export PATH="$HOME/bin:$PATH"` writes PATH and only reads HOME.
        operand = m.group(1)
        names.update(_WRITTEN_NAME.findall(operand))
        if re.search(r"(?:^|\s)[\"']?\$", operand):
            names.add("*")
    for m in _ENV_CALL.finditer(text):
        names.update(_ENV_UNSET.findall(m.group(0)))
    if _REBIND_ALL.search(text) or _REBIND_SOURCE.search(_mask_quotes(text)):
        names.add("*")
    return names


def _mask_quotes(text: str) -> str:
    # Quoted text blanked, so `echo "the source of truth"` is not a source.
    states, _ = _lex(text)
    return "".join(c if st == _ACTIVE else " " for c, st in zip(text, states))


def _is_rebound(name: str, ctx: dict) -> bool:
    return name in ctx["rebound"] or "*" in ctx["rebound"]


# Anything in the command that can change what `git rev-parse
# --show-toplevel` answers when bash runs it.
_GIT_TAINT = (
    r"\bGIT_\w*=|\bgit\s+(?:-c\b|config\b|init\b)|core\.worktree|\bexport\s+GIT_"
)
_TOPLEVEL_SPELLINGS = {
    "$(git rev-parse --show-toplevel)",
    "`git rev-parse --show-toplevel`",
}


def _git_toplevel(cwd: str):
    # `cd "$(git rev-parse --show-toplevel)"` is how agents reach a repo
    # root. Asking git directly keeps it a known directory. GIT_* variables
    # are dropped so an inherited GIT_DIR cannot redirect the answer.
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    try:
        r = subprocess.run(
            ["git", "-C", cwd, "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=1,
            env=env,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    top = r.stdout.strip()
    return os.path.normpath(top) if r.returncode == 0 and os.path.isabs(top) else None


def _apply_cd(tokens: list, where: _State, ctx: dict) -> bool:
    i = 0
    while i < len(tokens) and (
        _prog(tokens[i]) in _CD_PREFIX or (i > 0 and tokens[i].startswith("-"))
    ):
        i += 1
    if i >= len(tokens) or _prog(tokens[i]) not in CD_COMMANDS | {"popd"}:
        return False
    home = ctx["home"]
    args = [a for a in tokens[i + 1 :] if not (a.startswith("-") and a != "-")]
    relative = bool(args) and not os.path.isabs(args[0]) and args[0] != "-"
    if any(_prog(t) in _CD_CONDITIONAL for t in tokens[:i]):
        # `if x; then cd /; fi` or `while cd /`: the hook cannot know
        # whether the directory changed.
        new = None
    elif (
        _prog(tokens[i]) == "popd"
        or (_prog(tokens[i]) == "pushd" and not args)
        or re.fullmatch(r"[-+]\d+", args[0] if args else "")
    ):
        # The directory stack is not tracked.
        new = None
    elif not args:
        new = None if _is_rebound("HOME", ctx) else home
    elif args[0] == "-":
        new = where.prev if where.prev is not None else where.cwd
    elif relative and (
        (_is_rebound("HOME", ctx) and args[0].startswith("~"))
        or _is_rebound("CDPATH", ctx)
        or (os.environ.get("CDPATH") and not args[0].startswith("."))
    ):
        # ~ follows the new HOME, and a relative cd searches CDPATH first.
        new = None
    elif (
        args[0] in _TOPLEVEL_SPELLINGS
        and where.cwd is not None
        and not ctx["git_tainted"]
    ):
        new = _git_toplevel(where.cwd)
    else:
        t = args[0]
        if "$" in t:
            # `S=/tmp/x; cd $S/f2` resolves through the same rules as an rm
            # target, and anything ambiguous stays unknown.
            cands = _expand_variables(t, where, ctx)
            t = cands[0] if cands and len(cands) == 1 else "$"
        t = _expand(t, home)
        if _unresolvable(t) or (where.cwd is None and not os.path.isabs(t)):
            new = None
        else:
            new = os.path.normpath(
                t if os.path.isabs(t) else os.path.join(where.cwd, t)
            )
    where.prev, where.cwd = where.cwd, new
    return True


def _var_values(name: str, where: _State, ctx: dict, bound: bool):
    # The values a name can hold at this point, or None when unknown. An
    # unset $TMPDIR is known: it expands to nothing.
    if name in ctx["literals"] and "*" not in ctx["rebound"]:
        # `S=/tmp/x; rm -rf $S/y`: bound where the assignment ran, unknown
        # before it.
        if not bound or name not in where.vars:
            return None
    elif _is_rebound(name, ctx):
        return None
    if bound and name in where.vars:
        values = []
        for v in where.vars[name]:
            sub = _expand_variables(v, where, ctx, bound=False)
            if sub is None:
                return None
            values.extend(sub)
        return values
    if name == "HOME":
        return [ctx["home"]]
    if name == "PWD":
        return None if where.cwd is None else [where.cwd]
    if name == "TMPDIR":
        return [os.environ.get("TMPDIR", "").rstrip("/")]
    if name == "CLAUDE_PROJECT_DIR" and os.environ.get(name):
        # Set by Claude Code for hooks, the same trust as $TMPDIR.
        return [os.environ[name].rstrip("/")]
    return None


def _expand_variables(raw: str, where: _State, ctx: dict, bound: bool = True):
    # Returns a list of candidate targets, or None when the value cannot be
    # known. A leading $NAME or ${NAME} resolves through _var_values, and
    # ${NAME:-word} or ${NAME-word} adds the literal word as a candidate.
    # Every other modifier can produce an unrelated path (${PWD%/*} is the
    # parent, ${X:+~} is home), so it is unknown, as is any `$` left after
    # the leading one ($1, $@, ${!X}, $'...', ./$X) and any substitution.
    if "`" in raw or "$(" in raw:
        return None
    m = _VAR.match(raw)
    if not m:
        candidates = [raw]
    else:
        name, modifier, rest = m.group(1) or m.group(3), m.group(2) or "", m.group(4)
        values = _var_values(name, where, ctx, bound)
        default = re.fullmatch(r":?-([^$]*)", modifier)
        if values is None or (modifier and not default and modifier not in ("?", ":?")):
            return None
        if default:
            values = [v for v in values if v] + [default.group(1)]
        candidates = [v + rest for v in values]
    resolved = []
    for cand in candidates:
        # Plain references later in the word: `./$d`, `red_$base`, `$S/$x`.
        more = _substitute_refs(cand, where, ctx, bound)
        if more is None or len(resolved) + len(more) > _MAX_CANDIDATES:
            return None
        resolved.extend(more)
    final = []
    for cand in resolved:
        if "$" in cand or "`" in cand:
            return None
        if re.match(r"~[-+0-9]", cand):
            # ~+ is $PWD, ~- is $OLDPWD, ~N is the directory stack.
            return None
        if _is_rebound("HOME", ctx) and (cand == "~" or cand.startswith("~/")):
            # The new HOME is unknown. `~/.cache/pip` is judged under the
            # real home and under /, and a tail that ends a protected path
            # (`~/rock/proj` with HOME=/home) stays unresolved.
            tail = os.path.normpath(cand[2:]) if cand != "~" else ""
            if tail in ("", ".") or tail.startswith(".."):
                return None
            if any(p.endswith("/" + tail) for p in ctx["protected_paths"]):
                return None
            final.extend([os.path.join(ctx["home"], tail), "/" + tail])
            continue
        final.append(cand)
    return final


_REF = re.compile(r"\$(?:\{([A-Za-z_][A-Za-z0-9_]*)\}|([A-Za-z_][A-Za-z0-9_]*))")


def _substitute_refs(cand: str, where: _State, ctx: dict, bound: bool):
    # Every plain $NAME or ${NAME} in the word replaced by each value it can
    # hold, or None when one is unknown. Anything else with a `$` is left
    # for the caller to treat as unresolved.
    outs = [cand]
    for _ in range(8):
        pending = [o for o in outs if _REF.search(o)]
        if not pending:
            return outs
        nxt = [o for o in outs if not _REF.search(o)]
        for o in pending:
            m = _REF.search(o)
            values = _var_values(m.group(1) or m.group(2), where, ctx, bound)
            if values is None:
                return None
            nxt.extend(o[: m.start()] + v + o[m.end() :] for v in values)
            if len(nxt) > _MAX_CANDIDATES:
                return None
        outs = nxt
    return None


def _names_protected(cmd: str, config_root: str) -> bool:
    # Whether the command, heredoc prose aside, spells a credential store or
    # the config root as a whole path component: `~/.ssh/*` counts,
    # `~/.claude-mem` and `known_hosts` do not.
    text = _strip_heredocs(cmd)
    names = (*CREDENTIAL_STORES, os.path.basename(config_root), ".claude.json")
    alts = "|".join(re.escape(n) for n in names)
    return (
        re.search(rf"(?:^|[\s/'\"=:~])(?:{alts})(?=$|[\s/'\";&|)*])", text) is not None
    )


# `NAME=value` as a whole statement. The value is literal text plus plain
# references ($NAME, ${NAME}) and the numeric $$, $RANDOM, and $BASHPID.
# A command substitution or backtick can print `../..`, so it never counts.
_LIT_REF = r"\$(?:\$|\{[A-Za-z_][A-Za-z0-9_]*\}|[A-Za-z_][A-Za-z0-9_]*)"
# `$(mktemp)`, `$(mktemp -d)`, or `$(mktemp -d -t name.XXXXXX)` always
# names a fresh path under the scratch root. -p and --tmpdir pick another
# directory, so they do not count.
_MKTEMP = (
    r"\$\(\s*mktemp(?:\s+-[dqu]+)*(?:\s+-[dqu]*t[dqu]*\s+[\w.-]*X{3,}[\w.-]*)?\s*\)"
)
_LIT_VALUE = (
    _MKTEMP + r"|\"" + _MKTEMP + r"\""
    r"|'[^'$`]*'"
    r"|\"(?:[^\"$`\\]|" + _LIT_REF + r")*\""
    r"|(?:[^\s;&|$`'\"()<>\\{}*?\[]|" + _LIT_REF + r")+"
)
_LIT_STMT = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)=(" + _LIT_VALUE + r")")
_LIT_ASSIGN = re.compile(
    r"(?:\A|[;\n])[ \t]*([A-Za-z_][A-Za-z0-9_]*)=(?:" + _LIT_VALUE + r")"
    r"[ \t]*(?=;|\n|&&|\Z)"
)
_NUMERIC_REF = re.compile(r"\$(?:\$|\{\$\}|RANDOM\b|\{RANDOM\}|BASHPID\b|\{BASHPID\})")
_BLOCK_WORDS = re.compile(
    r"\b(?:if|then|else|elif|while|until|for|do|case|select|function|coproc|let)\b"
    r"|(?<!\$)\(\("
    r"|\(\s*\)|(?<!\$)\{"
)
_SPECIAL_NAMES = {"HOME", "PWD", "OLDPWD", "TMPDIR", "CDPATH", "IFS", "PATH"}


def _literals(cmd: str) -> set:
    # Names a flat command (no block, loop, function, or heredoc) assigns
    # exactly once, as a statement of its own after the start, `;`, or a
    # newline, with a literal value. scan() binds each where its statement
    # runs, so `S=/tmp/x; rm -rf $S/y` judges /tmp/x/y and a use before
    # the assignment stays unknown.
    cmd = _strip_heredocs(cmd)
    if _BLOCK_WORDS.search(cmd):
        return set()
    names = set()
    for m in _LIT_ASSIGN.finditer(cmd):
        name = m.group(1)
        if name in _SPECIAL_NAMES:
            continue
        if cmd[: m.start()].rstrip().endswith(("&&", "||", "|", "\\")):
            # `true ||` then a newline: the assignment may never run.
            continue
        writes = re.findall(rf"(?<![\w$]){name}(?:\[[^\]\n]{{0,64}}\])?\+?=", cmd)
        others = _rebound(re.sub(rf"(?<![\w$]){name}=", " ", cmd))
        if len(writes) == 1 and name not in others and "*" not in others:
            names.add(name)
    return names


def _literal_tail(raw: str) -> str:
    # The text after the last expansion: `/.ssh/id_rsa` in `$X/.ssh/id_rsa`.
    cut = max(raw.rfind(c) for c in "$)}`")
    tail = raw[cut + 1 :]
    if raw[cut : cut + 1] == "$":
        tail = re.sub(r"^[A-Za-z0-9_@*#?!-]*", "", tail)
    return tail


def _tail_reason(tail: str, ctx: dict):
    # An unresolved prefix judged as home or the root. Catches
    # `$X/.ssh/id_rsa` and `${X}.claude.json` without denying `rm -f "$tmp"`.
    # Rooting the tail first drops a leading `..`, so `$X/../.ssh/id_rsa`
    # is judged as `.ssh/id_rsa` under each prefix.
    tail = os.path.normpath("/" + tail)
    for prefix in (ctx["home"], "/"):
        path = os.path.normpath(prefix + tail)
        reason = _protected_reason(path, False, ctx)
        if reason in _ALWAYS_DENY:
            return path, reason
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
            tail = _tail_reason(_literal_tail(raw), ctx)
            if tail:
                return (raw, tail[0], tail[1])
            if ctx["names_protected"]:
                # `X=~/.ssh/*; rm -f $X`: the value is out of sight, but the
                # command spells a credential store or the config root.
                return (raw, "<unresolved variable>", "unresolved variable target")
            continue
        for cand in candidates:
            path, is_glob = _normalize(cand, where, ctx["home"])
            is_glob = is_glob or force_glob
            if path is None and where.cwd is None and not cand.startswith("~"):
                # Relative to a cd the hook could not follow. `cd $X && rm
                # .ssh/id_rsa` reaches a key when $X is home.
                tail = _tail_reason(cand, ctx)
                if tail:
                    return (raw, tail[0], tail[1])
                # `HOME=/; cd; rm -rf usr`: the cwd may be the root, so a
                # recursive target named like a real top-level directory
                # denies. `cd $X && rm -rf build` still passes.
                first = os.path.normpath(cand).split("/", 1)[0]
                if (
                    (recursive or is_glob)
                    and first not in ("", ".", "..")
                    and (os.path.lexists(os.path.join(os.sep, first)))
                ):
                    return (raw, os.path.join(os.sep, first), "top-level directory")
                continue
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
    if _apply_cd(tokens, where, ctx):
        return None
    if len(tokens) >= 3 and tokens[0] == "for" and tokens[2] == "in":
        where.vars[tokens[1]] = [
            t.rstrip(";") for t in tokens[3:] if t.rstrip(";") and t not in ("do", ";")
        ]
        return None
    k = 0
    while k < len(tokens) and _prog(tokens[k]) in _CD_PREFIX:
        k += 1
    if k < len(tokens) and _prog(tokens[k]) == "trap":
        # `trap -- 'rm -rf ~' EXIT` runs its first operand later.
        ops = [t for t in tokens[k + 1 :] if t not in ("--", "-p", "-l")]
        return scan(ops[0], ctx, depth + 1, where.copy()) if ops else None
    if tokens and tokens[0] == "alias":
        for tok in tokens[1:]:
            if "=" in tok:
                hit = scan(tok.split("=", 1)[1], ctx, depth + 1, where.copy())
                if hit:
                    return hit
        return None
    remote = False
    mounted = False
    for i, tok in enumerate(tokens):
        if _prog(tok) == "env":
            # `env -S 'rm -rf ~'` splits one argument into a command line.
            for j, t in enumerate(tokens[i + 1 :], start=i + 1):
                script = None
                if t in ("-S", "--split-string") and j + 1 < len(tokens):
                    script = tokens[j + 1]
                elif t.startswith("--split-string="):
                    script = t.split("=", 1)[1]
                elif t.startswith("-S") and len(t) > 2:
                    script = t[2:]
                if script is not None:
                    hit = scan(script, ctx, depth + 1, where.copy())
                    if hit:
                        return hit
        if _prog(tok) in ("docker", "podman", "nerdctl") and any(
            t.startswith(("-v", "--volume", "--mount")) for t in tokens[i + 1 :]
        ):
            mounted = True
        if _prog(tok) in SHELLS | {"source", "."}:
            for t in tokens[i + 1 :]:
                body = ctx["written"].get(t)
                if body is not None:
                    # `cat > s <<EOF ... EOF; bash s` runs what it wrote.
                    hit = scan(body, ctx, depth + 1, where.copy())
                    if hit:
                        return hit
        prog = _prog(tok)
        if _is_remote(tokens, i):
            remote = True
            continue
        if prog == "eval":
            return scan(" ".join(tokens[i + 1 :]), ctx, depth + 1, where.copy())
        if prog in SHELLS or prog in C_RUNNERS:
            rest = tokens[i + 1 :]
            for j, t in enumerate(rest):
                is_c = t == "-c" or (
                    t.startswith("-") and not t.startswith("--") and "c" in t[1:]
                )
                if is_c and j + 1 < len(rest):
                    return scan(rest[j + 1], ctx, depth + 1, where.copy())
                if t == "<<<" and j + 1 < len(rest):
                    return scan(rest[j + 1], ctx, depth + 1, where.copy())
                if t.startswith("<<<") and len(t) > 3:
                    return scan(t[3:], ctx, depth + 1, where.copy())
            # A shell reading its script from a pipe runs whatever the
            # previous segment printed. Scan that segment's tokens, each
            # on its own and all of them joined, so both `echo 'rm -rf ~'`
            # and `printf 'rm -rf %s' ~` are seen.
            stdin = ("-", "/dev/stdin", "/dev/fd/0")
            if pipe_sink and all(t.startswith("-") or t in stdin for t in rest):
                for script in [*prev_tokens[1:], " ".join(prev_tokens[1:])]:
                    hit = scan(script, ctx, depth + 1, where.copy())
                    if hit:
                        return hit
            continue
        if prog == "xargs":
            after = tokens[i + 1 :]
            sink = [_prog(t) for t in after]
            if not any(s in REMOVERS for s in sink):
                continue
            from_file = any(
                t in ("-a", "--arg-file") or t.startswith("--arg-file=") for t in after
            )
            producer = _prog(prev_tokens[0]) if prev_tokens else ""
            if pipe_sink and not from_file and producer in _XARGS_PRODUCERS:
                # echo and printf print their arguments. find and ls print
                # paths under their start paths, judged as globs of them.
                args = prev_tokens[1:]
                if producer in ("find", "ls"):
                    args = [a for a in args if not a.startswith(("-", "(", "!"))]
                    args = args[:1] if producer == "find" else args
                    args = args or ["."]
                hit = _judge_targets(args, True, where, ctx, force_glob=True)
                if hit:
                    return hit
            elif any(_RECURSIVE.fullmatch(t) for t in after):
                # Targets read from a file, a redirect, or a heredoc are out
                # of sight, the same as an unresolved variable.
                return (
                    "<xargs input>",
                    "<unresolved variable>",
                    "unresolved variable target",
                )
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
            if mounted and (
                prog == "rmdir" or any(_RECURSIVE.fullmatch(t) for t in tokens[i + 1 :])
            ):
                # `docker run -v ~:/w alpine rm -rf /w` deletes a host path
                # under a name the hook cannot map back.
                return ("<container path>", "<bind mount>", "bind-mounted target")
            if remote or (i > 0 and _prog(tokens[i - 1]) == "git"):
                continue
            hit = _check_removal(tokens[i + 1 :], prog, where, ctx)
            if hit:
                return hit
    return None


def scan(cmd: str, ctx: dict, depth: int = 0, where: _State = None, groups: int = 0):
    # Returns (raw target, resolved path, reason) for the first protected
    # removal, or None. `groups` counts ( ) and $( ) nesting, which costs a
    # re-split per level, so a deep stack denies fast instead of running
    # into the 10 second timeout.
    if depth > _MAX_DEPTH:
        return ("<nested>", "<nested>", "nesting beyond three levels")
    if groups > _MAX_GROUPS:
        return ("<nested>", "<nested>", f"group nesting beyond {_MAX_GROUPS}")
    if where is None:
        where = _State(ctx["session_cwd"])
    fed = []
    cleaned = _strip_heredocs(cmd, fed, ctx["written"])
    ctx["rebound"] |= _rebound(cleaned)
    for body in fed:
        hit = scan(body, ctx, depth + 1, where.copy())
        if hit:
            return hit
    segments, balanced = _split_segments(cleaned)
    if not balanced:
        ctx["rebound"].add("*")
        where.cwd = None
    tokenized = [(_tokenize(seg), sub, sink, raw) for seg, sub, sink, raw in segments]
    for tokens, _, _, _ in tokenized:
        ctx["rebound"] |= _rebound(" ".join(tokens))
    prev_tokens = []
    for tokens, subshell, pipe_sink, raw in tokenized:
        lit = _LIT_STMT.fullmatch(raw.strip())
        if lit and lit.group(1) in ctx["literals"]:
            value = _NUMERIC_REF.sub("0", lit.group(2).strip("\"'"))
            scratch = os.environ.get("TMPDIR", "").rstrip("/") or "/tmp"
            minted = re.search(_MKTEMP, value) is not None
            value = re.sub(_MKTEMP, scratch + "/tmp.mktemp", value)
            values = _substitute_refs(value, where, ctx, True)
            if minted and _is_rebound("TMPDIR", ctx):
                values = None
            if values is not None and len(values) == 1:
                where.vars[lit.group(1)] = values
            prev_tokens = tokens
            continue
        # A ( ) group and each $( ), <( ), >( ), or backtick body run in a
        # subshell: they see the directory as it stands here, and a cd
        # inside them applies to their own later commands only.
        bodies, rest = _groups(raw)
        subs = _substitutions(rest)
        for inner in bodies + subs:
            hit = scan(inner, ctx, depth, where.copy(), groups + 1)
            if hit:
                return hit
        if {_prog(t) for t in tokens} & (SHELLS | {"source", "."}):
            # `bash <(echo 'rm -rf ~')`: the substitution prints a script.
            for inner in subs:
                printed = _tokenize(inner)[1:]
                for script in [*printed, " ".join(printed)]:
                    hit = scan(script, ctx, depth + 1, where.copy())
                    if hit:
                        return hit
        if bodies:
            tokens = _tokenize(_clean_segment(rest))
            subshell = False
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
        if _OPAQUE.search(_mask_quotes(raw)):
            # A function, case, trap, coproc, select, eval, source, ., the
            # directory stack, or a script on stdin can change the directory
            # and any name in ways this scanner does not model, from here on.
            ctx["rebound"].add("*")
            where.cwd = None
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
    if len(cmd) > _MAX_COMMAND or cmd.count("<<") > _MAX_HEREDOCS:
        # Parsing cost grows with these. Deny fast instead of running into
        # the 10 second timeout, which blocks too but says less.
        return _block(
            "PreToolUse-bash-deny-rm-protected-paths: command too large to judge "
            f"(over {_MAX_COMMAND} bytes or {_MAX_HEREDOCS} heredocs). Split it."
        )
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
        "rebound": set(),
        "names_protected": _names_protected(cmd, config_root),
        "literals": _literals(cmd),
        "written": {},
        "git_tainted": re.search(_GIT_TAINT, cmd) is not None,
    }
    ancestors, cur = [], ctx["session_cwd"]
    while True:
        ancestors.append(cur)
        if os.path.dirname(cur) == cur:
            break
        cur = os.path.dirname(cur)
    ctx["protected_paths"] = [
        *ancestors,
        home,
        config_root,
        *(os.path.join(home, c) for c in CREDENTIAL_STORES),
    ]
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
