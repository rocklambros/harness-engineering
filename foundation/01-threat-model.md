# Threat Model

The harness exists in an adversarial environment whether or not we acknowledge it. This document names the threats explicitly, ranks them, and maps them to the harness layers that mitigate them. It is binding on every Phase 3 (deterministic layer) and Phase 4 (extension layer) decision.

## Scope

The threat model covers the harness as a system that produces and runs code at the direction of a developer using Claude Code. It does not cover the Anthropic platform itself, the underlying operating system, or general supply-chain attacks against pip, npm, and equivalent. Those threats exist and matter, but they're upstream of what the harness can influence.

In scope:

The behavior of Claude Code as a code-generating agent operating with permission to read, write, and execute against the developer's filesystem.

Untrusted content that enters the agent context through web fetches, MCP tool results, fetched documents, copy-pasted content, and the contents of files the agent reads.

The configuration surface of the harness itself: CLAUDE.md hierarchy, settings.json, hooks, skills, agents, rules, and any associated scripts.

The artifacts produced by the agent during a session: code, configuration changes, commits.

Out of scope:

Compromise of Anthropic's infrastructure or model weights.

Operating system compromise, kernel exploits, or hardware-level attacks against the developer's machine.

Insider threats from people with shell access to the developer's machine outside of Claude Code.

Generic supply-chain attacks on dependencies, except for the slopsquatting and dependency-confusion patterns the harness explicitly mitigates.

## Threat catalog

The threats below are numbered T.1 through T.7. Each names an attacker, an objective, the attack surface, the resulting harm, and the harness layers that mitigate it.

### T.1 Benign-prompt vulnerability generation

Attacker: nobody, structurally. This threat is the model itself.

Objective: not an objective. This is a failure mode.

Attack surface: every prompt asking Claude to write code.

Resulting harm: vulnerable code that passes tests, looks correct, and ships. The Liu et al. SecureForge research (arXiv:2605.08382) measures this at roughly 23% of benign coding prompts on frontier models including Claude Sonnet 4.6. The Arcanum sec-context research synthesizes 150+ sources estimating 40%+ of AI-generated code in production carries vulnerabilities.

Mitigations:

The `security-review` skill provides pre-generation guidance by lazy-loading anti-pattern context based on file type (Phase 4 extension layer, QC.1).

The PostToolUse Semgrep hook provides commit-time hardening by feeding static analysis findings back to Claude for in-session fixes (Phase 3 deterministic layer, QC.1).

The full pre-commit SAST stack provides post-generation validation as the final gate (Phase 3 deterministic layer, QC.1).

This is the highest-frequency threat. The three-layer defense is the entire reason QC.1 exists in the shape it does.

### T.2 Prompt injection through agent inputs

Attacker: a third party who controls content the agent reads.

Objective: induce the agent to take an action the developer did not authorize.

Attack surface: web fetches, MCP tool results, fetched documents, files in the project, content pasted by the developer that originated elsewhere.

Resulting harm: data exfiltration, unauthorized file writes, unauthorized command execution, credential disclosure.

Mitigations:

The agent treats all observed content from these sources as untrusted data, never as instructions. This is enforced by the system-level injection defense layer and reinforced in the project CLAUDE.md.

Hooks at PreToolUse can block tool calls that match exfiltration patterns (large outbound transfers, credential reads from unexpected paths).

The permission mode for read-heavy phases (Phase 1, Phase 2) is plan mode, which surfaces tool intent before execution.

User confirmation is required for actions in the explicit-permission list (downloads, account creation, irreversible writes, public posts, sending messages).

The Liu et al. Claude Architecture reverse engineering identifies the 50-subcommand bypass class. Hook registrations for PermissionRequest events provide a deterministic check against that class.

### T.3 Cache-state leakage and replay

Attacker: a passive observer of Anthropic API telemetry or someone who replays a cached prefix.

Objective: learn information about the project that should not have been cached, or trigger behavior that the developer thought was scoped to a single session.

Attack surface: cached prompt prefixes that include session-specific state, secrets, or sensitive paths.

Resulting harm: information disclosure, unintended persistence of session state.

Mitigations:

QC.4b prohibits timestamps, run IDs, and per-run state in cached prefix content. `<system-reminder>` blocks are used for changing data.

Secret scanning at pre-commit catches cases where secrets leak into committed CLAUDE.md or skill files.

The CLAUDE.md hierarchy size limit (under 400 lines, target 250) keeps the cached prefix small enough to audit visually.

### T.4 Hook bypass through subcommand or alternate-path execution

Attacker: a malicious actor with prompt-injection footing in the agent.

Objective: execute code or actions that bypass the deterministic hooks the harness relies on.

Attack surface: the 50-subcommand bypass class documented in the Liu et al. Claude Architecture analysis, alternate tool invocations that don't trigger the registered hooks, race conditions in hook execution.

Resulting harm: SAST gate bypass, unauthorized writes, unauthorized network egress.

Mitigations:

Hook registrations cover the bypass class by registering on the canonical and alternate event names where they differ.

Hooks are written to fail closed: if the hook script errors, the action is blocked, not allowed.

Hook scripts are themselves SAST-scanned at pre-commit. A hook that's been tampered with should fail the scan.

The PreToolUse hook on shell tools logs the actual invocation for after-action review.

### T.5 Dependency-supply-chain compromise

Attacker: a malicious actor who controls a package the project depends on.

Objective: execute code on the developer's machine through a poisoned dependency.

Attack surface: pip, npm, brew, apt, and platform-equivalent package installs triggered by the agent.

Resulting harm: arbitrary code execution at install time or runtime.

Mitigations:

QC.1 pins all dependencies to exact versions.

Trivy and grype scan dependency manifests at pre-commit.

OSV-Scanner cross-checks against the OSV database.

Slopsquatting (the AI-generation pattern where models hallucinate package names that don't exist, which attackers then register) is a specific failure mode caught by the `security-review` skill at the pre-generation guidance layer, and by trivy/grype at the post-generation layer.

SBOM generation at release time gives downstream consumers a verifiable list of what shipped.

### T.6 Credential and secret exposure in generated code

Attacker: not necessarily an attacker; this is often an accident.

Objective: not an objective when accidental; if intentional, credential theft.

Attack surface: generated code, configuration files, environment files, scripts that embed credentials.

Resulting harm: credential disclosure, downstream account compromise.

Mitigations:

Gitleaks at pre-commit and in CI.

The `security-review` skill flags credential-shaped strings in generated code.

The CLAUDE.md security rules explicitly require template-with-placeholder patterns instead of inline credentials.

Hooks at PreToolUse can block writes that match secret patterns before they hit disk.

### T.7 Configuration drift and silent capability erosion

Attacker: time and entropy.

Objective: nothing intentional.

Attack surface: the harness configuration itself, especially as Claude Code releases new versions with subtly different defaults.

Resulting harm: the harness silently stops enforcing what the documentation says it enforces. The March 2026 cache TTL regression is the canonical example.

Mitigations:

QC.5 requires re-evaluation on Claude Code minor-version bumps.

The `scripts/drift-check.sh` script at pre-commit checks for drift between cited references in artifacts and actual artifact content.

Pin Claude Code to a minor-version range in the harness CLAUDE.md status section.

JOURNEY.md entries on minor-version bumps document what changed and what was re-evaluated.

## Autonomous mode trade

The `HARNESS_AUTONOMOUS_MODE=1` env var, sourced from `~/.claude/settings.json` (project `.claude/settings.json` may override), instructs two PreToolUse hooks to return `allow` instead of `ask` for a defined subset of their findings. This is a deliberate weakening of the T.4 and T.5 mitigations, accepted in exchange for letting long-running unattended agents complete without operator prompts that would pause them indefinitely.

What it silences:

`PreToolUse-supply-chain-bash-checks.py` returns `allow` on every finding it would have prompted: unpinned `npx -y`, unpinned `uvx --from git+`, `@latest` tags, `pip install` without version constraint, `curl|sh` and `wget|bash` patterns.

`PreToolUse-bash-cap-subcommands.py` returns `allow` when the chain has between 31 and 49 subcommands. At 50 and above the deny stands, because Adversa.ai 2026 documents that per-subcommand deny-rule checks stop firing above 50, an irreversible loss of the deterministic floor.

What it does not silence:

`PreToolUse-external-write-gate.py`, `PreToolUse-git-push-force-ask.py`, `PreToolUse-cached-prefix-write-gate.py`, and `SessionStart-audit-claude-config.py` ignore the flag. These guard reversibility-low actions (writes outside cwd to settings.json or mcp.json, force push, cache-prefix mutations, hostile config in cloned repos under CVE-2025-59536 and CVE-2026-21852) where the cost of an inappropriate allow exceeds the workflow benefit.

Trust anchor: the env var is sourced from a settings.json file, and settings.json itself sits behind the external-write gate. The model cannot enable autonomous mode by writing to settings.json without an operator prompt. The flag therefore reflects operator intent at the moment they last edited the file.

Residual risk under T.5: a prompt-injected agent under autonomous mode can request a package install of a name the attacker controls. The PostToolUse Semgrep gate still scans any code the agent writes that references the package, and the bypass log at `~/.claude/hooks/autonomous-bypass.log` records every silenced finding for after-action review. The operator accepts this risk by leaving the flag set.

Residual risk under T.4: the 50-subcommand hard cap holds. The 30-to-49 range becomes available without the prompt-time check, but the runtime fallback above 50 still binds.

Per-project override: a project `.claude/settings.json` env block with `"HARNESS_AUTONOMOUS_MODE": "0"` restores prompting for that project. Use this on sensitive engagements (client work, security audits, anything where unattended supply-chain risk is not acceptable).

Audit trail: each silenced event writes one TSV line to `~/.claude/hooks/autonomous-bypass.log` (timestamp, hook name, tool, command, reason). File rotates at 1 MiB to `.log.1` with a single retained backup. The model also receives an `additionalContext` reminder so its turn output narrates the bypass.

## Threat ranking

Ranked by expected loss (frequency times severity), informed by the data in `foundation/04-research-references.md`:

T.1 (benign vulnerability generation) is the highest-frequency threat with moderate-to-high severity. It happens on roughly 1-in-4 generations and is invisible without static analysis.

T.2 (prompt injection) is medium-to-high frequency for users who fetch external content during sessions, with potentially severe consequences when it lands.

T.5 (dependency compromise) is low-frequency but high-severity, and the slopsquatting variant is rising in frequency as more code is AI-generated.

T.6 (secret exposure) is medium-frequency with high blast radius depending on what leaks.

T.7 (configuration drift) is low-frequency for any individual harness but high-cumulative-impact across the ecosystem.

T.3 (cache leakage) is low-frequency in practice but worth the constraint cost because the mitigation is cheap.

T.4 (hook bypass) is currently low-frequency but is the threat with the highest research-velocity. As the bypass class grows, this rises.

## How the threat model gets revised

When new research or in-the-wild incidents shift the ranking, the threat model is revised in its own commit with rationale and a JOURNEY entry. Downstream artifacts that reference threat IDs are updated in follow-up commits.
