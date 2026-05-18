# Jetson Harness Guide

The technical reference for the harness on NVIDIA Jetson AGX Orin. Read this after you understand the foundation docs and have read the Jetson `ARCHITECTURE.md`. For quickstart and daily operation, see `USER_GUIDE.md`.

## What the harness is

A configured Claude Code environment that enforces a Quality Contract through five layers (project CLAUDE.md, settings.json, deterministic rules, advisory skills, hooks and agents) and a three-layer security stack (pre-generation guidance, commit-time hardening, post-generation validation).

The harness is built, not adopted. The Jetson section reproduces the same capability surface as the Mac reference build using platform-appropriate tools. Cross-platform parity is the non-negotiable AP.3.

## The five layers

The architecture is documented in `ARCHITECTURE.md`. The shape is identical across platforms.

Layer 1 is the project-level CLAUDE.md (`harness/CLAUDE.md`). Advisory. Under 160 lines, hard cap 200. Seven sections: Role, code standards, security rules, core constraints, things that break, operational, status.

Layer 2 is `settings.json` (`harness/settings.json.template`). Deterministic. Configures permission modes, hook registrations, and trust-boundary policy. Jetson-specific deny entries cover `/proc/nvtegra/*`, `~/.nvidia-jetson/**`, and `nvpmodel -m`.

Layer 3 is the deterministic rules in `harness/rules/`. Path deny lists, command deny lists, secret patterns. Consumed by hooks, not interpreted by Claude. Jetson adds Tegra-specific path entries to the Mac baseline.

Layer 4 is the skills in `harness/skills/`. Advisory but lazy-loaded. The `security-review` skill is populated with ten pattern files matching its `SKILL.md` manifest. Content is byte-identical to the Mac reference build.

Layer 5 is the hooks and agents in `harness/hooks/` and `harness/agents/`. Hooks are deterministic. Agents are advisory and delegate-driven. Four agent definitions (security-reviewer, writer-reviewer, reviewer, inventory) are byte-identical to Mac.

## The three-layer security stack

The security architecture cuts across Layers 4 and 5.

**Layer 1 of the security stack** (pre-generation guidance) lives in `harness/skills/security-review/`. Loads lazily based on file type. Content informed by the Arcanum-Sec sec-context taxonomy (CC BY 4.0, attribution preserved). Surfaces high-frequency anti-patterns before code is written.

**Layer 2 of the security stack** (commit-time hardening) lives in `harness/hooks/post-tool-use-semgrep.sh`. Runs Semgrep on every Write or Edit and feeds findings back to Claude in the same session. Implements the SecureForge Appendix C pattern (MIT, Liu et al. 2026, arXiv:2605.08382). The paper measures a ~48% CWE-rate reduction from this layer alone.

**Layer 3 of the security stack** (post-generation validation) lives in `.pre-commit-config.yaml` at repo root. Same Semgrep tool, different invocation context. Supplemented by gitleaks for secrets and shellcheck for hook scripts.

Removing any of the three security layers weakens the others. The composition is binding per AP.2.

## Jetson tool versions

| Tool | Version | Install method | Path |
| --- | --- | --- | --- |
| Semgrep | 1.163.0 | pip (conda base + system Python 3.10) | conda and /usr/bin paths |
| gitleaks | v8.21.2 | Binary download | /usr/local/bin/gitleaks |
| shellcheck | 0.8.0 | apt | /usr/bin/shellcheck |
| pre-commit | 4.6.0 | pip (conda base) | conda bin |
| jq | system | apt | /usr/bin/jq |

The `install-harness-tools.sh` script in `scripts/` automates installation. All versions are pinned.

## Jetson-Mac hook divergences

Four of the eleven hook scripts have platform-specific changes. The remaining seven (all Python hooks) are byte-identical.

| Hook | Divergence | Reason |
| --- | --- | --- |
| post-tool-use-semgrep.sh | Removed pipx PATH prepend, updated error messages, added .cu/.cuh extensions, updated Semgrep version reference | Jetson uses conda PATH, apt for jq, and may have CUDA source files |
| pre-tool-use-shell-audit.sh | Updated jq install message | apt instead of brew |
| session-start.sh | Fixed awk version parsing ($1 vs $NF) | Bug fix: $NF grabs "Code)" not version number |
| pre-compact-preserve.sh | stat -c instead of stat -f | GNU stat vs macOS stat syntax |

The session-start.sh fix is also a bug in the Mac version. It is documented for upstream correction.

