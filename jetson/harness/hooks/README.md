# hooks/ (Jetson)

Deterministic enforcement scripts that Claude Code fires at lifecycle events. The 27 hook events defined in Claude Code v2.1.88 (Claude_Architecture.md §6.1) apply across platforms. The five tool-authorization events with rich output schemas (PreToolUse, PostToolUse, PostToolUseFailure, PermissionRequest, PermissionDenied) carry most of the enforcement weight on Jetson, same as Mac.

Hooks live here because they are the deterministic layer. The advisory layer (CLAUDE.md, skill instructions) cannot substitute for a hook. Every rule that must hold every time the harness runs lives in this directory.

## Naming convention

`hooks/<event>-<purpose>.sh` (or `.py`). Same as Mac.

Each hook script carries a header block: event registration, rule enforced, threat addressed, verification test (positive and negative), and the Linux shellcheck-cleanliness assertion.

## Security posture

Hooks are deterministic. They cannot be overridden by the model. The runtime fires them; the handler returns a decision; the runtime acts. A hook `allow` does not bypass subsequent rule-based denies or safety checks per Claude_Architecture.md §5.3.

Hook scripts pass shellcheck in pre-commit per QC.1 (PW.5.1). Hook scripts that fork subprocesses or make network calls justify the action in a header comment and the commit message. Hook scripts run with the user's full privileges on Linux. The discipline of writing them like security-critical code is not optional.

The 50-subcommand bypass class (Adversa.ai 2026) gets its own PreToolUse hook here. Pre-trust initialization defenses (CVE-2025-59536 class) live in a SessionStart hook with cadence per Phase 2's answer.

### Jetson-specific notes

`<NEEDS-JETSON-PORT-VALIDATION>`: hook scripts ported from Mac are verified to behave identically on ARM64 Linux. Specific edges:

- `grep -E` extended regex syntax is portable between GNU and BSD `grep`; `grep -P` Perl-compatible regex is GNU-only and is the preferred construct on Jetson if the Mac hook used it as a fallback.
- `find` flags differ between GNU and BSD; specifically `-mtime`, `-print0`, and `-regextype`. Each Mac hook using `find` is re-verified on Linux.
- `sed -i` syntax differs (Mac BSD `sed -i ''`, GNU `sed -i`). Hooks must use the Linux form.
- `xargs -0` and `-d` are GNU-specific. Stay on `-0` for null-delimited input.
- Path separators are forward slash on both platforms; no change needed.

The header block of each Jetson hook records which Mac edge cases were verified.

## Phase coverage

Phase 3 populates this directory. Phase 5 verifies every hook against the threat model and produces the polished final form.
