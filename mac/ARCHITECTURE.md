# Mac Harness Architecture

This document describes the macOS harness as a system. It explains what each layer does, why each layer exists, and how the layers compose. It is the authoritative reference for the Mac section; all phase prompts and harness files trace back to it.

The Jetson and Windows architectures share the same shape with platform-specific tool substitutions. See `jetson/ARCHITECTURE.md` and `windows/ARCHITECTURE.md` for the differences.

## System context

The Mac harness runs Claude Code (pinned to v2.1.x, range to be finalized in Phase 0) against the developer's local filesystem at `/Users/klambros/`. Claude Code is granted permission to read, write, and execute against a set of project directories with hooks and permission checks intercepting specific tool calls.

The harness mediates between the developer's intent (expressed through Claude Code prompts and the project CLAUDE.md hierarchy) and the actions Claude Code takes (file writes, command executions, network requests, MCP tool calls). The mediation is what makes the system a harness rather than just a chat interface.

Hardware: Apple Silicon (M-series), ARM64, macOS 14+ (Sonoma or later). Tooling assumes Homebrew is available, Python 3.12+ is on PATH, and the standard Unix toolchain (bash, sed, grep) is present.

External dependencies: the Anthropic API for Claude Code's model access, the package managers (Homebrew, pip, npm) for tool installation, the GitHub API for repo interactions when relevant.

## The five layers

The harness is structured into five layers, each scoped to what it can enforce or guide.

### Layer 1: Project CLAUDE.md

The `harness/CLAUDE.md` file is the project-level operational context for every Claude Code session against this repo. It follows a seven-section pattern (Role, code standards, security rules, core constraints, things-that-break, operational, status).

Scope: advisory. The model reads it, weights its instructions, and may not perfectly follow them. Rules that must not be broken belong in the deterministic layers below.

Size budget: under 200 lines hard cap, target 160. The total CLAUDE.md hierarchy (root plus subdirectory CLAUDE.md files in scope) stays under 400 lines per QC.4b.

Cache discipline per QC.4a applies: no timestamps, no run IDs, no session state. Changing data goes in `<system-reminder>` blocks injected per session, not in the cached prefix.

Rationale: AP.1 establishes deterministic-over-advisory as the architectural principle. CLAUDE.md is the advisory surface. It exists to influence model behavior at the margin, not to enforce policy.

### Layer 2: settings.json

The `harness/settings.json.template` configures the deterministic behavior of Claude Code: permission mode defaults, hook registrations, MCP server configurations, and the trust-boundary policy.

Scope: deterministic. Settings are enforced by Claude Code itself, not by the model.

Key configurations:

Permission mode defaults to plan for Phase 1 and Phase 2 prompts (read-heavy discovery), default for Phase 3 through Phase 5 (write phases).

PostToolUse hook registered on Write and Edit tools, invoking `harness/hooks/post-tool-use-semgrep.sh`.

PreCompact hook registered to preserve the relevant phase context across compaction events.

PermissionRequest hook registered to log and gate elevated-permission requests.

MCP server list is not present in this file by default; servers are added per-session via tool search.

Rationale: AP.1 and Liu et al. R.1.1 on hook events and the 50-subcommand bypass class. Coverage of the bypass class requires explicit hook registration on the canonical and alternate event names.

### Layer 3: Deterministic rules

The `harness/rules/` directory holds the deterministic policy that the hooks enforce. This is not a single tool; it's a collection of pattern files, regex sets, and policy documents that the hook scripts consult.

Concrete contents:

Path allow/deny lists for file operations (e.g., never write to `/etc/`, never read from `~/.ssh/`).

Command allow/deny lists for shell execution (e.g., block `curl | sh` patterns, gate `rm -rf` on specific paths).

Secret-detection patterns (supplementing gitleaks with project-specific patterns).

Network egress policies for tool calls that would fetch external content.

Scope: deterministic. These rules are consulted by hooks, which fail closed (AP.8).

Rationale: AP.1, AP.8. Rules that matter are enforced by hooks, not by CLAUDE.md.

### Layer 4: Skills

The `harness/skills/` directory holds the lazy-loadable guidance that informs Claude Code's behavior on specific tasks. Each skill has a `SKILL.md` that Claude reads when the skill is relevant.

The primary security skill is `harness/skills/security-review/`. It is the pre-generation guidance layer of the three-layer security stack. It loads anti-pattern context by file type: Python files load the Python anti-pattern section, JavaScript files load the JS section, and so on.

Other skills land here per Phase 4 evaluation: domain-specific guidance for the projects Rock works on, language-specific best practices, framework-specific patterns.

