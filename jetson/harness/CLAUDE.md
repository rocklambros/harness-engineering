# CLAUDE.md (Jetson) — SCAFFOLDED

This file is the Jetson-specific project-level CLAUDE.md scaffold. Phase 3 of the Jetson build populates this with the validated Jetson content. The scaffold below is a copy-from-Mac starting point.

Run `jetson/prompts/phase-3-deterministic-layer.md` against an actual Jetson AGX Orin to produce the validated version. The "needs validation when ported" markers in that prompt cover this file.

Reference the Mac equivalent at `mac/harness/CLAUDE.md` for content shape. Jetson-specific adjustments:

- Working directory likely `/home/jetson/` not `/Users/klambros/`
- Status section pins to Jetson-specific JetPack version and Claude Code aarch64 validated range
- Operational section notes apt-based dependency install rather than Homebrew

Do not adopt this scaffold into a Jetson project until Phase 3 validates it.
