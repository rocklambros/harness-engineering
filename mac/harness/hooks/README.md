# hooks/

Deterministic enforcement scripts that Claude Code fires at lifecycle events. The 27 hook events defined in Claude Code v2.1.88 (Claude_Architecture.md §6.1) span tool authorization, session lifecycle, user interaction, subagent coordination, context management, and workspace events. The five tool-authorization events with rich output schemas (PreToolUse, PostToolUse, PostToolUseFailure, PermissionRequest, PermissionDenied) carry most of the enforcement weight.

Hooks live here because they are the deterministic layer. The advisory layer (CLAUDE.md, skill instructions) cannot substitute for a hook. Every rule that must hold every time lives in this directory.

## Naming convention

`hooks/<event>-<purpose>.sh` (or `.py` where shell is the wrong tool). Examples: `PreToolUse-bash-cap-subcommands.sh`, `PreToolUse-deny-external-writes.sh`, `SessionStart-load-skill.sh`, `PreCompact-preserve-decisions.sh`.

The event name in the filename matches the Claude Code hook event exactly (Claude_Architecture.md §6.1 lists all 27). The purpose name is kebab-case and explains what the script enforces, not how.

Each hook script carries a header block with: the event it registers to, the rule it enforces, the threat it addresses (`foundation/01-threat-model.md` citation), the test that verifies the hook fires when expected, and the test that verifies the hook does not fire when not expected.

## Security posture

Hooks are deterministic. They cannot be overridden by the model. The runtime fires them, the handler returns a decision (per the Zod-validated output schema for that event from `types/hooks.ts`), the runtime acts. A hook `allow` does not bypass subsequent rule-based denies or safety checks per Claude_Architecture.md §5.3.

Hook scripts pass shellcheck in pre-commit per QC.1 (PW.5.1). Hook scripts that fork subprocesses or make network calls explicitly justify the action in a header comment and in the commit message. Hook scripts run with the user's full privileges; the discipline of writing them like security-critical code is not optional.

The 50-subcommand bypass class (Adversa.ai 2026, per Claude_Architecture.md §5.4) gets its own PreToolUse hook here. Pre-trust initialization defenses (CVE-2025-59536 class) live in a SessionStart hook that refuses to load a project whose `.claude/settings.json` or `.mcp.json` has not been audited within the last N days, where N comes from Phase 2 interview.

## Phase coverage

Phase 3 populates this directory. Phase 5 verifies every hook against the threat model and produces the polished final form with the audit results.
