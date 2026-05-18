# JOURNEY

A running narrative of the harness build. Each entry is a checkpoint, not a status report. Reasoning lives here, decisions land in commits, locked decisions land in foundation docs.

The build ran on a fixed loop sourced from Superpowers (Jesse Vincent, `obra`, MIT, https://github.com/obra/superpowers): brainstorm the design, write a plan, implement, review before merge. README.md "How this repo was built" explains why. Entries below are checkpoints within that loop.

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

## May 18, 2026: Jetson AGX Orin build validated

The Jetson section graduated from scaffold to validated today. All six phases ran on the actual hardware: an NVIDIA Jetson AGX Orin running JetPack R36 (release 5.0), Ubuntu 22.04.5 LTS, aarch64, with 64GB RAM and a 3.6TB NVMe.

Phase 1 inventoried the platform and found four blockers: Semgrep, gitleaks, shellcheck, and pre-commit were all missing from the Jetson. The install-harness-tools.sh script resolved these. Phase 2 made nine architecture decisions, the most consequential being the dual-environment Semgrep install (conda base Python 3.12 and system Python 3.10 both at version 1.163.0) and gitleaks at /usr/local/bin/ instead of ~/.local/bin/. Phase 3 built the deterministic layer and discovered four portability issues in the Mac hooks. The session-start.sh awk version parsing bug (`$NF` grabs "Code)" from the `claude --version` output "2.1.143 (Claude Code)") exists in the Mac version too. The pre-compact-preserve.sh `stat` syntax difference (GNU `-c '%Y %n'` vs macOS `-f '%m %N'`) is the only purely functional divergence between the two platform copies. Phase 4 copied the security-review skill and agents byte-identical from Mac and validated that Semgrep rule packs (p/default: 1059 rules, p/security-audit: 225 rules) resolve identically on aarch64. Phase 5 produced the integration test (21 checks, all passing), the Jetson-specific USER_GUIDE and HARNESS_GUIDE, and the SBOM.

Open questions from this build:

The Mac session-start.sh version parsing bug should be fixed upstream. The Jetson copy has the fix. The Mac copy still uses `awk '{print $NF}'`.

CUDA-specific anti-patterns in the security-review skill remain out of scope per Phase 0. The PostToolUse hook scans `.cu` and `.cuh` files, but the skill does not load CUDA-specific guidance. This is a tracked follow-up if CUDA security patterns become a priority.

The `jetson_clocks` advisory gap remains. The command cannot be blocked by the settings.json deny list because prefix-matching cannot distinguish bare `jetson_clocks` (unsafe) from `jetson_clocks --show` (safe). CLAUDE.md advisory guidance is the current mitigation.

---

## Template for future entries

```
## Month Day, Year: Short title

One to three paragraphs describing what changed, what was decided, and what's still open. If the entry resolves a question, link to the commit. If it opens a new one, mark it explicitly so the foundation docs can track it.
```
