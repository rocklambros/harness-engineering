#!/usr/bin/env python3
"""
Hook: SessionStart-audit-plugin-updates
Event: SessionStart
Purpose: Flag enabled Claude Code plugins whose installed files differ from
         the last reviewed baseline, so a marketplace auto-update or an
         in-place edit to plugin code never lands unnoticed.

Threat: foundation/01-threat-model.md T.5 (supply-chain compromise). Plugins
        auto-update from their marketplace, and their hooks, MCP servers, and
        scripts run with the operator's privileges. Also T.7 (silent
        capability change). SessionStart-audit-claude-config hashes
        settings.json, which stays byte-identical when plugin code changes.

Decision: Flag, do not block. SessionStart fires after plugins load, so an
          updated plugin's own hooks have already run once by the time this
          check reports. The value is detection within one session plus a
          file-level diff that makes review fast. Prevention needs
          marketplace auto-update turned off, which is an operator decision.
          A check that cannot block fails loud: any internal error surfaces
          as a visible warning instead of a silent pass (AP.8).

Baseline store (~/.claude/plugin-audit/):
    registry.json         plugin id to reviewed baseline summary
    manifests/<id>.json   relative path to file digest for that baseline
    stat-cache.json       absolute path to [size, mtime_ns, inode, sha256]

Registry entry format:
    "<plugin-id>": {
      "version": "<installed_plugins.json version at review>",
      "tree_sha256": "<sha256 over the sorted manifest>",
      "file_count": <int>,
      "audited_at": "YYYY-MM-DD",
      "auditor": "<username>",
      "note": "<what was reviewed>"
    }

The stat cache memoizes digests so steady-state checks read file metadata
instead of 770 MB of plugin payload. It is not authoritative. A file whose
size, mtime, or inode moved gets re-read and compared by content. An attacker
who can rewrite a plugin file and restore all three stat fields already holds
write access to ~/.claude, registry included, which this hook does not defend.

Scope: plugins enabled after merging enabledPlugins across user settings,
user local settings, project settings, and project local settings, in that
precedence order. Disabled plugins do not execute and wait until enabled.
Per-process .in_use markers, VCS metadata, and bytecode caches are excluded
because they change without any code change. Symlinks are recorded by target
path and never followed. A change to what a link's target file contains
outside the plugin tree is invisible here, so any link change gets listed
with code.

Usage:
    Hook mode reads the SessionStart payload on stdin:
        SessionStart-audit-plugin-updates.py
    Manual check, full hashing, exit 1 when anything is flagged:
        SessionStart-audit-plugin-updates.py --check
    Record a reviewed baseline:
        SessionStart-audit-plugin-updates.py --acknowledge <plugin-id> --note "<review>"
        SessionStart-audit-plugin-updates.py --acknowledge-enabled --note "<review>"

Verify (no plugins enabled, silent, exit 0):
    mkdir -p /tmp/pa-empty/.claude && echo '{}' > /tmp/pa-empty/.claude/settings.json
    echo '{"cwd":"/tmp/pa-empty"}' | \
        HOME=/tmp/pa-empty python3 SessionStart-audit-plugin-updates.py
    # exit 0, empty stdout

Verify (change flagged): under a temp HOME holding a fake installed plugin,
    run --acknowledge, edit one plugin file, then run --check. Expect exit 1
    and the edited file listed with an M prefix.

Owner: harness-engineering (post-launch revision, September 13, 2026)
Version: 1.0.0
"""

from __future__ import annotations

import argparse
import datetime
import getpass
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
import time
from pathlib import Path

CLAUDE_DIR = Path.home() / ".claude"
INSTALLED_PLUGINS = CLAUDE_DIR / "plugins" / "installed_plugins.json"
STORE_DIR = CLAUDE_DIR / "plugin-audit"
REGISTRY_PATH = STORE_DIR / "registry.json"
MANIFEST_DIR = STORE_DIR / "manifests"
STAT_CACHE_PATH = STORE_DIR / "stat-cache.json"

EXCLUDED_DIRS = frozenset({".in_use", ".git", "__pycache__"})
EXCLUDED_FILES = frozenset({".DS_Store"})

# Session start waits on this hook. An update that rewrites a 500 MB plugin
# would otherwise stall startup, so hashing stops here and the remaining
# changed files are reported as unverified.
HASH_BUDGET_SECONDS = 5.0

