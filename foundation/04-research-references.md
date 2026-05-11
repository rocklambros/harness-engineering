# Research References

Three documents ground this repo. They live in `research/` and the repo cites them by section when a specific fact lands in a phase prompt, a foundation document, or a commit message. This file is the index: what each source is authoritative on, what kind of claim cites which document, and the citation conventions used in commits and prose.

The discipline is straightforward. If a fact in any artifact in this repo comes from one of these sources, the artifact cites the source by document name and section. If a fact lives somewhere else (Anthropic blog posts, vendor docs, practitioner repos), the artifact names the URL or the repo. If a claim cannot be sourced, it does not get written.

## research/Claude_Architecture.md

Liu et al., reverse-engineering study of Claude Code v2.1.88. Published 2026. Authoritative on the source-level behavior of Claude Code at that version.

Cite this document for:

- **Permission modes**: The seven modes (plan, default, acceptEdits, auto, dontAsk, bypassPermissions, bubble). Section 5.1.
- **Hook events**: The 27 events defined in the source, the 15 with rich output schemas, the five that participate in tool authorization (PreToolUse, PostToolUse, PostToolUseFailure, PermissionRequest, PermissionDenied). Sections 5.3 and 6.
- **Permission pipeline**: Deny-first evaluation, pre-filtering by `filterToolsByDenyRules()`, the four-path permission handler (coordinator, swarm worker, speculative classifier, interactive). Section 5.2.
- **Auto-mode classifier**: The `yoloClassifier.ts` flow, the TRANSCRIPT_CLASSIFIER feature flag, the 0.4% false-positive rate (Hughes, 2026). Section 5.3.
- **CVE classes**: CVE-2025-59536 (CVSS 8.7), CVE-2026-21852 (CVSS 5.3), CVE-2025-54794, CVE-2025-54795. Pre-trust initialization ordering. Section 5.4 and footnote 3.
- **50-subcommand bypass**: The Adversa.ai 2026 finding that >50 subcommands fall back to a single approval prompt. Section 5.4.
- **Compaction pipeline**: Five-layer compaction, the PreCompact and PostCompact hook events. Section 7.
- **Subagent delegation**: The Task tool, worktree isolation, the SubagentStart and SubagentStop events. Section 8.
- **The 1.6% / 98.4% codebase ratio**: Decision logic versus operational harness. Section 4.
- **The 27 hook events list**: Tool authorization, session lifecycle, user interaction, subagent coordination, context management, workspace events, notifications. Section 6.1.

Citation form in this repo:
> *(Claude_Architecture.md §5.3)*

## research/Harness_Engineering_for_Claude_Code_A_Systems_Architecture_Analysis.md

The "SAGE doc." Lambros and Claude, 2026. Authoritative on the working definition of harness engineering, the distinction from adjacent terms, and the nine-component decomposition.

Cite this document for:

- **The working definition** of a Claude harness as a deterministic software envelope. Section 2.1.
- **The Bayesian confidence rating** on the term (roughly 0.7). Section 2.1.
- **Distinction from agent scaffolding, agentic runtime, agent framework, and eval harness**. Section 2.2.
- **The strongest counterargument** that harness engineering is a marketing rebrand of scaffolding. Section 2.3.
- **The nine components**: agent loop, instruction layer, tool pool, permission layer, context pipeline, sandbox, MCP integration, subagent delegation, persistence. Section 4.
- **The five tradeoffs**: latency vs. accuracy, autonomy vs. control, context economy vs. capability, extensibility vs. attack surface, capability vs. reliability. Section 5.2.
- **Design principles from the primary literature**: Schluntz and Zhang's four, Rajasekaran's five, the Liu et al. derivation of 13 from five values. Section 5.1.
- **Security and governance**: Owasp Agentic Top 10, OWASP LLM Top 10, NIST AI RMF, MITRE ATLAS, ISO 42001 cross-walks. Section 7.
- **Practical recommendations** for a personal harness. Section 9.

Citation form in this repo:
> *(SAGE §2.1)*

## research/NIST_SP_800-218-Secure-Software-Development-Framework.md

NIST SP 800-218 v1.1, Secure Software Development Framework. Authoritative on the four practice groups and individual practice IDs that the harness aligns with.

Cite this document for:

- **The four practice groups**: PO (Prepare the Organization), PS (Protect the Software), PW (Produce Well-Secured Software), RV (Respond to Vulnerabilities). Section 2.
- **Specific practice IDs** when a QC property or phase prompt requirement maps to a practice. Common ones used in this repo:
  - **PO.1.1**: Define security requirements for software development.
  - **PS.1.1**: Protect all forms of code from unauthorized access and tampering.
  - **PS.2.1**: Provide a mechanism for verifying software release integrity.
  - **PS.3.1**: Archive and protect each software release.
  - **PW.4.1**: Acquire and maintain well-secured software components.
  - **PW.5.1**: Create source code by adhering to secure coding practices.
  - **PW.7.1**: Configure the compilation, interpreter, and build processes.
  - **PW.8.2**: Design and perform testing.
  - **RV.1.1**: Gather information from software acquirers, users, and public sources on potential vulnerabilities.
  - **RV.1.3**: Establish a vulnerability disclosure program. (Cited by `SECURITY.md`.)
  - **RV.2.1**: Analyze each vulnerability to gather sufficient information.

Citation form in this repo:
> *(NIST SP 800-218 PW.5.1)*

## What is not authoritative

Sources outside this list are evidence, not authority. Anthropic blog posts on Claude Code best practices, practitioner repos (`obra/superpowers`, `affaan-m/everything-claude-code`, `disler/claude-code-hooks-mastery`), vendor documentation, and Hacker News discussion threads can appear in phase outputs and rationale documents, but they do not have the standing to override a claim in the three authoritative documents above.

When the authoritative documents disagree (which happens, especially on counts: the Architecture doc lists 27 hook events, public Claude Code docs at various times have cited 12-21 depending on what they were counting), the repo cites both numbers, names the discrepancy, and uses whichever count fits the question being asked.

## When sources go stale

The Claude Code architecture document is a snapshot of v2.1.88. When Claude Code ships a minor or major version bump, the document is not automatically wrong, but specific claims about hook event schemas, permission modes, or the source-code organization may be. QC.5 (versioning posture) triggers a review of the architecture document on every Claude Code minor bump. The NIST SP 800-218 reference is v1.1; if NIST publishes v2 or v1.2, the cross-walks get reviewed. The SAGE doc is at version 0.1; the repo cites Section numbers, which should be stable through revisions.

The discipline: cite the section, not the page, so revisions stay easy to track.
