# Hooks (Windows) — SCAFFOLDED

Phase 3 produces validated hook scripts. Scripts are byte-identical to Mac and Jetson; they run inside WSL2 via `wsl.exe -e bash` invocation configured in `settings.json.template`.

A path-translation helper at the top of each hook script handles Windows-style paths (`C:\...`) in hook payloads, converting them to WSL2 paths (`/mnt/c/...`).

The `session-start.sh` hook on Windows includes a WSL2 health-check section.

Reference: `mac/harness/hooks/README.md`.

The post-tool-use Semgrep hook implements SecureForge Appendix C (R.2.1) identically across all three platforms. Layer 2 of the three-layer security stack.
