# Windows Harness Architecture

The Windows harness mirrors the Mac architecture in capability while inverting how the tools execute. The five layers and three-layer security stack are identical; the invocation context for Layer 2 and Layer 3 is WSL2 rather than native Windows.

If you have not read `mac/ARCHITECTURE.md`, read it first. This document is a delta plus the WSL2 decision rationale.

## System context

The Windows harness runs Claude Code on Windows 10/11 (x86-64) with a WSL2 instance running Ubuntu 22.04 LTS as the tool execution environment. Claude Code on Windows is a native Windows application; the security tools (Semgrep, gitleaks, shellcheck, jq, pre-commit) are native Linux binaries running inside WSL2.

Filesystem layout:

The harness lives in the Windows filesystem (typically `C:\Users\<user>\harness-engineering\` or wherever the user clones it).

WSL2 sees this filesystem at `/mnt/c/Users/<user>/harness-engineering/`.

Hook scripts in `windows/harness/hooks/` are bash scripts. Claude Code on Windows invokes them through `wsl.exe -e bash <path>`.

Process invocation flow:

Claude Code on Windows triggers a hook (e.g., PostToolUse).

The settings.json hook command is `wsl.exe -e bash /mnt/c/Users/<user>/harness-engineering/windows/harness/hooks/post-tool-use-semgrep.sh`.

WSL2 spawns bash inside the Ubuntu environment, which runs the hook script with full access to Semgrep, jq, and the rest of the Linux tooling.

The script's stdout returns to Claude Code on Windows, which presents findings to the model.

## The WSL2 decision

The choice to invoke security tooling through WSL2 rather than natively on Windows comes from a survey of the native tool landscape:

Semgrep on Windows native has spotty rule-pack coverage as of build time. Several `p/security-audit` rules either fail to load or behave inconsistently. The Linux build is the reference and is the build that the SecureForge research (R.2.1) measured against.

shellcheck on Windows is available via Chocolatey, but the bash hook scripts use Linux-isms (jq for JSON parsing, POSIX-compliant test syntax, `/proc` and `/dev` paths in places) that don't translate cleanly.

gitleaks on Windows is functional natively, but running it in a different environment than Semgrep creates a configuration split that's prone to drift.

pre-commit on Windows works for many hook types but has known issues with hooks that shell out to Linux-specific binaries.

The alternative (re-implement the hooks in PowerShell or Python) was evaluated and rejected:

It would create a divergent codebase from Mac and Jetson, violating AP.3.

It would require re-validating the SecureForge methodology against the new implementation, doubling the validation cost.

The WSL2 startup overhead (100-300ms per hook invocation cold, less when warm) is acceptable for the workflow.

The cost of the WSL2 decision:

A required dependency: users must install WSL2 with a supported distribution. This is documented in `windows/USER_GUIDE.md`.

A path-translation step: Windows paths in tool input must be converted to WSL2 paths before the bash scripts process them. Helper functions live in the hook scripts.

A small per-hook latency overhead.

A failure mode that doesn't exist on Mac or Jetson: WSL2 can be uninstalled, paused, or have its distribution removed. The session-start hook checks WSL2 health and surfaces issues early.

The benefit:

Capability parity with Mac and Jetson at the security-tooling level.

Identical hook script content across all three platforms, modulo the `wsl.exe` wrapper for the Windows invocation context.

A single SAST rule pack and a single methodology validating against the same tooling across the fleet.

## The five layers (Windows variations)

### Layer 1: Project CLAUDE.md

Identical to Mac in shape and content. The status section pins to the Windows-validated Claude Code range and notes the WSL2 distribution version.

### Layer 2: settings.json

Identical to Mac in structure. The hook command paths use `wsl.exe -e bash` wrappers around the bash hook scripts.

Example hook entry:

```json
{
  "type": "command",
  "command": "wsl.exe -e bash /mnt/c/Users/{{USER}}/harness-engineering/windows/harness/hooks/post-tool-use-semgrep.sh",
  "timeout": 60
}
```

The path is the WSL2-visible path (`/mnt/c/...`), not the Windows path (`C:\...`).

The `permissions.deny` list adds Windows-specific patterns: `Read(C:\Windows\System32\config\**)`, `Read(C:\Users\*\AppData\Local\Microsoft\Credentials\**)`, and similar Windows-specific sensitive paths.

### Layer 3: Deterministic rules

Same rule files as Mac with Windows-specific path additions:

`paths.deny` extends with Windows credential stores (`AppData\Roaming\Microsoft\Crypto\`, registry-export files, common Windows secret paths).

`paths.allow` notes the WSL2-vs-Windows path duality.

`commands.deny` extends with Windows-specific patterns: `powershell.exe -EncodedCommand`, `cmd /c reg add HKLM:\...`, similar high-risk patterns.

`secrets.patterns` is identical.

### Layer 4: Skills

The `security-review` skill content is identical to Mac. The skill loads in Claude Code on Windows the same way it loads on Mac. The file-type triggers cover the same extensions.

### Layer 5: Hooks and agents

Hook scripts are byte-identical to Mac and Jetson. They are bash. They expect a Linux-like environment (`/tmp`, `/proc` access for some checks, POSIX commands). They run inside WSL2.

The `wsl.exe` invocation is configured in `settings.json.template`, not in the hook scripts themselves. This keeps the hook scripts portable and identical across platforms.

Agents (`security-reviewer.md`, `writer-reviewer.md`) are identical.

One Windows-specific consideration: the `session-start.sh` hook on Windows includes a WSL2 health check (verify the distribution is running, verify Semgrep is available, verify path translation works). The check is appended to the same hook script via a Windows-specific section guarded by an environment check.

## The three-layer security stack (Windows)

Identical composition. Identical content. Different runtime substrate for Layers 2 and 3.

Layer 1: `harness/skills/security-review/`. Content identical. Loaded by Claude Code on Windows.

Layer 2: `harness/hooks/post-tool-use-semgrep.sh`. Script identical. Invoked via `wsl.exe`. Runs inside WSL2 with Linux Semgrep.

Layer 3: `.pre-commit-config.yaml`. Same configuration. Pre-commit runs inside WSL2 (the developer activates the WSL2 environment to run `git commit`, or configures git on the Windows side to invoke pre-commit through WSL2).

The methodology binding (SecureForge), taxonomy binding (sec-context), and Quality Contract binding (QC.1) are identical to Mac and Jetson.

## Cross-platform tool equivalency for Windows

| Capability | Tool on Windows | Same as Mac? | Notes |
| --- | --- | --- | --- |
| SAST engine | semgrep (Linux build inside WSL2) | Same engine, Linux build | WSL2 invocation |
| Secret scanning | gitleaks (Linux build inside WSL2) | Same engine, Linux build | Can run native on Windows but uses WSL2 for consistency |
| Shell linting | shellcheck (Linux build inside WSL2) | Same engine | WSL2 invocation |
| JSON tooling | jq (inside WSL2) | Same tool | WSL2 invocation |
| Python runtime | Python in WSL2 | Different (WSL2 Python, not Windows Python) | Pre-commit runs against WSL2 Python |
| Package manager | apt inside WSL2 plus Chocolatey for Windows-host needs | Different | Documented in `windows/USER_GUIDE.md` |
| Pre-commit framework | pre-commit inside WSL2 | Same | Git on Windows configured to invoke through wsl.exe |

## Build sequence on Windows

Same six-phase sequence as Mac and Jetson.

Phase 0, Phase 1, Phase 2 are fully ported and ready to run.

Phase 3, Phase 4, Phase 5 are scaffolded with "needs validation when ported" markers. The validation work for Windows is more involved than for Jetson because of the WSL2 indirection.

## What this architecture does not address

Cross-platform development from Mac or Jetson to Windows. The harness assumes the developer is at the Windows machine.

PowerShell-based hooks. The harness uses bash via WSL2 for parity. PowerShell variants are out of scope.

Windows-specific anti-pattern coverage in the security-review skill (e.g., Windows API-specific buffer overflows, Windows credential API misuse). These could be added as Windows-specific skill content if Phase 4 surfaces specific projects that need them. Out of scope for the initial scaffolded build.

Multi-WSL2-distribution setups. The harness assumes one default WSL2 distribution. Users with multiple distributions configure the default explicitly.

These omissions are deliberate. They keep the Windows section focused on the parity the harness actually needs.
