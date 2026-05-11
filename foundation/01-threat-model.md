# Threat Model

The harness is a piece of software that sits between Claude Code, a stochastic model, and three machines containing source code, secrets, SSH keys, browser cookies, and the ability to push to GitHub. The threat model treats the harness as defended territory, not as plumbing.

This document names the threats this harness defends against, the threats it explicitly does not defend against, and the assumptions that make the defense work. When an assumption becomes false (the Claude Code version changes, a new CVE class appears, the operating environment shifts), the threat model gets revisited. Drift in the threat model is itself a threat.

## Assets

What the harness protects, in rough priority order:

1. **Source code integrity**: Working copies on three machines and the public GitHub remote. Unauthorized writes, silent edits, and supply-chain compromise of dependencies all land here.
2. **Secrets**: `.env` files, SSH keys, API tokens (Anthropic, GitHub, MCP server credentials), browser session cookies, password manager state.
3. **Execution permissions**: The ability of any process on the machine to invoke `git push`, `npm publish`, `gh` CLI commands, `curl` against arbitrary endpoints, or `rm -rf`.
4. **The cached prefix**: The CLAUDE.md hierarchy and any cache-eligible content. Cache poisoning by way of injected text is cheap and high-leverage.
5. **The deterministic layer**: Hook scripts and deny rules. If an attacker rewrites a hook, every subsequent invocation runs against altered rules.
6. **Reputation of the public repo**: This repo is public. Malicious changes to harness templates or rationale documents could harm anyone who reads them as reference.

## Threat actors

- **Prompt injection via files and tool returns**: A document Rock asks Claude to read contains hostile instructions. A web search result contains them. An MCP tool return contains them. Probability of encountering this in normal use is high. The current Claude Code defenses (the ML-based prompt-injection classifier, the deny-first permission system) are partial mitigations, not complete.
- **Supply-chain compromise**: A pinned dependency gets compromised upstream. A seed repo evaluated and integrated turns malicious in a later version. The pre-commit and SBOM workflow catches some of this. The seed evaluation methodology (`03-seed-evaluation-methodology.md`) treats integration as a permission grant, not a curiosity.
- **Pre-trust initialization (CVE-2025-59536 class)**: The architectural class where code in `.claude/settings.json` or `.mcp.json` executes during project initialization before the user trust dialog appears. CVE-2025-59536 (CVSS 8.7) and CVE-2026-21852 (CVSS 5.3) were patched by Anthropic, but the user habit of opening cloned repos without auditing settings files survives the patch. Treating every cloned repo as hostile until its `.claude/` directory is reviewed is the defense.
- **50-subcommand bypass class**: Commands chained with more than 50 subcommands fall back to a single generic approval prompt instead of per-subcommand deny-rule checks, due to UI-freeze performance constraints documented by Adversa.ai. The harness defends by capping subcommand chains in hook scripts and rejecting long chains at the PreToolUse stage.
- **Cache poisoning of the prefix**: An attacker who can land text in CLAUDE.md or any cached-prefix file lands persistent influence over every future session. Read-only flags on harness files during runtime, pre-commit review of CLAUDE.md changes, and drift checks all push against this.
- **Compromised or hostile MCP server**: An MCP server with broad tool exposure is a privilege escalation surface. The harness defaults to denying network egress to MCP servers not on an explicit allowlist, and treats every MCP server registration as a permission grant requiring review.

## Out of scope

The harness does not defend against:

- **Physical access to the unlocked machine**. Disk encryption and screen lock are the host operating system's job. If an attacker is at the keyboard, the harness is not the right layer.
- **Anthropic itself going rogue**. The trust model assumes Claude Code's source code and the Anthropic API endpoints behave as documented. Verification of the binary against a known-good hash on every install is overkill for a personal harness; the harness pins the version and watches the changelog.
- **Compromise of the GitHub credential during a push**. If Rock's GitHub token leaks, the harness cannot help. The token is treated as a tier-1 secret and rotated on a calendar schedule.
- **Long-horizon adversaries with insider knowledge of Rock's habits**. The harness is built for general threats. Targeted adversarial work would require a different model.

## Assumptions

The defenses above hold conditional on these assumptions. When any one becomes false, the threat model is stale.

1. Claude Code v2.1.x permission modes and hook event schemas remain as documented in the architecture reference (`research/Claude_Architecture.md`). The harness pins to a specific minor-version range to keep this stable.
2. The five tool-authorization hook events (PreToolUse, PostToolUse, PostToolUseFailure, PermissionRequest, PermissionDenied) fire as documented and cannot be silently disabled by a hostile setting.
3. Deny rules in `permissions.ts` evaluate before allow rules, in deny-first order. A broad deny always wins over a narrow allow.
4. The pre-commit framework actually runs the hooks declared in `.pre-commit-config.yaml`. A user who bypasses pre-commit (`git commit --no-verify`) defeats this assumption. The CI gate is the redundant defense.
5. The operating system on each of the three machines applies file permissions as expected. Hook scripts marked read-only stay read-only without Rock's deliberate intervention.

## What "deterministic" buys

The single most important design decision in the harness is the line between deterministic and advisory enforcement. Hooks are deterministic: they run regardless of the model's mood, the prompt context, or whether the model believes it understood the instruction. CLAUDE.md is advisory: the model reads it and incorporates it probabilistically. Anthropic's internal research, cited in the architecture analysis, found 93% approval rates on permission prompts, which means user vigilance cannot be the primary defense. The 0.4% false-positive rate of the auto-mode classifier, cited in the same source, is an acceptable trade for the threat coverage that `--dangerously-skip-permissions` gives up.

Every threat in this document is mitigated by one or more deterministic mechanisms. Advisory text in CLAUDE.md backs the determinism up; it does not substitute for it. When a phase prompt or harness component lands an instruction in CLAUDE.md that should also live in a hook, the Phase 5 Reviewer subagent flags the omission.

## How threats land in the build

Phase 1 (discovery) maps what's currently on the machine that could be exploited or that already protects against these threats. Phase 2 (architecture interview) explicitly asks which threats Rock wants to enforce in hooks versus accept as residual risk. Phase 3 (deterministic layer) writes the hook scripts and deny rules. Phase 4 (extension layer) adds the skills, agents, and MCP servers and stress-tests each against this document. Phase 5 (wire and document) closes the loop, with the Reviewer subagent checking every artifact against this threat model.

The threat model is a living document. Post-launch, every revision lands with a commit message that names the threat or assumption the change addresses.
