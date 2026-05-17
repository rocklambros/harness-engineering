# Harness Guide

The technical reference for the harness across all three platforms. Read this after you understand the foundation docs and have picked a platform section. For end-user quickstart and daily operation, see `USER_GUIDE.md`.

## What the harness is

A configured Claude Code environment that enforces a Quality Contract through five layers (project CLAUDE.md, settings.json, deterministic rules, advisory skills, hooks and agents) and a three-layer security stack (pre-generation guidance, commit-time hardening, post-generation validation).

The harness is built, not adopted. Each platform section reproduces the same capability surface using platform-appropriate tools. Cross-platform parity is the non-negotiable AP.3.

## The five layers

The architecture is documented in each platform's `ARCHITECTURE.md`. The shape is identical across platforms.

Layer 1 is the project-level CLAUDE.md (`{platform}/harness/CLAUDE.md`). Advisory. Under 200 lines. TRACT pattern: Role, code standards, security rules, core constraints, things that break, operational, status.

Layer 2 is `settings.json` (`{platform}/harness/settings.json.template`). Deterministic. Configures permission modes, hook registrations, and trust-boundary policy.

Layer 3 is the deterministic rules in `{platform}/harness/rules/`. Path deny lists, command deny lists, secret patterns. Consumed by hooks; not interpreted by Claude.

Layer 4 is the skills in `{platform}/harness/skills/`. Advisory but lazy-loaded. The `security-review` skill is the primary one, scaffolded across all three platforms with identical content.

Layer 5 is the hooks and agents in `{platform}/harness/hooks/` and `{platform}/harness/agents/`. Hooks are deterministic. Agents are advisory and delegate-driven.

## The three-layer security stack

The security architecture cuts across Layers 4 and 5. Same composition on every platform.

**Layer 1 of the security stack** (pre-generation guidance) lives in `{platform}/harness/skills/security-review/`. Loads lazily based on file type. Content informed by the Arcanum-Sec sec-context taxonomy (CC BY 4.0, attribution preserved). Surfaces high-frequency anti-patterns before code is written.

**Layer 2 of the security stack** (commit-time hardening) lives in `{platform}/harness/hooks/post-tool-use-semgrep.sh`. Runs Semgrep on every Write or Edit and feeds findings back to Claude in the same session. Implements the SecureForge Appendix C pattern (MIT, Liu et al. 2026, arXiv:2605.08382). The paper measures a ~48% CWE-rate reduction from this layer alone.

**Layer 3 of the security stack** (post-generation validation) lives in `.pre-commit-config.yaml` at repo root. Same Semgrep tool, different invocation context. Supplemented by gitleaks for secrets, shellcheck for hook scripts, and the optional secondary scanners documented in each platform's `evaluations/deep-eval.md`.

Removing any of the three security layers weakens the others. The composition is binding per AP.2.

## Cross-platform tool equivalency

The capability is identical on every platform. The tool may differ.

| Capability | macOS | Jetson AGX Orin | Windows |
| --- | --- | --- | --- |
| SAST engine | Semgrep (native) | Semgrep (native) | Semgrep in WSL2 |
| Secret scanning | gitleaks (native) | gitleaks (native) | gitleaks in WSL2 |
| Shell linting | shellcheck (native) | shellcheck (native) | shellcheck in WSL2 |
| Hook scripts | bash | bash | bash in WSL2 |
| Python runtime | Homebrew-managed | Tegra Python | WSL2 Python |
| Package manager | Homebrew | apt + Jetson SDK | WSL2 apt + Chocolatey for Windows-native dependencies |

The WSL2 decision on Windows is documented in `windows/ARCHITECTURE.md` and pending hardware validation. The native Windows alternatives (Semgrep for Windows is incomplete on some rule packs as of build time) were evaluated and rejected for parity reasons.

## Build sequence

Every platform follows the same six-phase build sequence. Phase 0 establishes goals; Phases 1-5 build progressively from discovery to deterministic enforcement to advisory guidance to integration.

Phase 0 produces `phase-outputs/PHASE_0_GOALS.md`. Concrete success criteria, scope boundaries, out-of-scope decisions.

Phase 1 produces `phase-outputs/INVENTORY.md`, `CONFLICTS.md`, and `QUESTIONS.md`. Read-only discovery. Plan mode.

Phase 2 produces `phase-outputs/ANSWERS.md` and updates `ARCHITECTURE.md`. Architecture interview via `AskUserQuestion`. Last read-only phase.

Phase 3 produces the deterministic layer: `harness/CLAUDE.md`, `settings.json.template`, `rules/*`, `hooks/*`, and the wired pre-commit config. The PostToolUse Semgrep hook lands here.

Phase 4 produces the extension layer: `skills/*` (including `security-review` populated with pattern content), `agents/*`.

Phase 5 wires it all, runs the integration test, finalizes documentation, and produces the release commit. Uses the writer/reviewer subagent pattern.

The phase prompts in `{platform}/prompts/` are runnable Claude Code instructions. Each is self-contained and references the foundation docs and the relevant `ARCHITECTURE.md` section.

## Hook event coverage

The harness registers hooks on four Claude Code events:

`PostToolUse` on Write, Edit, and MultiEdit. Fires `post-tool-use-semgrep.sh` for commit-time hardening.

`PreToolUse` on Bash. Fires `pre-tool-use-shell-audit.sh` for shell audit logging.

`SessionStart`. Fires `session-start.sh` for drift check and Claude Code version check.

`PreCompact`. Fires `pre-compact-preserve.sh` to preserve active phase state across compaction.

Coverage is informed by the Liu et al. reverse engineering of Claude Code v2.1.x (R.1.1), which enumerates 12-21 events depending on count method. The four registered here are the ones with explicit harness dependencies. Additional events may be added per platform if Phase 1 surfaces specific needs.

## Versioning posture

The harness pins to a Claude Code minor-version range. The pinned range is documented in each platform's `harness/CLAUDE.md` status section.

Minor-version bumps trigger Quality Contract re-evaluation per QC.5:

The cache TTL behavior is re-checked. The March 2026 regression is the canonical example of why this matters.

Hook event coverage is verified against the current event list.

The SecureForge methodology is optionally re-run against representative workload to see whether the model's failure distribution has shifted enough to refresh the `security-review` skill.

Patch-version bumps do not trigger formal re-evaluation but are noted in the `JOURNEY.md` entry that covers the bump.

## How to update the harness

Updates are commits. Each commit follows the AP.5 template: phase or topic, Context, Decision, Why, Tradeoff.

The Why field cites the Quality Contract property or threat ID that justifies the change. The drift check verifies these citations resolve.

Cross-platform changes land as one commit when possible, with the rationale showing the equivalent change on each platform.

A change that affects only one platform is suspect and gets extra scrutiny per AP.3. Single-platform divergence requires an explicit rationale that survives review.

## Adopting the harness in a project

The harness ships in `{platform}/harness/`. To adopt it in a project:

Copy `{platform}/harness/` to the target project's repo root.

Copy the appropriate `settings.json.template` to `.claude/settings.json` and replace `{{REPO_ROOT}}` with the absolute path to the target project.

Copy `.pre-commit-config.yaml` and run `pre-commit install`.

Run the project's existing tests plus the integration test in `{platform}/scripts/integration-test.sh` (created during Phase 5).

The full adoption walkthrough is in `USER_GUIDE.md`.