# Paths that change what executes or what the model gets told are listed
# ahead of payload churn so review starts where the risk sits.
CODE_DIRS = frozenset({"hooks", "bin", "scripts"})
CONFIG_NAMES = frozenset(
    {".mcp.json", ".lsp.json", "plugin.json", "hooks.json", "package.json"}
)
CODE_SUFFIXES = frozenset(
    {
        ".py",
        ".sh",
        ".bash",
        ".zsh",
        ".js",
        ".mjs",
        ".cjs",
        ".ts",
        ".cmd",
        ".ps1",
        ".rb",
        ".go",
        ".node",
        ".so",
        ".dylib",
        ".wasm",
        ".exe",
    }
)
INSTRUCTION_DIRS = frozenset({"agents", "commands", "skills", "output-styles"})
LIST_LIMIT = 8


class HashBudget:
    def __init__(self, seconds: float | None) -> None:
        self.deadline = None if seconds is None else time.monotonic() + seconds

    def exhausted(self) -> bool:
        return self.deadline is not None and time.monotonic() > self.deadline


def load_json(path: Path, default):
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def write_json_atomic(path: Path, data) -> None:
    # A torn registry or manifest would read as a changed baseline on the
    # next session, so writes go through a temp file and an atomic rename.
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=1, sort_keys=True)
            f.write("\n")
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def enabled_plugins(cwd: Path) -> list[str]:
    layers = [
        CLAUDE_DIR / "settings.json",
        CLAUDE_DIR / "settings.local.json",
        cwd / ".claude" / "settings.json",
        cwd / ".claude" / "settings.local.json",
    ]
    effective: dict[str, bool] = {}
    for layer in layers:
        data = load_json(layer, {})
        plugins = data.get("enabledPlugins") if isinstance(data, dict) else None
        if not isinstance(plugins, dict):
            continue
        for plugin_id, value in plugins.items():
            # Documentation arrays live beside the booleans in this map.
            if isinstance(value, bool):
                effective[plugin_id] = value
    return sorted(pid for pid, on in effective.items() if on)


def install_entries(installed: dict, plugin_id: str) -> list[dict]:
    entries = installed.get("plugins", {}).get(plugin_id, [])
    if isinstance(entries, dict):
        entries = [entries]
    return [e for e in entries if isinstance(e, dict) and e.get("installPath")]


