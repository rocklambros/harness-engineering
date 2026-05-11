#!/usr/bin/env python3
"""
Hook: Stop-prune-session-logs
Event: Stop
Purpose: Delete per-session JSONL logs older than 90 days from
         ~/.claude/projects/. Skip if the last cleanup ran within the last
         24 hours (guard against per-session overhead).

Threat: Not a direct threat-model citation. SAGE §4.10 names persistence as
        the only durable component of the Claude Code execution model; the
        retention policy balances replay value, disk usage, and privacy posture.

Decision: Phase 2 Q11 → 90 days. Phase 3 chose the Stop hook over a launchd
          plist (rationale in PHASE-3-NOTES.md §Q11): no LaunchAgent
          maintenance, runs in-process with the access needed, 24h guard
          avoids per-session overhead.

The aggregate ~/.claude/history.jsonl is NOT pruned (rolling buffer; serves a
different audit purpose than per-session logs).

Verify:
    echo '{}' | python3 Stop-prune-session-logs.py
    # exit 0, empty stdout. Inspect ~/.claude/.last-cleanup-90d to confirm
    # the marker's mtime updated to now.

Owner: harness-engineering (Phase 3, 2026-05-11)
"""
import json
import os
import sys
import time
from pathlib import Path

RETENTION_DAYS = 90
MIN_INTERVAL_SECONDS = 24 * 3600
MARKER = Path(os.path.expanduser("~")) / ".claude" / ".last-cleanup-90d"
PROJECTS_DIR = Path(os.path.expanduser("~")) / ".claude" / "projects"


def main() -> int:
    # Drain stdin to be polite to the runtime; ignore the content (Stop hook
    # does not branch on it).
    try:
        json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        pass
    now = time.time()
    if MARKER.exists():
        try:
            if now - MARKER.stat().st_mtime < MIN_INTERVAL_SECONDS:
                return 0
        except OSError:
            pass
    if not PROJECTS_DIR.is_dir():
        return 0
    cutoff = now - RETENTION_DAYS * 86400
    for p in PROJECTS_DIR.rglob("*.jsonl"):
        try:
            mtime = p.stat().st_mtime
        except OSError:
            continue
        if mtime < cutoff:
            try:
                p.unlink()
            except OSError:
                continue
    try:
        MARKER.parent.mkdir(parents=True, exist_ok=True)
        MARKER.touch()
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
