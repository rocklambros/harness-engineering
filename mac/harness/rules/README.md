# Rules

Deterministic policy that the hooks and Claude Code settings consult. The files in this directory are not interpreted by Claude itself. They are read by hook scripts and by the deny/allow lists in `settings.json.template`.

Per AP.1, rules that must not be bypassed live in this layer. Advisory guidance lives in the skills directory instead.

## Files

`paths.deny` — newline-separated path patterns that hooks block. Includes credential stores, system configuration, and user-secret directories. Loaded by `pre-tool-use-shell-audit.sh` and the deny list in `settings.json`.

`paths.allow` — explicit allow list for sensitive operations. Defaults to the user's working directory. Override when a project legitimately needs broader access.

`commands.deny` — patterns for shell commands that must be blocked at the harness layer (defense in depth, since `settings.json` also blocks these). Includes `curl | sh` family, `rm -rf` against system paths, `sudo *`.

`secrets.patterns` — regex patterns for detecting secrets in generated code. Supplementary to gitleaks. Add project-specific patterns here (internal API token formats, partner credential prefixes).

Note: each rule file is populated by Phase 3 against the specific Claude Code session needs. Initial templates are minimal. Extend through commits with rationale rather than freehand edits.

## How rules compose with skills

Rules say "this cannot happen." Skills say "here is what to do when this situation arises."

A rule that blocks `eval()` calls in Python is in `paths.deny` or a similar deterministic enforcement.

A skill that explains why `eval()` is dangerous and what to use instead lives in `harness/skills/security-review/patterns/command-injection.md`.

Both serve the same threat. Different layer, different mechanism.

## Updating rules

Changes to rules are commits with rationale. The Why field cites the threat ID or Quality Contract property that justifies the rule.

Removing a rule requires a stronger case than adding one. Document why the threat is now mitigated elsewhere (different layer, deprecated capability, accepted residual risk).

The drift check verifies rule files are referenced by at least one hook or settings entry. Orphan rules surface as drift.