def iter_tree(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        descend = []
        for name in dirnames:
            if name in EXCLUDED_DIRS:
                continue
            if os.path.islink(os.path.join(dirpath, name)):
                # A symlinked directory can point anywhere, so it is recorded
                # as a link entry and never followed.
                filenames.append(name)
            else:
                descend.append(name)
        dirnames[:] = descend
        for name in filenames:
            if name in EXCLUDED_FILES:
                continue
            full = os.path.join(dirpath, name)
            yield full, Path(os.path.relpath(full, root)).as_posix()


def scan_tree(
    root: Path, cache: dict, fresh_cache: dict, budget: HashBudget
) -> dict[str, str | None]:
    manifest: dict[str, str | None] = {}
    for full, rel in iter_tree(root):
        st = os.lstat(full)
        if stat.S_ISLNK(st.st_mode):
            target = os.readlink(full).encode("utf-8", "surrogateescape")
            manifest[rel] = "symlink:" + hashlib.sha256(target).hexdigest()
            continue
        if not stat.S_ISREG(st.st_mode):
            continue
        key = [st.st_size, st.st_mtime_ns, st.st_ino]
        cached = cache.get(full)
        if isinstance(cached, list) and len(cached) == 4 and cached[:3] == key:
            digest = cached[3]
        elif budget.exhausted():
            manifest[rel] = None
            continue
        else:
            digest = sha256_file(full)
        fresh_cache[full] = key + [digest]
        # The executable bit changes what a hook command can run, so it is
        # part of the recorded state alongside content.
        manifest[rel] = digest + (":x" if st.st_mode & 0o111 else "")
    return manifest


def tree_sha256(manifest: dict[str, str]) -> str:
    h = hashlib.sha256()
    for rel in sorted(manifest):
        h.update(f"{rel}\0{manifest[rel]}\n".encode("utf-8", "surrogateescape"))
    return h.hexdigest()


def manifest_path(plugin_id: str) -> Path:
    return MANIFEST_DIR / (re.sub(r"[^A-Za-z0-9._@+-]", "_", plugin_id) + ".json")


def classify(rel: str) -> str:
    parts = rel.split("/")
    name = parts[-1]
    if (
        parts[0] in CODE_DIRS
        or name in CONFIG_NAMES
        or Path(name).suffix.lower() in CODE_SUFFIXES
    ):
        return "code"
    if parts[0] in INSTRUCTION_DIRS or (len(parts) == 1 and name.endswith(".md")):
        return "instructions"
    return "other"


def check(cwd: Path, budget_seconds: float | None) -> list[dict]:
    installed = load_json(INSTALLED_PLUGINS, {})
    registry = load_json(REGISTRY_PATH, {})
    cache = load_json(STAT_CACHE_PATH, {})
    fresh_cache: dict = {}
    budget = HashBudget(budget_seconds)
    findings = []
    for plugin_id in enabled_plugins(cwd):
        for entry in install_entries(installed, plugin_id):
            root = Path(entry["installPath"])
            if not root.is_dir():
                continue
            current = scan_tree(root, cache, fresh_cache, budget)
            finding = {
                "id": plugin_id,
                "version": entry.get("version", "?"),
                "path": str(root),
            }
            baseline_entry = registry.get(plugin_id)
            if not isinstance(baseline_entry, dict):
                findings.append({**finding, "kind": "unreviewed"})
                continue
            finding["baseline_version"] = baseline_entry.get("version", "?")
            baseline = load_json(manifest_path(plugin_id), None)
            if not isinstance(baseline, dict) or tree_sha256(
                baseline
            ) != baseline_entry.get("tree_sha256"):
                findings.append({**finding, "kind": "baseline-mismatch"})
                continue
            added = sorted(set(current) - set(baseline))
            removed = sorted(set(baseline) - set(current))
            common = set(current) & set(baseline)
            modified = sorted(
                r
                for r in common
                if current[r] is not None and current[r] != baseline[r]
            )
            unverified = sorted(r for r in common if current[r] is None)
            # Only a link's target path is recorded, never the target's
            # content, so a link change can redirect what runs while every
            # hashed file stays identical. Link changes always get named.
            links = sorted(
                r
                for r in added + removed + modified
                if str(current.get(r) or baseline.get(r)).startswith("symlink:")
            )
            if added or removed or modified or unverified:
                findings.append(
                    {
                        **finding,
                        "kind": "changed",
                        "added": added,
                        "removed": removed,
                        "modified": modified,
                        "unverified": unverified,
                        "links": links,
                    }
                )
    if fresh_cache != cache:
        write_json_atomic(STAT_CACHE_PATH, fresh_cache)
    return findings


def format_findings(findings: list[dict]) -> str:
    hook = Path(__file__).resolve()
    lines = [
        "PLUGIN CODE CHANGED. Enabled plugins differ from their reviewed baseline "
        "(foundation/01 T.5 supply chain, T.7 silent capability change). Their "
        "hooks, MCP servers, and skills already loaded in this session.",
        "",
    ]
    for f in findings:
        head = f"  {f['id']} (installed {f['version']}"
        if "baseline_version" in f:
            head += f", reviewed {f['baseline_version']}"
        lines.append(head + ")")
        if f["kind"] == "unreviewed":
            lines.append("    no reviewed baseline on record")
            continue
        if f["kind"] == "baseline-mismatch":
            lines.append(
                "    baseline manifest missing or does not match its registry "
                "tree hash, so the stored baseline cannot be trusted"
            )
            continue
        buckets: dict[str, list[str]] = {"code": [], "instructions": [], "other": []}
        for prefix, key in (("M", "modified"), ("A", "added"), ("D", "removed")):
            for rel in f[key]:
                bucket = "code" if rel in f["links"] else classify(rel)
                buckets[bucket].append(f"{prefix} {rel}")
        for label, key in (
            ("code and config", "code"),
            ("instructions", "instructions"),
        ):
            items = buckets[key]
            if items:
                more = (
                    f", +{len(items) - LIST_LIMIT} more"
                    if len(items) > LIST_LIMIT
                    else ""
                )
                lines.append(f"    {label}: {', '.join(items[:LIST_LIMIT])}{more}")
        if buckets["other"]:
            lines.append(f"    other: {len(buckets['other'])} file(s) changed")
        if f["unverified"]:
            lines.append(
                f"    unverified: {len(f['unverified'])} file(s) changed on disk "
                "but were not re-hashed within the session-start budget. Run "
                "--check for a full comparison."
            )
        lines.append(f"    path: {f['path']}")
    lines += [
        "",
        "Review the listed files, then record the new baseline:",
        f'  python3 {hook} --acknowledge <plugin-id> --note "<what you reviewed>"',
    ]
    return "\n".join(lines)


def emit(system_message: str, context: str) -> None:
    print(
        json.dumps(
            {
                "systemMessage": system_message,
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": context,
                },
            }
        )
    )


