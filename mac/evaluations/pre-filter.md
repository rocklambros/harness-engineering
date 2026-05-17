# Stage 1 Pre-Filter Evaluations

This file holds the Stage 1 pre-filter results for every tool considered during the Mac harness build. Pre-filter is fast (30 seconds per tool) and intentionally harsh. The methodology is in `foundation/03-seed-evaluation-methodology.md`.

Each entry below is one candidate tool. The three gates are License, Architecture support, and Maintainership. Failure on any gate ends the evaluation.

---

## Template

```markdown
### Candidate: <name>

**Source**: <URL>

**License gate**: <pass | fail> — <one sentence>

**Architecture gate**: <pass | fail> — <one sentence>

**Maintainership gate**: <pass | fail | pass with flag> — <one sentence>

**Result**: <proceeds to deep evaluation | rejected at pre-filter>

**Notes**: <optional>
```

---

## Evaluations completed during the Mac build

### Candidate: Arcanum-Sec/sec-context

**Source**: https://github.com/Arcanum-Sec/sec-context

**License gate**: pass — CC BY 4.0, suitable for content reference with attribution.

**Architecture gate**: pass — text content, platform-agnostic.

**Maintainership gate**: pass with flag — 12 commits, single-org maintainership (Arcanum-Sec), 573+ stars, active 2025-2026. Flagged as single point of failure.

**Result**: proceeds to deep evaluation.

**Notes**: Deep evaluation in `deep-eval.md` scored 3+ across all dimensions. Adopted as content seed for the `security-review` skill.

### Candidate: Stanford SecureForge

**Source**: https://github.com/sisl/SecureForge ; paper at arXiv:2605.08382.

**License gate**: pass — MIT (confirmed May 16, 2026).

**Architecture gate**: pass — Python pipeline, runs anywhere Python and Semgrep run.

**Maintainership gate**: pass — Stanford SISL lab, multi-year track record.

**Result**: proceeds to deep evaluation.

**Notes**: Adopted as methodology (Appendix C commit-time hardening pattern) rather than artifact. Optimized prompts not adopted due to model-version and turn-count specificity.

### Candidate: Semgrep

**Source**: https://github.com/returntocorp/semgrep

**License gate**: pass — LGPL 2.1 for the engine, with rule packs under various licenses (most permissive). LGPL is compatible since we use the CLI, not embed library code.

**Architecture gate**: pass — runs on macOS, Linux (Jetson), and Windows (WSL2 recommended for full rule pack coverage).

**Maintainership gate**: pass — frequent commits, active rule-pack development, well-funded company backing.

**Result**: proceeds to deep evaluation. Adopted as the SAST engine for Layers 2 and 3.

### Candidate: gitleaks

**Source**: https://github.com/gitleaks/gitleaks

**License gate**: pass — MIT.

**Architecture gate**: pass — Go binary, cross-platform.

**Maintainership gate**: pass — active maintenance, single maintainer with established track record.

**Result**: proceeds to deep evaluation. Adopted for secret scanning at pre-commit and CI.

### Candidate: obra/superpowers

**Source**: https://github.com/obra/superpowers

**License gate**: pass — Apache 2.0.

**Architecture gate**: pass — agnostic skill pack.

**Maintainership gate**: pass with flag — single maintainer.

**Result**: proceeds to deep evaluation. Specific skills adopted on a case-by-case basis; the full pack is not bulk-imported.

### Candidate: cosai-oasis/project-codeguard

**Source**: https://github.com/cosai-oasis/project-codeguard

**License gate**: pass — Apache 2.0.

**Architecture gate**: pass — text content.

**Maintainership gate**: pass — multi-vendor consortium (OASIS).

**Result**: proceeds to deep evaluation. Referenced in `foundation/04-research-references.md`; specific patterns informed the `security-review` skill scaffolding.

---

## How to add an evaluation

Run pre-filter against the candidate. Add an entry under "Evaluations completed."

If the candidate fails pre-filter, the entry still goes in this file. The failure is informative for future evaluators considering the same tool.

If the candidate proceeds to deep evaluation, add a corresponding entry in `deep-eval.md` with the five-dimension scoring.
