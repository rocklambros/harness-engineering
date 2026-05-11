# Security Policy

This repo is a public reference for a personal Claude Code harness. It contains configuration, prompts, and rationale documents, not a runtime service. The vulnerability surface is correspondingly narrow, and so is this policy.

## Scope

In scope:

- Hook scripts, deny rules, and sandbox configuration in `mac/`, `jetson/`, and `windows/` that could mishandle untrusted input.
- The drift-check script and any helper scripts under `scripts/`.
- Foundation documents (`foundation/`) that prescribe security-critical decisions; factual errors that would mislead an implementer count as security issues.
- Reference to CVE classes (CVE-2025-59536, CVE-2026-21852, CVE-2025-54794, CVE-2025-54795) in the threat model that have become inaccurate or stale.

Out of scope:

- Claude Code itself. Report Claude Code vulnerabilities to Anthropic directly. This repo is not a runtime and does not modify Claude Code.
- Third-party seeds referenced in the seed evaluation documents. Report those upstream.
- Cosmetic issues, typos, and style preferences. Open a normal issue.
- Speculative threats not grounded in a specific behavior of code or documentation in this repo.

## Reporting

Email `security@rockcyber.com` with:

- A summary of the issue in one sentence.
- The specific file, line, or document section affected.
- Why it is a security issue. The threat model in `foundation/01-threat-model.md` is the reference frame.
- A reproduction, if applicable.

Do not file a public GitHub issue for in-scope vulnerabilities until a fix has landed. For out-of-scope or ambiguous issues, a regular issue is fine.

## Response

Triage response within five business days of receipt. The five-day target reflects this being a personal project, not a commercial service. If the issue is genuinely time-critical, mark the email subject `[security][urgent]` and the response window tightens.

After triage, expect one of three outcomes:

1. **Accepted, fix planned.** A commit lands addressing the issue, the commit message follows the project template, and the reporter is acknowledged in the commit if they want to be.
2. **Accepted, won't fix.** The issue is real but the cost of fixing exceeds the cost of accepting. The reasoning lands in `foundation/01-threat-model.md` or a similar document so the residual risk is on the record.
3. **Rejected.** The issue is out of scope or not actually a vulnerability. The response explains why.

Coordinated disclosure on accepted issues: 30 days from the first response to public disclosure unless the reporter and I agree to a different window.

## Bounty

There is no bounty program. This is a personal project. Acknowledgment in the commit message and in this section's hall-of-fame block (when one exists) is the available recognition.

## Reference

This policy is the minimum form of NIST SP 800-218 v1.1 practice RV.1.3 (Establish a vulnerability disclosure program). The broader threat model and harness security posture live in `foundation/01-threat-model.md` and `foundation/00-quality-contract.md`.