def hook_main() -> int:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        payload = {}
    cwd_value = payload.get("cwd") if isinstance(payload, dict) else None
    cwd = Path(cwd_value or os.getcwd())
    try:
        findings = check(cwd, HASH_BUDGET_SECONDS)
    except Exception as exc:  # noqa: BLE001 - any failure must surface, not pass silently
        detail = f"{type(exc).__name__}: {exc}"
        emit(
            f"Plugin audit check failed ({detail}). Plugin code changes are unchecked this session.",
            f"PLUGIN AUDIT CHECK FAILED. {detail}. Plugin code changes were not "
            "checked this session. Tell the operator before relying on plugin behavior.",
        )
        return 0
    if findings:
        ids = ", ".join(sorted({f["id"] for f in findings}))
        emit(
            f"Plugin audit: {len(findings)} enabled plugin install(s) changed or "
            f"unreviewed: {ids}. Review before relying on them.",
            format_findings(findings),
        )
    return 0


def acknowledge(plugin_ids: list[str], note: str, auditor: str) -> int:
    installed = load_json(INSTALLED_PLUGINS, {})
    registry = load_json(REGISTRY_PATH, {})
    cache = load_json(STAT_CACHE_PATH, {})
    fresh_cache = dict(cache)
    today = datetime.date.today().isoformat()
    for plugin_id in plugin_ids:
        entries = [
            e
            for e in install_entries(installed, plugin_id)
            if Path(e["installPath"]).is_dir()
        ]
        if not entries:
            print(f"ERROR: {plugin_id} is not installed", file=sys.stderr)
            return 2
        manifests = [
            scan_tree(Path(e["installPath"]), cache, fresh_cache, HashBudget(None))
            for e in entries
        ]
        # One baseline per plugin id. Divergent installs of the same id would
        # make a single recorded baseline wrong for one of them.
        if any(m != manifests[0] for m in manifests[1:]):
            print(
                f"ERROR: {plugin_id} has installs with different contents. "
                "Resolve that before recording a baseline.",
                file=sys.stderr,
            )
            return 2
        manifest = manifests[0]
        tree = tree_sha256(manifest)
        write_json_atomic(manifest_path(plugin_id), manifest)
        registry[plugin_id] = {
            "version": entries[0].get("version", "?"),
            "tree_sha256": tree,
            "file_count": len(manifest),
            "audited_at": today,
            "auditor": auditor,
            "note": note,
        }
        print(
            f"recorded {plugin_id} {registry[plugin_id]['version']} "
            f"files={len(manifest)} tree={tree[:16]}"
        )
    write_json_atomic(REGISTRY_PATH, registry)
    write_json_atomic(STAT_CACHE_PATH, fresh_cache)
    return 0


def cli_main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--check", action="store_true", help="full comparison, exit 1 on findings"
    )
    mode.add_argument("--acknowledge", nargs="+", metavar="PLUGIN_ID")
    mode.add_argument("--acknowledge-enabled", action="store_true")
    parser.add_argument("--note", help="what was reviewed, required to acknowledge")
    parser.add_argument("--auditor", default=getpass.getuser())
    parser.add_argument(
        "--cwd", default=os.getcwd(), help="project dir for enabledPlugins"
    )
    args = parser.parse_args(argv)
    cwd = Path(args.cwd)
    if args.check:
        findings = check(cwd, None)
        if findings:
            print(format_findings(findings))
            return 1
        print("plugin audit: all enabled plugins match their reviewed baseline")
        return 0
    if not (args.note and args.note.strip()):
        parser.error("--note is required when recording a baseline")
    ids = args.acknowledge or enabled_plugins(cwd)
    return acknowledge(ids, args.note.strip(), args.auditor)


if __name__ == "__main__":
    sys.exit(cli_main(sys.argv[1:]) if len(sys.argv) > 1 else hook_main())