Scope: advisory, but with a structural advantage over CLAUDE.md: skills load on demand, so they don't consume cached prefix budget unless invoked.

Rationale: AP.7 (lazy load) and AP.2 (three-layer security pre-generation guidance position).

### Layer 5: Agents and hooks

The `harness/agents/` directory holds specialized subagent definitions for tasks that benefit from delegation. The `harness/hooks/` directory holds the hook scripts that the settings.json registers.

Hooks of interest:

`post-tool-use-semgrep.sh` runs Semgrep on changed files after Write or Edit. If findings, returns the rule ID, line, and message to Claude via hook output. This is the SecureForge Appendix C commit-time hardening pattern.

`pre-tool-use-shell-audit.sh` logs shell command invocations before execution. Does not block (logging only).

`session-start.sh` runs the drift check on session start and surfaces any drift before the session begins.

`pre-compact-preserve.sh` ensures the relevant phase context survives the compaction event.

Agents of interest:

`writer-reviewer` agent pair for Phase 5 documentation: one writes, one reviews against SSDF practices.

`security-reviewer` subagent for deep security analysis of generated code beyond what Semgrep catches.

Scope: deterministic for hooks, advisory for agents. Agents are still model-driven; they just have a constrained scope.

Rationale: AP.1, AP.2.

## The three-layer security stack in context

The security architecture cuts across layers 4 and 5 specifically. Here's where each layer of the security stack lives:

Pre-generation guidance lives in Layer 4: `harness/skills/security-review/`. Loaded lazily when files of relevant types are touched. Content seeded from sec-context taxonomy (R.2.2), attributed under CC BY 4.0.

Commit-time hardening lives in Layer 5: `harness/hooks/post-tool-use-semgrep.sh`. Runs deterministically after every Write or Edit. Implements the SecureForge Appendix C pattern (R.2.1, MIT).

Post-generation validation lives in `.pre-commit-config.yaml` at repo root. Same Semgrep tool, different invocation context (pre-commit hook rather than PostToolUse hook), supplemented by gitleaks, shellcheck, and the optional secondary scanners in `mac/evaluations/`.

The three layers are independent. Removing any one weakens the others. The SecureForge research (R.2.1) shows the combination outperforms any single layer at equivalent compute budget.

## Build sequence and phase boundaries

The harness is built in five phases (Phase 0 through Phase 5), with Phase 0 establishing scope before the build begins. Each phase produces specific artifacts:

Phase 0 produces the goal statement, scope boundaries, success criteria, and constraint inventory. Deliverable: `phase-outputs/PHASE_0_GOALS.md`.

Phase 1 produces the discovery output: an inventory of existing tools and configurations, a conflicts list of incompatibilities, and a questions list to drive Phase 2. Deliverables: `phase-outputs/INVENTORY.md`, `phase-outputs/CONFLICTS.md`, `phase-outputs/QUESTIONS.md`.

Phase 2 produces the architecture decisions: an answers document keyed to the Phase 1 questions, an updated `ARCHITECTURE.md`, and the seed list for Phase 3 and Phase 4 evaluation. Deliverable: `phase-outputs/ANSWERS.md`.

Phase 3 produces the deterministic layer: `harness/CLAUDE.md`, `harness/settings.json.template`, `harness/rules/*`, `harness/hooks/*`, and the wired `.pre-commit-config.yaml`. Includes the PostToolUse Semgrep hook (the commit-time hardening layer of the security stack).

Phase 4 produces the extension layer: `harness/skills/*`, `harness/agents/*`. Includes the `security-review` skill (the pre-generation guidance layer).

Phase 5 wires it all together, runs integration tests, and finalizes the documentation. Includes the writer/reviewer agent pattern documented in the SAGE analysis (R.2.3).

Phase boundaries are not arbitrary. They map to Quality Contract properties and to the threat model: Phase 3 deliverables address T.4 (hook bypass) and T.6 (secret exposure); Phase 4 deliverables address T.1 (benign vulnerability generation) and T.2 (prompt injection); Phase 5 verifies T.7 (configuration drift) is mitigated by the drift-check infrastructure.

## What this architecture does not include

A custom model. Claude Code is the substrate. We configure it, we don't replace it.

A web service. The harness runs locally. Outputs that would otherwise go through a service (SBOM generation, vulnerability reports) are produced by command-line tools.

A long-running daemon. Hooks run synchronously inside Claude Code sessions. No background process maintains harness state.

A user management system. The harness is single-user. Multi-developer extensions are out of scope.

These omissions are deliberate. Each one represents a class of complexity the harness explicitly does not buy. The cost of adding any of them would dwarf the cost of the current build, and none of them are needed for the actual problem the harness solves.