## Hook event coverage

The harness registers hooks on four Claude Code events:

`PostToolUse` on Write, Edit, and MultiEdit. Fires `post-tool-use-semgrep.sh` for commit-time hardening.

`PreToolUse` on Bash. Fires `pre-tool-use-shell-audit.sh` for shell audit logging.

`SessionStart`. Fires `session-start.sh` for drift check and Claude Code version check.

`PreCompact`. Fires `pre-compact-preserve.sh` to preserve active phase state across compaction.

Seven additional Python hooks provide supplementary enforcement: bash command capping, cached-prefix write gating, external write gating, git push force confirmation, supply-chain bash checks, Claude config auditing, and session log pruning.

## Build sequence

The Jetson build followed the same six-phase sequence as Mac. All phases are validated on Jetson AGX Orin hardware.

| Phase | Status | Artifacts |
| --- | --- | --- |
| Phase 0: Goals | Validated | `phase-outputs/PHASE_0_GOALS.md` |
| Phase 1: Discovery | Validated | `phase-outputs/INVENTORY.md`, `CONFLICTS.md`, `QUESTIONS.md` |
| Phase 2: Architecture | Validated | `phase-outputs/ANSWERS.md`, `ARCHITECTURE.md` updates |
| Phase 3: Deterministic | Validated | `harness/CLAUDE.md`, `settings.json.template`, `rules/*`, `hooks/*` |
| Phase 4: Extension | Validated | `skills/*`, `agents/*` |
| Phase 5: Wire and Document | Validated | Integration test, guides, SBOM, release tag |

## Versioning posture

The harness pins to Claude Code minor-version range v2.1.x. The pinned range is documented in `harness/CLAUDE.md` status section.

Minor-version bumps trigger Quality Contract re-evaluation per QC.5:

The cache TTL behavior is re-checked. The March 2026 regression is the canonical example of why this matters.

Hook event coverage is verified against the current event list.

The SecureForge methodology is optionally re-run against representative workload to see whether the model's failure distribution has shifted enough to refresh the `security-review` skill.

Patch-version bumps do not trigger formal re-evaluation but are noted in `JOURNEY.md`.

## How to update the harness

Updates are commits. Each commit follows the AP.5 template: phase or topic, Context, Decision, Why, Tradeoff.

The Why field cites the Quality Contract property or threat ID that justifies the change. The drift check verifies these citations resolve.

Cross-platform changes land as one commit when possible, with the rationale showing the equivalent change on each platform.

A change that affects only one platform is suspect and gets extra scrutiny per AP.3. Single-platform divergence requires an explicit rationale that survives review.

## Adopting the harness in a Jetson project

Copy `harness/` to the target project's repo root.

Copy `settings.json.template` to `.claude/settings.json` and replace `{{REPO_ROOT}}` with the absolute path to the target project.

Copy `.pre-commit-config.yaml` and run `pre-commit install`.

Run `pre-commit run --all-files`, `scripts/drift-check.sh`, and `shellcheck harness/hooks/*.sh` to verify the wiring.

The full walkthrough is in `USER_GUIDE.md`.

## Jetson-specific considerations

**CUDA source files.** The PostToolUse Semgrep hook includes `.cu` and `.cuh` in its extension allow-list. Semgrep scans these files with its default and security-audit rule packs. The `security-review` skill does not include CUDA-specific guidance patterns. This is an explicit scope decision from Phase 0.

**Power management.** `nvpmodel -m` is in the settings.json deny list. Read-only queries (`nvpmodel -q`, `jetson_clocks --show`) are allowed. Bare `jetson_clocks` is not denied because Claude Code's prefix-matching cannot distinguish it from `--show`. CLAUDE.md advisory guidance covers the gap.

**Tegra paths.** `/proc/nvtegra/*` and `~/.nvidia-jetson/**` are in the paths deny list. These are hardware configuration directories that should not be modified through Claude Code.

**GNU vs BSD.** All hooks use GNU coreutils syntax. If porting hooks from Mac, check `stat`, `awk`, `sed`, and `date` flag compatibility. The pre-compact-preserve hook and session-start hook each had one BSD-specific flag replaced during the Jetson build.

**Python environments.** The Jetson has two Python environments: system Python 3.10.12 at `/usr/bin/python3.10` and Anaconda Python 3.12.2. Semgrep is installed in both. Pre-commit runs from the conda base environment. The `VALIDATED_PYTHON` in the install script targets both.
