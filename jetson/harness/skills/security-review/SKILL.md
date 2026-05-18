---
name: security-review
description: Pre-generation security guidance for AI-generated code. Loads anti-pattern context on demand based on file type. Use whenever writing or editing source code, especially in Python, JavaScript, TypeScript, Go, Bash, Terraform, or SQL. The skill flags high-frequency vulnerability patterns before they ship: dependency risks (slopsquatting and confusion), cross-site scripting, hardcoded secrets, SQL injection, authentication failures, input validation gaps, command injection, missing rate limiting, data exposure through verbose errors or logs, and unsafe file upload handling.
---

# Security Review Skill

Pre-generation guidance for the three-layer security stack. Loaded lazily by file type. Pattern-specific content lives in `patterns/` and is read on demand, not bulk-loaded.

This is Layer 1 of the three-layer security stack defined in `foundation/02-architectural-principles.md` AP.2. The other two layers are commit-time hardening (the PostToolUse Semgrep hook) and post-generation validation (the pre-commit SAST stack).

## When this skill loads

Claude Code's skill discovery loads this skill when relevant file types are touched. Specifically:

For Python files (`.py`, `.pyi`): load `patterns/sql-injection.md`, `patterns/command-injection.md`, `patterns/input-validation.md`, `patterns/hardcoded-secrets.md`, `patterns/dependency-risks.md`.

For JavaScript and TypeScript files (`.js`, `.jsx`, `.ts`, `.tsx`): load `patterns/xss.md`, `patterns/input-validation.md`, `patterns/hardcoded-secrets.md`, `patterns/dependency-risks.md`, `patterns/auth-failures.md`.

For shell scripts (`.sh`, `.bash`): load `patterns/command-injection.md`, `patterns/hardcoded-secrets.md`.

For Terraform and infrastructure code (`.tf`, `.tfvars`, `.hcl`, `.yaml`): load `patterns/hardcoded-secrets.md`, `patterns/data-exposure.md`, `patterns/auth-failures.md`.

For SQL files (`.sql`): load `patterns/sql-injection.md`, `patterns/auth-failures.md`.

For files involving file upload, request handling, or API endpoints (matched by content heuristic, not extension): load `patterns/file-upload.md`, `patterns/rate-limiting.md`, `patterns/data-exposure.md`.

If a file type is not covered, the skill does not load. Add coverage by extending the pattern files with the new file-type mappings.

## Top patterns

The ten patterns covered here are ranked by frequency-severity-detectability score in the source taxonomy. Highest impact first:

`patterns/dependency-risks.md` covers slopsquatting (AI hallucinating package names that attackers register) and dependency confusion (internal-package-name attacks). CWE-1357, CWE-829.

`patterns/xss.md` covers reflected, stored, and DOM-based cross-site scripting. CWE-79.

`patterns/hardcoded-secrets.md` covers credentials, API keys, and tokens embedded in source. CWE-798, CWE-259.

`patterns/sql-injection.md` covers string-concatenation SQL, missing parameterization, and ORM misuse. CWE-89.

`patterns/auth-failures.md` covers missing auth checks, broken session management, and weak credential storage. CWE-287, CWE-306, CWE-384.

`patterns/input-validation.md` covers missing input bounds checks, type confusion, and validation bypass. CWE-20, CWE-1284.

`patterns/command-injection.md` covers shell injection, OS command injection, and unsafe subprocess invocation. CWE-77, CWE-78, CWE-94.

`patterns/rate-limiting.md` covers missing or bypassable rate limits on resource-intensive endpoints. CWE-770, CWE-307.

`patterns/data-exposure.md` covers verbose errors, debug endpoints in production, and over-fetching that leaks sensitive fields. CWE-200, CWE-209.

`patterns/file-upload.md` covers unsafe file type checks, path traversal in upload handling, and content-type confusion. CWE-434, CWE-22.

## How the skill works alongside the other security layers

This skill provides guidance that influences what Claude writes. It does not enforce anything.

When you write or edit a file, the `post-tool-use-semgrep.sh` hook runs Semgrep against the file (Layer 2). If Semgrep flags an issue, the hook surfaces it to you in the same session. Fix in place.

When you commit, the pre-commit hooks run the full SAST stack against the staged changes (Layer 3). If anything is flagged, the commit is blocked.

The three layers compose. None is sufficient alone. The SecureForge research (R.2.1) measures a ~48% CWE-rate reduction from the commit-time hardening layer alone, with the combined three-layer approach further reducing the residual.

## Attribution

This skill's pattern selection and ranking are informed by the Arcanum-Sec sec-context taxonomy, attribution to Jason Haddix and Arcanum Information Security. The taxonomy is licensed CC BY 4.0.

Source: https://github.com/Arcanum-Sec/sec-context

The methodology of feeding static-analysis findings back to the model for in-session fixes is adapted from:

Liu, H., Einstein, L., Yang, J., et al. (2026). SecureForge: Finding and Preventing Vulnerabilities in LLM-Generated Code via Prompt Optimization. arXiv:2605.08382. MIT License.

Pattern content in `patterns/` is rewritten to repo voice; the taxonomy and ranking are the attributed contribution.

## Status

Phase 4 complete on the Mac reference build. The ten pattern files in `patterns/` are populated and match the manifest above by filename, CWE ID, and file-type trigger. The `security-reviewer` and `writer-reviewer` agents are in `mac/harness/agents/`. Jetson and Windows carry the scaffold with identical structure, pending hardware validation.

The SKILL.md description above is the user-facing summary. Each pattern file lives independently and is loaded only when relevant.
