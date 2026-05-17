# Stage 2 Deep Evaluation

This file holds the Stage 2 deep evaluations for candidates that survived the Stage 1 pre-filter. The methodology and scoring rubric are in `foundation/03-seed-evaluation-methodology.md`.

Each entry scores the candidate on five dimensions on a 1-5 scale: Capability fit, Quality Contract alignment, Integration cost, Replaceability, Maintenance burden. A candidate must score 3 or higher on every dimension to be adopted.

---

## Template

```markdown
### Candidate: <name>

| Dimension | Score | Notes |
| --- | --- | --- |
| Capability fit | <1-5> | <reason> |
| Quality Contract alignment | <1-5> | <reason> |
| Integration cost | <1-5> | <reason> |
| Replaceability | <1-5> | <reason> |
| Maintenance burden | <1-5> | <reason> |

**Decision**: <adopted | rejected | conditionally adopted>

**Integration details**: <where it lives in the harness, attribution requirements>
```

---

## Adopted candidates

### Candidate: Arcanum-Sec/sec-context

| Dimension | Score | Notes |
| --- | --- | --- |
| Capability fit | 3 | Right anti-pattern coverage. Delivery (165K-token markdown) does not fit our lazy-load model unless used as content seed. |
| QC alignment | 2 (4 as seed) | QC.4b fails on bulk load. Passes when used as content for a lazy-loaded skill. |
| Integration cost | 4 | Used as content seed for one skill. Pattern files rewritten to repo voice. |
| Replaceability | 5 | Reference content. Replacing means re-curating from primary sources. |
| Maintenance burden | 3 | Content drifts as CWE landscape shifts. Not a code dependency; content review cadence needed. |

**Decision**: adopted as content seed.

**Integration details**: `mac/harness/skills/security-review/`. Top-10 ranking from sec-context README informs the pattern file selection. CC BY 4.0 attribution maintained in `SKILL.md` and `README.md`. Deep-pattern content rewritten to repo voice during Phase 4 execution.

### Candidate: Stanford SecureForge

| Dimension | Score | Notes |
| --- | --- | --- |
| Capability fit | 3 | Methodology maps cleanly to T.1. Artifact (optimized prompts) does not fit our multi-turn agent context. |
| QC alignment | 4 | SARIF-compatible Semgrep output, pinned dependencies, well-documented. |
| Integration cost | 2 for full pipeline, 4 for Appendix C pattern | We adopt only the Appendix C commit-time hardening pattern. |
| Replaceability | 4 | The Appendix C pattern is generic to any SAST-feedback hook. Lock-in is minimal. |
| Maintenance burden | 3 | Pipeline ages with model versions. Appendix C pattern is stable. |

**Decision**: adopted as methodology, not as artifact.

**Integration details**: The `post-tool-use-semgrep.sh` hook in `mac/harness/hooks/` implements the Appendix C pattern using Semgrep. The optimized prompts from the paper are not adopted. The full SecureForge pipeline is reserved as a periodic re-evaluation tool that runs against Rock's actual workload on Claude Code minor-version bumps per QC.5.

### Candidate: Semgrep

| Dimension | Score | Notes |
| --- | --- | --- |
| Capability fit | 5 | SAST engine that catches our target patterns. Multi-language coverage. |
| QC alignment | 5 | SARIF output, version-pinned, deterministic exit codes, fail-closed semantics. |
| Integration cost | 5 | Single binary call, both as a PostToolUse hook and as a pre-commit hook. |
| Replaceability | 4 | Could be swapped with another SARIF-emitting tool. Rule packs are Semgrep-specific. |
| Maintenance burden | 3 | Active rule-pack development requires periodic review of pinned ruleset against repo behavior. |

**Decision**: adopted as SAST engine for Layers 2 and 3.

**Integration details**: `.pre-commit-config.yaml` at repo root pins Semgrep version. `mac/harness/hooks/post-tool-use-semgrep.sh` invokes Semgrep CLI on the changed file with the default and security-audit rule packs.

### Candidate: gitleaks

| Dimension | Score | Notes |
| --- | --- | --- |
| Capability fit | 5 | Built for secret detection at the git layer. Exactly the threat. |
| QC alignment | 5 | Pinned versions, deterministic exit codes. |
| Integration cost | 5 | Single pre-commit hook entry. |
| Replaceability | 4 | Several alternatives (trufflehog, detect-secrets). Migration cost is one config block. |
| Maintenance burden | 4 | Stable interfaces, infrequent breaking changes. |

**Decision**: adopted for secret scanning.

**Integration details**: `.pre-commit-config.yaml` registers gitleaks at v8.21.2. Project-specific patterns supplement the default ruleset via `mac/harness/rules/secrets.patterns` when needed.

---

## Pending evaluations

The seed list from Phase 2 includes additional candidates that have not been deeply evaluated yet:

- `affaan-m/everything-claude-code`
- `disler/claude-code-hooks-mastery`
- Anthropic official skills and plugins (specific selections)
- `MemPalace`
- `Serena`

These are pre-filter candidates pending Stage 2 evaluation. Evaluation lands when there is a specific harness gap a candidate could address, not as speculative adoption.
