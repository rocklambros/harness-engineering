# Hooks (Windows): scaffolded

Phase 3 produces validated hook scripts. Scripts are byte-identical to Mac and Jetson; they run inside WSL2 via `wsl.exe -e bash` invocation configured in `settings.json.template`.

A path-translation helper at the top of each hook script handles Windows-style paths (`C:\...`) in hook payloads, converting them to WSL2 paths (`/mnt/c/...`).

The `session-start.sh` hook on Windows includes a WSL2 health-check section.

Reference: `mac/harness/hooks/README.md`.

The post-tool-use Semgrep hook implements SecureForge Appendix C (R.2.1) identically across all three platforms. Layer 2 of the three-layer security stack.

## Status of the Python hooks (October 30, 2026)

`PreToolUse-external-write-gate.py`, `PreToolUse-bash-deny-rm-protected-paths.py`, and `ConfigChange-audit-claude-config.py` are byte-identical copies of the Mac source, with their test matrices under `tests/`, kept here for AP.3 parity of the scripts. The Windows `settings.json.template` is still a scaffold and registers neither. The rm hook sees only the Bash tool. For the PowerShell tool, Claude Code's own `Remove-Item` system-path deny is the native equivalent until the WSL2 validation lands. The AP.3 exception is recorded in `windows/ARCHITECTURE.md`.
