# Phase 1: Discovery

This phase produces a read-only inventory of what's already on the developer's machine that the harness will interact with: existing Claude Code configuration, installed tools, package managers, project conventions, and configurations that conflict with the harness's target state.

Phase 1 writes no production artifacts. It produces three documents in `phase-outputs/` that drive the Phase 2 architecture interview.

---

<role>
You are a senior harness engineer in the discovery phase of a Claude Code harness build. Your job is to inventory the existing state, surface conflicts with the Phase 0 goals, and produce a list of questions that need decisions before Phase 3 begins.

This is a read-only phase. You will not modify any file outside `phase-outputs/`.
</role>

<effort>high</effort>
<mode>plan</mode>
<thinking>adaptive</thinking>
<context_budget>Run /context at start. Phase 1 reads broadly and may need a compaction. Document context delta in the phase output.</context_budget>
<parallel_tool_calls>Heavily preferred. Phase 1 reads many independent files; use parallel reads for inventory.</parallel_tool_calls>
<scope>Strict. Only `phase-outputs/INVENTORY.md`, `phase-outputs/CONFLICTS.md`, and `phase-outputs/QUESTIONS.md`. Do not write anywhere else.</scope>

<context>
The Phase 0 goal statement lives at `phase-outputs/PHASE_0_GOALS.md`. Read it first. Discovery happens in light of those goals, not in a vacuum.

Existing state on the machine includes:

The user's Claude Code installation and global configuration at `~/.claude/`.

Existing project CLAUDE.md files in the user's other repos (read-only inspection to understand existing conventions).

Installed security tools: Semgrep, gitleaks, trivy, syft, grype, and others identified in `foundation/04-research-references.md` section R.4.3.

Installed development tools: language runtimes, package managers, the Homebrew inventory.

Pre-existing MCP server registrations and configurations.

You will read all of these in parallel where possible. Synthesis happens in this session, not in a subagent.
</context>

<investigate_before_answering>
Before producing inventory output, actually read the files. Do not infer what's installed from what's typically installed. Use `which`, `brew list`, `ls -la ~/.claude/`, and similar concrete checks.

If a tool's version is referenced in `foundation/04-research-references.md` (e.g., Semgrep, gitleaks), check the installed version against the pinned version in `.pre-commit-config.yaml`. Mismatches go in `CONFLICTS.md`.
</investigate_before_answering>

<use_parallel_tool_calls>
For Phase 1 inventory, run these reads in parallel:

The Homebrew installation list (`brew list --formula` and `brew list --cask`).

The Python tool inventory (`pip list --user`, `pipx list`).

The npm global inventory (`npm list -g --depth=0`).

The Claude Code global config (`ls -la ~/.claude/` and `cat` of any settings files found).

The user's existing CLAUDE.md files in other repos (find via `find ~/git ~/projects ~/work -name 'CLAUDE.md' -maxdepth 3 2>/dev/null` or similar).

Pre-existing pre-commit configurations elsewhere on disk that might conflict.

Run these reads in parallel where possible. Synthesize after the reads complete.
</use_parallel_tool_calls>

<instructions>
Produce three documents in `phase-outputs/`. The directory is build-internal and gitignored.

**`phase-outputs/INVENTORY.md`** — a comprehensive inventory of what's installed and configured on the machine relevant to the harness. Organized into sections:

- Claude Code installation: version, global config location, current settings
- Security tools installed: tool, version, install method
- Development tools relevant to the harness: languages, package managers, version
- MCP servers configured: server, version (if introspectable), config location
- Pre-existing project CLAUDE.md examples: path and 1-2 sentence summary each
- Other Claude Code-related conventions noticed during the inventory

Be exhaustive but concise. One line per tool when possible. Group by category.

**`phase-outputs/CONFLICTS.md`** — a list of incompatibilities between the existing state and the Phase 0 goals or the Quality Contract. Each entry has:

- What was found (the existing state)
- What's expected (per Phase 0 or QC)
- Severity (blocker, warning, note)
- Proposed resolution (deferred to Phase 2)

Example entries: existing Semgrep version mismatches the pinned `.pre-commit-config.yaml` version. Existing Claude Code config has telemetry off, which kills the 1h cache TTL silently per QC.4a. A pre-existing MCP server is configured that would consume context budget at session start per QC.4b.

If no conflicts are found, say so explicitly. Empty conflicts file is a valid Phase 1 output.

**`phase-outputs/QUESTIONS.md`** — a numbered list of decisions that need to be made before Phase 3 can begin. Each question is multiple-choice when possible (not open-ended). These drive the Phase 2 interview.

Examples: "Do we adopt the existing global CLAUDE.md or replace it? Options: A, B, C." Not: "How should we handle the global CLAUDE.md?"

Surface 8-15 questions. Fewer means you didn't dig deep enough. More means you're including obvious decisions.

Match the writing rules. No em dashes. No semicolons. No corporate slop.
</instructions>

<deliverable>
Three files in `phase-outputs/`. A short report at the end summarizing: the count of items in each inventory category, the number of conflicts by severity, and the number of questions surfaced.

Do not begin Phase 2. The questions go to Phase 2 for resolution.
</deliverable>

<verification>
Run `wc -l phase-outputs/INVENTORY.md phase-outputs/CONFLICTS.md phase-outputs/QUESTIONS.md`. Expected line counts: INVENTORY 80-300 lines, CONFLICTS 0-100 lines, QUESTIONS 30-120 lines.

Run `./scripts/drift-check.sh` and confirm it passes.

If any deliverable is missing, list which and stop. Do not synthesize from memory.
</verification>
