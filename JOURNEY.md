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

## October 30, 2026: Scratch roots stop prompting, rm gets a real deny, and the harness fails closed for real

The operator asked for one thing: writes under `/tmp` and `/private` must never prompt, including under `--dangerously-skip-permissions`. Investigation found that allow rules have no effect in bypass mode, so the only lever is the external-write gate's own `ask`, and that the gate's `$TMPDIR` exemption depended on the variable reaching the hook, which it does not when Claude Code starts from the Desktop app or launchd. The first landing widened the gate's scratch class to the whole of `/private`. An adversarial premortem the same day measured what that opened (persistent per-user application state under `/var/folders/.../0`, `C`, and `X`, and world-writable system directories such as `/var/db/mds` and `/var/OOPJit`) and the root was narrowed to `/tmp`, `$TMPDIR`, and the per-user temp directory that `getconf DARWIN_USER_TEMP_DIR` reports, which needs no environment variable. Pre-trust names under scratch (`.claude`, `.mcp.json`, `CLAUDE.md`, `.git`) stay gated. Matching `Read` and `Edit` allow rules carry the same decision in the modes that honor them. Rationale in `mac/harness/rules/filesystem-allow-scratch-roots.md`.

Two adjacent findings turned into the larger half of the change. The `Bash(rm -rf /:*)` family never matched root-prefixed paths: Claude Code reads `:*` as a trailing space-wildcard, so `rm -rf ~/<child>` and `rm -rf /tmp/<child>` both ran under the rules the documentation said covered them. A rule glob cannot distinguish a directory from its children, so enforcement moved to a new hook, `PreToolUse-bash-deny-rm-protected-paths.py`, whose protected set is the root, every top-level directory, homes, mounted volumes, the session cwd and its ancestors, credential stores, and the config files that make the harness enforce anything. The premortem reproduced bypasses in the first draft through wrappers (`timeout`, `nice -n 5`), `cd` chains, dot-globs, case-folded spellings, the bare Data volume, and the config root itself, and every one is now a row in a committed test matrix under `mac/harness/hooks/tests/`. The five dead `Write(path)` rules in the Mac source settings were removed because Claude Code matches file permissions against `Edit(path)` and `Read(path)` only.

The finding with the widest blast radius was about the runtime, not the change. A hook that cannot start, times out, exits non-zero, or prints invalid JSON has always been a non-blocking error, and Claude Code 2.1.295 added the first way to change that, the `onFailure: "block"` registration key. The harness asserted AP.8 (fail closed) in prose while every registration used the default. The four destructive-class hooks now carry the flag, run under `python3 -I` so a planted module cannot shadow the standard library, and the two newest exit 2 on any internal error. `foundation/01-threat-model.md` T.7 records it, and `_claude_code_hook_onfailure_floor` in `settings.json` records the version floor for QC.5. The reversibility principle that every gate cites as "Principle 3" had no section in `foundation/02`. It is now AP.11. `/etc` and `~/.ssh` write denials, which existed only as advisory files under `~/.claude/rules/`, are now enforced `Edit` deny rules with a rationale document. The Mac `settings.json.template` now registers the same hooks as the reference build, and `scripts/deploy-harness.sh` prefers `settings.json` for the Mac as its own comment always said.

Jetson received every part of the change in the repository: the hooks and tests byte-identical, the rule documents, the template with the allow rules, the fail-closed registrations, and the CLAUDE.md paragraph on the autonomous flag. Deployment to the device itself is a runbook, `jetson/prompts/patch-scratch-roots-and-rm-protected-paths.md`, on the pattern of the managed-store port. Windows stays a scaffold with an AP.3 exception recorded in its ARCHITECTURE.md. Still open: a drift-check item that diffs hook registrations across the reference file, the template, and the live settings, and one that verifies every rule document is cited (the rules README claimed one that did not exist). The rule-layer spot checks in a live `default`-mode session. A `ConfigChange` gate that can block on an unaudited settings file, since a SessionStart hook can only flag. A launcher for unattended `-p` runs that passes `--settings` explicitly before `--bare` becomes the `-p` default. A session-start probe that proves the four gates can start and that the running version meets the 2.1.295 floor. And the five older hooks that still cite "Threat actors #N", a Phase 2 vocabulary with no section in the threat model. A second premortem round against the remediated tree reproduced a further set of bypasses (here-strings and pipes into a shell, `for` loops, aliases, uppercase `RM`, brace lists, `~/**/*`, parameter expansions, `mv` and `unlink` of credentials, an in-cwd symlink escaping the write gate, and unprotected `skills`, `agents`, and `mcp.json` under the config root), all closed and added to the matrices before the commit. The premortem record is `operations/11-scratch-roots-and-rm-premortem.md`.

---

## Template for future entries

```
## Month Day, Year: Short title

One to three paragraphs describing what changed, what was decided, and what's still open. If the entry resolves a question, link to the commit. If it opens a new one, mark it explicitly so the foundation docs can track it.
```
