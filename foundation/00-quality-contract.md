# Quality Contract

Every artifact in this repo binds to these five properties. Commits reference them by ID (QC.1, QC.2, QC.3, QC.4a, QC.4b, QC.5) in the rationale block. Phase prompts cite them in deliverable acceptance criteria. Skills, hooks, and rules trace to them.

If a proposed change conflicts with one of these, the conflict is named explicitly and either resolved or accepted with a rationale recorded in JOURNEY.md and the relevant commit.

---

## QC.1 Security

The harness aligns to NIST SP 800-218 Secure Software Development Framework practices. Specifically: PO.1.1 (define security requirements), PS.1.1 (protect all forms of code from unauthorized access), PW.5.1 (create source code by adhering to secure coding practices), PW.7 (review and analyze human-readable code), PW.8 (test executable code), RV.1.3 (collect, maintain, and share vulnerability information).

Concrete implementation:

Dependencies pin to exact versions. No floating ranges in `requirements.txt`, `pyproject.toml`, `package.json`, or platform equivalents.

SBOM generation runs on every release. CycloneDX format, attached as a release artifact.

Secret scanning runs in CI and at pre-commit. Gitleaks at minimum, with optional supplementary scanners per platform.

SAST runs at three layers. Pre-generation guidance flows through the `security-review` skill. Commit-time hardening runs through a PostToolUse hook that feeds Semgrep findings back to Claude during the same session. Post-generation validation runs the full SAST stack at the pre-commit gate.

A vulnerability disclosure policy exists in `SECURITY.md`. Acknowledgment within 72 hours, coordinated disclosure on a 90-day default window.

This contract is informed by two pieces of research that bear citation. The Liu et al. SecureForge work (MIT, arXiv:2605.08382) shows that frontier models including Claude Sonnet 4.6 produce statically-verifiable vulnerabilities at roughly 23% on benign coding prompts even when explicitly asked to write secure code. The Arcanum-Sec sec-context taxonomy (CC BY 4.0) catalogs the specific anti-patterns where this manifests in published AI-generated code. The three-layer defense in this harness exists because neither pre-generation guidance alone nor post-generation validation alone closes the gap that data describes.

---

## QC.2 Tight code

Avoid speculative scope expansion. When asked to fix one thing, fix only that thing. When asked to add a feature, add the smallest version that meets the requirement.

This is not "never refactor adjacent code." That distinction matters. Adjacent refactoring is allowed when it's necessary to land the requested change cleanly. It's not allowed as a parallel improvement project tacked onto a focused task.

Concrete rules:

Avoid speculative generality. No interfaces for one implementation. No abstraction layers for one consumer. No configuration knobs for one setting.

No dead code paths. If a branch isn't reachable, delete it. If it's reachable only by configuration that doesn't exist, delete it and add the configuration later when the use case appears.

Prefer the explicit over the clever. A four-line function that clearly does one thing beats a one-line list comprehension that does three.

This block matches the Anthropic anti-overengineering guidance in spirit. Phase prompts that produce code include the verbatim block from Anthropic's prompting documentation.

---

## QC.3 Comments

Comment the why, not the what. If a reader needs the what explained, the names or structure are wrong. Fix those first.

Comment thresholds:

Non-obvious algorithmic choices get a why comment. (Why MCMC over rejection sampling? Why GEPA over MIPRO?)

Cross-cutting constraints get a why comment. (Why this directory excluded from Semgrep? Why this hook runs synchronously?)

External-facing behavior changes get a why comment, especially if the behavior was inherited from upstream and we're consciously diverging.

Project files in `mac/harness/`, `jetson/harness/`, `windows/harness/` may override this default for their specific scope. Overrides are documented in the project's `CLAUDE.md`.

---

## QC.4a Cache discipline

Applies to direct Anthropic API and SDK use, not to Claude Code sessions themselves. Claude Code manages its own caching internally.

When generating code that calls the API or SDK directly:

Set `cache_control.ttl` to `"1h"` explicitly on system prompts and stable prefixes where reuse is expected. The default changed in March 2026 from 1h to 5m. Code that relied on the implicit 1h is silently expensive now.

Telemetry off also kills the 1h TTL silently. If your config sets telemetry off, you must set `"ttl": "1h"` explicitly or accept the 5m default.

Per-model cache isolation matters. Opus and Haiku do not share cache. Subagent model selection affects cache economics. Document the model choice in the calling code.

Cache checkpoints have a 1024-token minimum. Prefixes shorter than that don't cache. If you need caching on a short prefix, pad with stable content or restructure.

---

## QC.4b Context window discipline

Applies to all Claude Code sessions running against this repo.

CLAUDE.md hierarchy total (root plus subdirectory CLAUDE.md files in scope) stays under 400 lines. Target 250.

Cache-eligible content lives in the prefix. Changing data goes in `<system-reminder>` blocks. No timestamps, run IDs, session-specific paths, or other per-run state in cached content.

Skills lazy-load on demand. The `security-review` skill in particular is large (the underlying sec-context taxonomy is ~165K tokens combined) and must not be loaded wholesale.

Each line in a CLAUDE.md passes the removal test: would removing it cause Claude to make mistakes? Anything Claude does correctly without the instruction comes out.

MCP server lists do not live in CLAUDE.md. Tools defer and load on demand via the tool search mechanism.

---

## QC.5 Versioning posture

The harness pins to a Claude Code minor-version range. The pin is recorded in `mac/harness/CLAUDE.md` status section and in equivalent files for Jetson and Windows.

Re-evaluation triggers on minor-version bumps:

The Quality Contract is reviewed for any property that depends on Claude Code internals (cache TTL behavior, hook event semantics, permission mode behavior).

The SecureForge-style pipeline is re-run against representative workload to check whether the model's failure distribution has shifted enough to warrant a refresh of the `security-review` skill content.

Hook event coverage is verified against the current Claude Code event list (Liu et al. catalog 12 to 21 events depending on count method, evolving).

Patch-version bumps don't trigger re-evaluation by default but are noted in the JOURNEY entry that covers the bump.

---

## How the Quality Contract is enforced

Phase prompts in `*/prompts/` reference QC properties in their deliverable criteria.

Commit messages reference QC properties in the rationale block (the Why field of the commit template).

The `scripts/drift-check.sh` script runs at pre-commit and checks for drift between cited QC properties and the actual artifact content.

Seed evaluations in `*/evaluations/` score candidate tools against the QC properties as part of the deep-eval rubric.

When a QC property changes, the change is its own commit, with full rationale, and a JOURNEY entry. The downstream artifacts that reference the changed property are updated in follow-up commits, traced back to the QC change by commit reference.
