# hooks/ (Windows)

Deterministic enforcement scripts that Claude Code fires at lifecycle events. The 27 hook events defined in Claude Code v2.1.88 (Claude_Architecture.md §6.1) apply across platforms. The five tool-authorization events with rich output schemas (PreToolUse, PostToolUse, PostToolUseFailure, PermissionRequest, PermissionDenied) carry most of the enforcement weight on Windows, same as Mac and Jetson.

Hooks live here because they are the deterministic layer. The advisory layer (CLAUDE.md, skill instructions) cannot substitute for a hook. Every rule that must hold every time the harness runs lives in this directory.

## Naming convention

`hooks/<event>-<purpose>.ps1` for PowerShell-native hooks. `hooks/<event>-<purpose>.py` for Python hooks. `hooks/<event>-<purpose>.sh` if Phase 2 elected WSL2 routing for shell-class hooks. The choice is documented in `windows/ARCHITECTURE.md` and applied consistently.

Each hook script carries a header block: event registration, rule enforced, threat addressed, verification test (positive and negative), execution context (native PowerShell, WSL2 bash, etc.), and the language-appropriate linter cleanliness assertion (PSScriptAnalyzer for PowerShell, shellcheck for bash through WSL2).

## Security posture

Hooks are deterministic. They cannot be overridden by the model. The runtime fires them; the handler returns a decision; the runtime acts. A hook `allow` does not bypass subsequent rule-based denies or safety checks per Claude_Architecture.md §5.3.

PowerShell hook scripts pass PSScriptAnalyzer in pre-commit per QC.1 (PW.5.1). Python hook scripts pass language-appropriate SAST. Hook scripts that fork subprocesses or make network calls justify the action in a header comment and the commit message. Hook scripts run with the user's full privileges on Windows. The discipline of writing them like security-critical code is not optional.

The 50-subcommand bypass class (Adversa.ai 2026) gets its own PreToolUse hook here. Pre-trust initialization defenses (CVE-2025-59536 class) live in a SessionStart hook with cadence per Phase 2's answer.

### Windows-specific notes

`<NEEDS-WINDOWS-PORT-VALIDATION>`: hook scripts ported from Mac or Jetson are verified to behave identically on Windows. Specific edges:

- PowerShell version differences. PowerShell 7+ is mostly POSIX-friendly. PowerShell 5.1 (Windows inbox default that some installs still carry) has parameter binding and pipeline edges that differ. Hook scripts that target one are tagged; cross-version compatibility is not assumed.
- Execution policy. `Restricted` blocks all hooks. `RemoteSigned` is the minimum working policy. `Bypass` is not acceptable. Phase 0 records and Phase 2 confirms.
- Path conventions. `Resolve-Path` and `Convert-Path` cmdlets normalize the slash direction within a script. Cross-script comparisons need a canonical form.
- Line endings. PowerShell tolerates both CRLF and LF for hook scripts. WSL2 bash hooks must be LF. The `.gitattributes` discipline pins LF for any bash script.
- Process invocation. `Start-Process` vs direct invocation has different return semantics. Hook scripts that need to capture exit codes use direct invocation with `$LASTEXITCODE`.
- WSL2 routing latency. If a hook routes from native Windows to WSL2 for shell-class work, the startup cost is non-trivial. Phase 3 measures and records; if latency exceeds the PreToolUse budget, the routing decision gets revisited.

The header block of each Windows hook records which Mac or Jetson edge cases were verified and which execution context (native PowerShell, WSL2 bash) the hook uses.

## Phase coverage

Phase 3 populates this directory. Phase 5 verifies every hook against the threat model and produces the polished final form.
