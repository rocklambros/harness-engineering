# JOURNEY

A running narrative of the harness build. Each entry is a checkpoint, not a status report. Reasoning lives here, decisions land in commits, locked decisions land in foundation docs.

## Format

Each entry has a date heading and a short prose block. No bullet lists except where they materially aid comprehension. Three to seven items max if bulleted.

If an entry resolves an open question, link to the commit that landed the decision. If an entry surfaces a new question, mark it explicitly so it can be tracked into a foundation doc revision.

---

## May 16, 2026: Repo seeded

Three batches of artifacts landed today. Batch 1 produced root files and `foundation/`. Batch 2 produced the Mac section in full, including the three-layer security stack derived from the SecureForge methodology (Liu et al., MIT) and the sec-context taxonomy (Arcanum, CC BY 4.0). Batch 3 produced Jetson and Windows scaffolding with Phase 0 through Phase 2 written and Phase 3 through Phase 5 marked for hardware validation.

Open questions surfaced during the build:

The sec-context content quality below the README is still unverified. Phase 4 seed evaluation will inspect three to four deep-pattern sections before deciding how much of the taxonomy to absorb into the `security-review` skill.

The SecureForge optimized prompts in the published paper target single-turn Python generation against specific model versions (GPT-5.4, Claude Sonnet 4.6). Those prompts will not be adopted directly. The pipeline methodology lands as a periodic re-evaluation task on Claude Code minor-version bumps per QC.5.

Cross-platform tool equivalency for the commit-time hardening hook is documented in each platform's ARCHITECTURE.md. Mac uses the standard Semgrep CLI. Jetson uses the same binary, scaffolded but unvalidated against the AGX Orin's environment. Windows uses Semgrep in WSL2 because the native Windows binary has spotty coverage on some rule packs. The Windows decision needs validation when ported.

---

## May 17, 2026: Foundation revision, portable Semgrep gate, Phase 4 populated

A repo-wide pass landed in eight commits. The foundation docs gained an explicit map from each Quality Contract property to NIST SP 800-218 practices and stable T.N threat identifiers that hooks and skills can cite. The ignore rules and the pre-commit pipeline were tightened to a pinned gate. The NIST research filename was aligned to the canonical dotted name that `scripts/pre-flight.sh` and `foundation/04-research-references.md` already used. The drift check was reoriented from line-count policing to reference integrity, checking research paths, QC IDs, threat IDs, and hook shellcheck, and made portable across the macOS ugrep, BSD awk, and gawk. It scans only git-tracked files so build-internal scratch cannot false-trip it.

The Semgrep gate was made portable and conda-independent so the pre-commit SAST layer no longer depends on a fragile interpreter environment. That fix landed through pull request 1 (merge `1e05ad1`).

Phase 4 for the Mac reference build is complete (commit `60d6f81`). The `security-review` skill is populated with ten pattern files that match its `SKILL.md` manifest exactly by filename, CWE identifier, and file-type trigger, plus the `security-reviewer` and `writer-reviewer` agents. This resolves the open question from the May 16 entry on sec-context content quality. The XSS, SQL injection, and hardcoded-secrets depth sections were assessed and are substantive. The taxonomy cites no Semgrep rule identifiers, so every Semgrep cross-reference was sourced from the official registry rather than from sec-context, and the taxonomy's unsourced figures were not propagated. Pattern prose is deliberately tight per the binding writing rules rather than padded to a line target.

Still open: the Jetson and Windows `security-review` skills remain scaffolds with identical structure, pending hardware validation. Cross-platform parity for the populated pattern content is the tracked follow-up.

---

## Template for future entries

```
## Month Day, Year: Short title

One to three paragraphs describing what changed, what was decided, and what's still open. If the entry resolves a question, link to the commit. If it opens a new one, mark it explicitly so the foundation docs can track it.
```
