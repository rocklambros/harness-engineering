# Research References

The artifacts in this repo are grounded in published research and primary documentation. This file catalogs the references that are cited across the foundation docs, phase prompts, and skill content. New references land here first, then get cited downstream.

References are organized by what they bind. A reference cited in foundation docs is authoritative for the entire repo. A reference cited only in a specific platform's `evaluations/` folder binds only that evaluation.

---

## R.1 Claude Code architecture and behavior

### R.1.1 Liu et al., Reverse engineering Claude Code v2.1.88

Internal location: `research/Claude_Architecture.md` (after pre-flight).

Authoritative on: Claude Code permission modes, hook events (12 to 21 depending on count method), the compaction pipeline, the 50-subcommand bypass class, and the CVE classes documented in the analysis.

Cited from:

- `foundation/01-threat-model.md` (T.4, hook bypass)
- `foundation/02-architectural-principles.md` (AP.1, deterministic over advisory)
- `mac/ARCHITECTURE.md` (permission mode rationale, hook event coverage)
- `jetson/ARCHITECTURE.md` (same)
- `windows/ARCHITECTURE.md` (same)

When citing, reference the relevant section heading. Direct quotes are kept under 15 words per QC and copyright requirements.

### R.1.2 Anthropic Claude Code documentation

External location: https://code.claude.com/docs

Authoritative on: official feature behavior, settings.json schema, hook registration syntax, MCP server configuration.

Cited from phase prompts and the harness CLAUDE.md files. Used in evaluations to verify behavior claims against official documentation.

### R.1.3 Anthropic prompt engineering documentation

External location: https://docs.claude.com/en/docs/build-with-claude/prompt-engineering

Authoritative on: Opus 4.7-specific guidance (literal instruction-following, scope discipline, parallel tool calls), the verbatim anti-overengineering block, AskUserQuestion tool usage, adaptive thinking, plan mode semantics.

Cited from: all phase prompts in `*/prompts/`.

---

## R.2 Security research on AI-generated code

### R.2.1 SecureForge (Liu, Einstein, Yang, et al., 2026)

Citation: Houjun Liu, Lisa Einstein, John Yang, Joachim Baumann, Duncan Eddy, Christopher D. Manning, Mykel Kochenderfer, Diyi Yang. SecureForge: Finding and Preventing Vulnerabilities in LLM-Generated Code via Prompt Optimization. arXiv:2605.08382v1, May 2026.

