# Architectural Principles

The principles below bind every design decision in the harness. They sit above the Quality Contract: the QC defines what the artifacts must satisfy, the principles define why the artifacts are shaped the way they are.

## AP.1 Deterministic over advisory, always

Claude Code offers two enforcement surfaces for harness rules. CLAUDE.md and skills are advisory: the model reads them and is influenced by them, but compliance is probabilistic. Hooks and the permission system are deterministic: they execute regardless of what the model thinks.

When a rule matters, it goes in a hook or a permission check, not in CLAUDE.md. CLAUDE.md is for guidance the model should weight when there's ambiguity, not for rules that must not be broken.

This is the single most important architectural decision in the harness. Every Phase 3 deliverable starts from "which of these belongs in a hook." Phase 4 starts from "what does Claude need to know that isn't enforceable deterministically."

Source: Liu et al. Claude Architecture analysis, hooks section, and the SAGE harness engineering systems-architecture analysis.

## AP.2 Three-layer security, never one

Pre-generation guidance, commit-time hardening, and post-generation validation are three different defense layers. Each catches failures the others miss. The harness implements all three.

Pre-generation guidance (skills) shapes what Claude writes by loading anti-pattern context on demand. It catches the high-frequency low-novelty patterns at the cheapest layer.

Commit-time hardening (PostToolUse hooks running Semgrep on changed files) catches what slipped past the guidance, while Claude is still in the same session and can fix in place. This is the SecureForge Appendix C pattern adapted to a deterministic hook.

Post-generation validation (the full pre-commit SAST stack) catches what slipped past both, before the code lands in a commit.

Removing any one of the three weakens the others. The Liu et al. SecureForge research shows the three-layer combination outperforms any single layer at equivalent compute budget.

## AP.3 Cross-platform parity, not portability

Every capability that exists on Mac exists on Jetson and Windows. When the tool differs across platforms, the platform-specific equivalent is documented in that platform's `ARCHITECTURE.md` with a stated reason. This is parity, not portability: the code itself may differ, the capability does not.

This principle exists because the cost of inconsistent capabilities across machines is paid at session start, every session, forever. The harness is worth building precisely because that cost is being eliminated.

When a capability cannot be replicated cross-platform, the cross-platform constraint takes precedence: the capability is dropped from all three platforms, or the harness adopts an inferior tool that exists everywhere. Adding a capability to one platform while leaving the others without an equivalent is not allowed.

## AP.4 Reasoning is the artifact

Code in this repo is supporting evidence for the reasoning. Reasoning lives in `README.md`, `ARCHITECTURE.md`, foundation docs, commit messages, and JOURNEY entries.

This shapes how every artifact is written. Prompts in `prompts/` are long because they encode reasoning. Commits are long because the rationale block is mandatory. CLAUDE.md is short because reasoning belongs in foundation docs, not in cached prefix content.

A reader who reads only the code in this repo gets less than half the value. A reader who reads the reasoning chain and skims the code gets the full value.

## AP.5 Tight scope, every commit

Commits land one thing at a time. Mixed-purpose commits (refactor plus feature plus test) are not allowed. When a change requires three landings, it's three commits.

The commit template below is mandatory:

```
<phase or topic>: <one-sentence decision>

Context: <what was happening>
Decision: <what we chose>
Why: <reasoning, anchored in QC section or evidence>
Tradeoff: <what we gave up>
```

The rationale block (Context, Decision, Why, Tradeoff) is what makes the commit history a readable reasoning chain. Without it, the chain doesn't exist.

A commit that doesn't have a clear single decision is a sign that the scope of work was wrong. Split it.

## AP.6 Adopt where possible, build where necessary

The harness is built, not adopted. That's the framing of this entire repo. But within the harness, individual components are adopted where the upstream is healthy and the fit is good. Semgrep is adopted, not reimplemented. Gitleaks is adopted, not reimplemented. The Anti-Pattern taxonomy from sec-context is referenced and attributed, not duplicated.

The build-where-necessary criteria are: the upstream is unhealthy (single-maintainer, slow updates, license problems), the fit is wrong (designed for a different use case in a way that can't be reconfigured), or the integration cost exceeds the build cost.

The `seed evaluation methodology` in `03-seed-evaluation-methodology.md` is the rubric for these decisions.

## AP.7 Lazy load, never bulk import

Context window is the most expensive resource in a Claude Code session. The harness treats it accordingly.

Skills load on demand based on file type and task. The `security-review` skill loads anti-pattern context only when relevant files are touched, not at session start.

Research documents in `research/` are read on demand by phase prompts, not loaded into the session prefix.

MCP server tool descriptions defer until queried via tool search, not loaded at session start.

This principle is the practical application of QC.4b.

## AP.8 Fail closed, never silent

When a hook errors, the action is blocked. When a check is ambiguous, the agent stops and surfaces the ambiguity. When a tool reports a finding, the finding is reported, not summarized away.

The cost of fail-open is asymmetric: a missed finding can ship; a false positive costs a re-run. The harness optimizes for the catchable case.

This applies to hook scripts, SAST tool exit codes, the drift-check script, and the seed-evaluation rubric. A failure mode that gets logged but not surfaced is a failure mode.

## AP.9 Version pinning is part of the design

QC.5 requires pinning to a Claude Code minor-version range. The pinning is recorded in each platform's harness CLAUDE.md status section.

This is not paranoia. The March 2026 cache TTL regression is the canonical example of why: the default behavior changed silently, and every harness that didn't pin its assumptions paid the cost. Pinning isn't preventing the change. Pinning is making sure the change is visible.

Pinning also applies to security-tool versions (Semgrep, gitleaks, trivy, syft, grype) in `.pre-commit-config.yaml`. Tool behavior on rule packs changes between versions.

## AP.10 Public by default, born public

The repo is born public at the end of the build phase. There is no discrete "dogfood phase" separate from "publish phase." Dogfooding is continuous, post-launch revisions land as commits with full rationale.

This shapes what gets written: everything is written for a reader who is not the author. Private context, internal jokes, and shorthand do not appear. The voice is consistent across all artifacts because every artifact is public-facing.

The `JOURNEY.md` entries acknowledge that the build is in progress. They do not apologize for it.
