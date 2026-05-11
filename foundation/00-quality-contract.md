# Quality Contract

The Quality Contract binds every phase of the build and every artifact in this repo. Five properties. Each one names a failure mode that recurs in Claude Code harness work and the discipline that prevents it. Phase prompts reference this document by section. Commit messages cite the QC ID when a decision turns on one of these properties.

The contract is short on purpose. A long contract becomes wallpaper. These five carry their weight.

## QC.1 Security

The harness aligns with NIST SP 800-218 Secure Software Development Framework (SSDF) v1.1. The four practice groups (Prepare the Organization, Protect the Software, Produce Well-Secured Software, Respond to Vulnerabilities) map to concrete obligations in this repo:

- **PO**: Documented secure development practices live in `foundation/` and in `mac/ARCHITECTURE.md`. Toolchain choices include a recorded rationale.
- **PS**: Software components are protected from tampering. Dependencies are pinned to specific versions, not floating ranges. A Software Bill of Materials (SBOM) is generated for each release. Secret scanning runs in pre-commit and CI.
- **PW**: Static analysis runs against any executable code added to the repo. Hook scripts and helper scripts pass shellcheck. Skills with executable bodies pass language-appropriate SAST. Code review by a Reviewer subagent happens before any wiring change lands.
- **RV**: A Vulnerability Disclosure Policy is published in `SECURITY.md` (RV.1.3). Issues filed against this repo get a triage response within five business days.

The harness is not a product, but it touches code, secrets, and execution permissions on three machines. Treating it as if it were a product is the cheapest way to keep the threat model from drifting.

## QC.2 Tight code

Avoid speculative scope expansion. When a phase produces code or configuration, the output addresses the specified deliverable and nothing else. New files, new dependencies, new abstractions, and new test scaffolding all require an explicit decision recorded in the phase output or commit message.

The discipline is verbatim from Anthropic's guidance on Claude Code: stay focused on the explicit task, do not edit unrelated areas of the codebase, refrain from creating new abstractions or test files unless required by the prompt.

The discipline is **not** "never refactor adjacent code." Refactoring adjacent code is sometimes the correct move and sometimes is what the phase explicitly asked for. The rule is that scope expansion is a decision, not a habit. When the model expands scope on its own, the Reviewer subagent in Phase 5 flags it and the change either gets a rationale or gets reverted.

## QC.3 Comments

Comments explain the *why*, not the *what*. The code already shows what it does. The reasoning behind a non-obvious decision is what survives the next reader. When a phase prompt specifies a different commenting posture (terse, none, or specific format), the prompt overrides this default for files within its scope.

Comment density varies by file. A pinned dependency in `package.json` does not need a comment. A hook script that denies `Bash(prefix:rm)` does. A skill that triggers on a non-obvious phrase does. The Reviewer subagent checks that consequential decisions carry a why-comment and that obvious lines are not over-commented.

## QC.4a Cache discipline (API and SDK)

Applies to direct Anthropic API and Agent SDK use. The cache_control TTL default reverted from one hour to five minutes in March 2026. Any cache write expecting reuse beyond five minutes sets `"ttl": "1h"` explicitly. Telemetry-off also drops the 1h TTL silently, so cache-economy work happens with telemetry on.

The 1024-token minimum per cache checkpoint applies. Cache writes shorter than 1024 tokens silently fail to cache. Per-model cache isolation applies. Opus and Haiku do not share cache. Subagent model selection therefore affects cache economics, not just inference cost.

These caveats catch first-time API users by surprise. They cost real money over a build of this size, and the silent-failure modes are the most expensive ones.

## QC.4b Context window discipline (Claude Code)

Applies to every Claude Code session in this repo, on every platform.

The CLAUDE.md hierarchy across project root, harness directory, and any nested CLAUDE.md files stays under 400 lines total. Target 250. The drift check in `scripts/drift-check.sh` enforces this.

The cached prefix stays cacheable. No timestamps, no per-run state, no session identifiers in CLAUDE.md or anywhere else in the cached prefix. Changing data goes in `<system-reminder>` blocks, which sit outside the cached prefix and update freely.

Every phase prompt runs `/context` at start and at end, and the phase output records the delta. Context economy is a measurable property, not a vibe.

## QC.5 Versioning posture

The harness pins to a specific Claude Code minor-version range. On a minor-version bump, the harness gets re-evaluated against the new version before adoption. The current pin and rationale live in `mac/ARCHITECTURE.md` (and equivalents in `jetson/` and `windows/`).

Three things drive this. First, the permission model and hook event schemas evolve across Claude Code versions, and a working harness against v2.1.x can break against v2.2.x without warning. Second, the cache TTL default already shifted once in 2026, which would have invalidated cache economy assumptions silently if the harness had not been version-pinned. Third, every harness component encodes an assumption about model behavior, and assumptions go stale across model generations (this is documented in the SAGE analysis as the central lesson of Rajasekaran's harness retrospective).

When a Claude Code minor bump lands, the work is: re-read the changelog, re-run the seed evaluation pre-filter on anything new, validate the deny rules still match expected behavior, and update the pin. Cost is roughly one focused afternoon per bump.

---

## How violations are caught

QC.1: pre-commit hooks (secret scan, dependency lockfile check), CI SAST gate, SBOM diff on release.
QC.2: Reviewer subagent in Phase 5 scope check, manual review on every PR.
QC.3: Reviewer subagent in Phase 5, follow-up review on `git log -p` during dogfooding.
QC.4a: cache hit ratio in API logs, cost monitoring.
QC.4b: `scripts/drift-check.sh` in pre-commit and CI.
QC.5: Claude Code version recorded in every commit producing harness code; release notes monitored.

## When QC properties conflict

QC.2 (tight code) and QC.3 (comment the why) sometimes pull against each other when a refactor is justified by a non-obvious safety property. The resolution: the refactor lives in its own commit with the rationale in the commit message under "Why." The code itself stays tight.

QC.4a (cache economy) and QC.5 (re-evaluate on minor bump) pull against each other on the day after a Claude Code bump: the cache strategy may need to change, and short-term cache economy gets worse. QC.5 wins. Cache regressions get re-tuned, not rolled back.

When a real conflict shows up that this section does not name, the resolution becomes part of the commit record so the next reader sees how the decision was made.