License: MIT (confirmed source code at https://github.com/sisl/SecureForge).

Internal location: paper attached during build, methodology referenced; source code not embedded.

Authoritative on:

The benign-prompt vulnerability rate measurement: ~23% on frontier models including Claude Sonnet 4.6 even when explicitly asked for secure code.

The MCMC amplification methodology for failure-distribution discovery.

The GEPA-based system-prompt optimization technique.

The Appendix C commit-time hardening pattern: feed Semgrep findings back to the model with line and rule context for in-session fix, iterate until clean or retry cap.

The transferability data: optimized prompts transfer zero-shot to in-the-wild SWE-chat prompts.

Cited from:

- `foundation/00-quality-contract.md` (QC.1, the data justifying the three-layer defense)
- `foundation/01-threat-model.md` (T.1, benign vulnerability generation)
- `foundation/02-architectural-principles.md` (AP.2, three-layer security)
- `foundation/03-seed-evaluation-methodology.md` (worked example)
- `mac/prompts/phase-3-deterministic-layer.md` (the PostToolUse Semgrep hook implementation)
- `mac/harness/hooks/post-tool-use-semgrep.sh` (in-file comment citing Appendix C)

Methodology adopted, optimized prompts not adopted. Rationale in seed evaluation methodology doc.

### R.2.2 Arcanum-Sec sec-context taxonomy

Citation: Jason Haddix, Arcanum Information Security. AI Code Security Anti-Patterns. https://github.com/Arcanum-Sec/sec-context. Synthesizes 150+ sources across academic papers, CVE databases, security blogs, and developer communities.

License: CC BY 4.0.

Internal location: referenced externally, not embedded. Pattern selection and ranking inform the `security-review` skill content.

Authoritative on: the AI-code anti-pattern taxonomy, the top-10 ranking by frequency-severity-detectability score, and the supporting research citations (which are themselves valuable for verification).

Cited from:

- `foundation/00-quality-contract.md` (QC.1, the empirical basis for the pre-generation guidance layer)
- `foundation/01-threat-model.md` (T.1, severity data)
- `foundation/03-seed-evaluation-methodology.md` (worked example)
- `mac/harness/skills/security-review/SKILL.md` (attribution and pattern source)

Specific statistics from the README are cited with care. Some are well-supported primary research findings (slopsquatting rates from academic literature), others are looser developer-survey aggregates. Citations within the skill content note which is which.

### R.2.3 Harness Engineering for Claude Code: A Systems Architecture Analysis (SAGE)

Internal location: `research/Harness_Engineering_for_Claude_Code_A_Systems_Architecture_Analysis.md` (after pre-flight; original filename has a space that gets normalized).

Authoritative on: the harness engineering definition, the Quality Contract framework, OWASP and NIST cross-walks, and the architectural shape of a production harness.

Cited from:

- `foundation/00-quality-contract.md` (QC.1 framework provenance)
- `foundation/02-architectural-principles.md` (AP.1, AP.2 framing)
- All platform `ARCHITECTURE.md` files (harness layer definitions)

---

## R.3 Standards and frameworks

### R.3.1 NIST SP 800-218 Secure Software Development Framework

Internal location: `research/NIST.SP.800-218-Secure-Software-Development-Framework.md` (after pre-flight).

Authoritative on: SSDF practice IDs (PO.1.1, PS.1.1, PW.5.1, PW.7, PW.8, RV.1.3) that the harness aligns to.

Cited from:

- `foundation/00-quality-contract.md` (QC.1 SSDF alignment)
- `mac/prompts/phase-3-deterministic-layer.md` (practice IDs in deliverable criteria)
- `jetson/prompts/phase-3-deterministic-layer.md` (same)
- `windows/prompts/phase-3-deterministic-layer.md` (same)

Practice IDs are cited directly, not paraphrased.

### R.3.2 MITRE Common Weakness Enumeration (CWE)

External location: https://cwe.mitre.org

Authoritative on: CWE IDs referenced in the `security-review` skill and in evaluations of SAST tool coverage.

The CWE Top 25 list is the practical baseline for what the SAST stack must cover. The 2024 release is current as of build time.

### R.3.3 CISA Secure by Design Pledge

External location: https://www.cisa.gov/securebydesign/pledge

Authoritative on: the framing for secure-by-design as a development practice rather than an after-the-fact check. Cited in the threat model and architectural principles.

---

## R.4 Reference repositories

These are the public repositories whose patterns informed the harness shape. They are not dependencies. They are exemplars.

### R.4.1 rocklambros/zerg

External location: https://github.com/rocklambros/zerg

Used for: README pattern (Why I Built This framing), CLAUDE.md pattern, voice and tone for first-person educational content.

### R.4.2 rocklambros/TRACT

External location: https://github.com/rocklambros/TRACT

Used for: the seven-section CLAUDE.md pattern (Role, code standards, security, constraints, things-that-break, operational, status). The section structure is borrowed from this repo's TRACT acronym and applied here with the same shape.

### R.4.3 Seed candidates evaluated

The following tools were considered as seeds during the build. Each is evaluated in `mac/evaluations/` or platform-equivalent against the methodology in `foundation/03-seed-evaluation-methodology.md`.

obra/superpowers, affaan-m/everything-claude-code, cosai-oasis/project-codeguard, disler/claude-code-hooks-mastery, anthropics/claude-code official skills and plugins, semgrep, gitleaks, trivy, syft, grype, cyclonedx-cli, sigstore/cosign, OSV-Scanner, detect-secrets, MemPalace, Serena.

---

## How references get added

New research lands in `research/` (if it's a document) or is referenced externally (if it's a repo or documentation site).

The reference is added to this file with citation, location, authoritative-on summary, and cited-from list.

Citations in downstream files use the reference ID (R.1.1, R.2.2, etc.) where unambiguous, or full citation where the reader needs the context.

When a reference is superseded, the entry is updated with a note pointing to the new reference. The old entry is not deleted; the reasoning chain may still depend on it.
