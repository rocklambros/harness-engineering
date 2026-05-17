# CLAUDE.md (Windows) — SCAFFOLDED

This file is the Windows-specific project-level CLAUDE.md scaffold. Phase 3 of the Windows build replaces it with the validated content.

Reference: `mac/harness/CLAUDE.md`. Windows-specific adjustments:

- Working directory convention: WSL2-visible paths `/mnt/c/Users/<user>/...` rather than `/Users/klambros/...`
- Status section pins to Windows-validated Claude Code range and WSL2 distribution version
- Operational section notes the WSL2 dependency and the `wsl.exe -e bash` hook invocation pattern

Do not adopt this scaffold into a Windows project until Phase 3 validates it.
