# Security Policy

This is a reference repository, not a production service. The artifacts describe how a Claude Code harness was built and reasoned about. Even so, security issues in the patterns, configurations, or example code matter, because people read this repo and adapt from it.

## Reporting a vulnerability

If you find a security issue in this repository's configuration, hooks, scripts, or example code, report it via one of the following channels.

Email: security at rockcyber dot com. PGP key fingerprint listed at https://rockcyber.com/security.

GitHub private security advisory: open one at https://github.com/rocklambros/harness-engineering/security/advisories/new.

I'll acknowledge receipt within 72 hours and aim to confirm or dispute the issue within 7 days. If the issue is real, I'll work with you on a remediation timeline and credit you in the fix commit unless you ask to remain anonymous.

## What's in scope

Misconfigurations in `settings.json.template` that would weaken trust boundaries if copied verbatim.

Hook scripts in `*/harness/hooks/` that could be bypassed, exploited, or fail silently in ways that would invalidate the security model.

Example code in `prompts/` or `evaluations/` that contains exploitable patterns even when the surrounding text frames them as guidance.

Documentation that misrepresents the security properties of upstream tools (Claude Code, Semgrep, gitleaks, the SecureForge methodology, the sec-context taxonomy) in ways that would mislead a reader into adopting an unsafe pattern.

## What's out of scope

Issues in the upstream tools themselves. Report those to their respective maintainers. This repo documents how those tools were composed, not their internals.

Theoretical attacks that require the reader to ignore explicit warnings in the relevant `ARCHITECTURE.md` or Quality Contract.

Issues in the three research documents in `research/`. Those are source materials, not authored by me.

## Disclosure timeline

I prefer coordinated disclosure with a 90-day window from acknowledgment to public disclosure, adjusted as needed for the severity and complexity of the fix. If you have a different expectation, say so in your initial report.

## Cryptographic verification

Releases (when they exist) are signed. The public key for tag signature verification is published at https://rockcyber.com/security.

Build provenance attestations are generated through the SLSA Level 3 pipeline configured in `.github/workflows/` once that pipeline lands. Until then, treat unsigned commits as advisory artifacts and verify against the documented reasoning in the commit message body.
