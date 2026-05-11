# Windows section

The Windows build of the harness. Windows 11 on x86_64. Claude Code running from the working directory recorded in `ARCHITECTURE.md`.

This section is scaffolded, not validated. Foundation, Phase 0, Phase 1, and Phase 2 prompts are written and ready to run. Phase 3, Phase 4, and Phase 5 prompts are scaffolded with `<NEEDS-WINDOWS-PORT-VALIDATION>` markers where Windows-specific behavior must be confirmed before any Mac-validated pattern is treated as portable. When Rock executes the Windows build, validation findings replace the markers and the section graduates from scaffolded to validated.

Capabilities identical across the three platforms per locked decision 3 in `CHECKPOINT.md`. Equivalence on Windows asserts against documented expectations until the build runs.

## What's in here

`ARCHITECTURE.md` documents the Windows harness target. Filled draft with `<TBD-PHASE-0>` blocks for platform-specific values and `<NEEDS-WINDOWS-PORT-VALIDATION>` blocks for Mac-ported assertions awaiting Windows confirmation.

`prompts/` holds the seven phase prompts. Phase 0 through Phase 2 carry the standard header and verification rigor. Phase 3 through Phase 5 carry scaffold-grade content marked with the `[SCAFFOLDED]` banner.

`harness/` holds the operational artifacts. `harness/CLAUDE.md` is the daily-driver instruction file for Windows sessions. `harness/settings.json.template` is the structural skeleton; Phase 0 and Phase 3 fill platform-specific values.

`evaluations/` holds the seed evaluation worksheets. The pre-filter table is pre-populated with the candidate set. The architecture-support column changes per candidate based on Windows x86_64 availability.

`scripts/` is reserved for Windows-platform-specific scripts that come out of Phase 3 or Phase 5.

## What's different from Mac and Jetson

The harness's nine components and the Quality Contract apply unchanged. Platform-specific deltas land in `ARCHITECTURE.md`. Summary:

- Operating system: Windows 11 on x86_64. Different shell (PowerShell 7+ recommended, with PowerShell 5.1 as the inbox default that may be present on older installs), different package manager (winget primary, Chocolatey or Scoop secondary), different credential store (Windows Credential Manager backed by DPAPI), different code-execution control (AppLocker or Windows Defender Application Control if configured), different host integrity model (UAC plus Microsoft Defender plus VBS, no SIP equivalent).
- WSL2 availability: most modern Windows installs have WSL2. Phase 2 decides whether the harness runs in native Windows, in WSL2, or in a hybrid model where Claude Code lives on Windows and hooks invoke Linux tooling via WSL2 for parity with the Mac and Jetson hook scripts.
- Network egress monitoring: GlassWire or simplewall on Windows is the equivalent of Little Snitch on Mac and opensnitch on Linux.
- Disk encryption: BitLocker, not FileVault or LUKS.
- Path conventions: forward slash works in most modern Windows tools and in Claude Code paths; backslash required for some PowerShell-native cmdlets. Hook scripts pick one and apply consistently.
- Line endings: CRLF default. `.gitattributes` in the repo root pins LF for shell scripts and configuration files; hooks normalize on read.

The threat model in `foundation/01-threat-model.md` is platform-agnostic. The mitigations in `harness/hooks/` and `harness/rules/` are platform-specific in their commands but identical in their intent.

## How to use this section

If you are reading this repo as a reference for building your own harness on Windows, the path is the same as Mac and Jetson: foundation first, then this section's `ARCHITECTURE.md`, then the seven prompts in order. The `<NEEDS-WINDOWS-PORT-VALIDATION>` markers are honest signals about which assertions have not yet been confirmed on this platform. Treat them as live questions, not as finished documentation.

If you are running these prompts against your own Windows machine, Phase 0 is the entry point. Run it first. Replace the `<TBD-PHASE-0>` blocks with the actual environment baseline. Phase 1 inventories your machine, Phase 2 makes the architecture decisions (including the WSL2 posture), and Phase 3 onward delivers the harness components with full validation. The build sequence is identical across the three platforms; the inputs and outputs are Windows-specific.

## Status

Scaffolded. Phase 0 through Phase 2 ready to execute. Phase 3 through Phase 5 carry validation markers that resolve when the build runs on real Windows hardware.

Build date: pending. The first execution of Phase 0 against a live Windows machine stamps the section with the date and the validation results.
