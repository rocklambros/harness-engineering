# Phase 4: Extension Layer

This phase builds the advisory guidance layer of the harness: skills and agents. The headline artifact is the `security-review` skill (Layer 1 of the three-layer security stack), seeded from the Arcanum-Sec sec-context taxonomy with attribution.

Phase 4 produces the guidance that lazy-loads when relevant. Nothing in Phase 4 is enforceable deterministically; everything is advisory. Rules that must not be broken belong in Phase 3.

---

<role>
You are a senior harness engineer building the extension layer of a Claude Code harness for macOS. Your job is to produce the skills in `mac/harness/skills/` and the agents in `mac/harness/agents/`.

The `security-review` skill is the most consequential artifact in this phase. It is the pre-generation guidance layer of the three-layer security stack. It loads anti-pattern context by file type, sourced from the Arcanum-Sec sec-context taxonomy (CC BY 4.0, R.2.2).

Match the writing rules in the root `CLAUDE.md`.
</role>

<effort>xhigh</effort>
<mode>default</mode>
<thinking>adaptive</thinking>
<context_budget>Run /context at start. Phase 4 may need to inspect external sec-context content; budget for that and document delta.</context_budget>
<parallel_tool_calls>Use parallel reads for foundation docs and prior-phase outputs.</parallel_tool_calls>
<scope>Strict. Produce only the artifacts named in deliverables below. Do not modify Phase 3 outputs unless explicitly correcting a verified bug. Do not begin Phase 5.</scope>

<context>
Phase 3 produced the deterministic enforcement layer. Phase 4 adds the advisory guidance that complements it.

The `security-review` skill is the pre-generation guidance layer. It works as follows:

The `SKILL.md` file declares the skill and lists the file types it covers (Python, JavaScript, TypeScript, Go, Bash, infrastructure-as-code, and others identified in Phase 2).

When Claude touches a file of a covered type, the skill's relevant section loads into context.

Each section names the top anti-patterns for that file type, provides BAD/GOOD pseudocode examples, and cites the source.

The skill content is seeded from the Arcanum-Sec sec-context taxonomy. Pattern selection follows the top-10 ranking documented in their README. Content is rewritten to match the repo's voice, with attribution preserved.

The skill must not load the entire sec-context content (~165K tokens) at once. The lazy-load pattern is core to the design per AP.7 and QC.4b.
</context>

<investigate_before_answering>
Read these files in full:

- `phase-outputs/PHASE_0_GOALS.md`
- `phase-outputs/ANSWERS.md`
- `phase-outputs/PHASE_3_VERIFICATION.md`
- `mac/ARCHITECTURE.md`
- `mac/harness/CLAUDE.md` (the project-level CLAUDE.md, distinct from repo root)
- `foundation/00-quality-contract.md` (QC.1, QC.2, QC.3, QC.4b)
- `foundation/01-threat-model.md` (T.1, T.6)
- `foundation/02-architectural-principles.md` (AP.2, AP.6, AP.7)
- `foundation/04-research-references.md` (R.2.1 SecureForge, R.2.2 sec-context)

Fetch the sec-context README and at least three deep-pattern sections from the actual sec-context repo to verify content quality before basing the skill on it. Specifically inspect: XSS, SQL Injection, and Hardcoded Secrets. If any of those sections looks substantially weaker than the README implies, surface the issue and reduce reliance on that source for that pattern.
</investigate_before_answering>

<instructions>
Produce the following artifacts.

### 1. `mac/harness/skills/security-review/SKILL.md`

The skill manifest. Declares the skill name, description, and the file-type triggers that cause Claude to load the skill on demand. Includes the attribution block for sec-context (CC BY 4.0, Jason Haddix / Arcanum Information Security) and the methodology reference for SecureForge (R.2.1).

Lists the top-10 anti-patterns from the sec-context ranking matrix with brief one-line summaries. Each entry points to a deeper file in the same skill directory (e.g., `security-review/patterns/sql-injection.md`).

The SKILL.md itself stays under 200 lines. The depth lives in pattern files that load only when relevant.

### 2. `mac/harness/skills/security-review/patterns/` directory

One file per top-10 pattern:

- `dependency-risks.md` (slopsquatting, dependency confusion)
- `xss.md` (cross-site scripting)
- `hardcoded-secrets.md`
- `sql-injection.md`
- `auth-failures.md`
- `input-validation.md`
- `command-injection.md`
- `rate-limiting.md`
- `data-exposure.md`
- `file-upload.md`

Each pattern file:

States the CWE ID and severity rating.

Names the file types where this pattern is relevant (so Claude can match on extension).

Provides 2-3 BAD examples in the most relevant languages, with brief annotation of why each is bad.

Provides corresponding GOOD examples with brief annotation of what makes them good.

Lists the specific Semgrep rules that catch this pattern (so the Phase 3 hook can be cross-referenced).

Cites the primary source for the pattern (peer-reviewed paper, CWE entry, or sec-context section), with the appropriate attribution.

Each pattern file targets 150-300 lines. Concise but complete.

Do not bulk-copy from sec-context. Rewrite to match the repo voice. Direct quotes stay under 15 words per QC and copyright requirements. Attribution remains intact.

### 3. `mac/harness/skills/security-review/README.md`

A short user-facing overview of the skill: what it does, when it loads, what patterns it covers, and the attribution.

### 4. `mac/harness/agents/security-reviewer.md`

A subagent definition for deep security analysis beyond what Semgrep catches. The subagent:

Is invoked explicitly when the main session asks for security review of a code change.

Operates in plan mode (read-only).

Loads the relevant `security-review` skill patterns plus any project-specific context.

Produces a structured report: findings categorized by CWE and severity, false-positive rate estimate, and suggested remediations.

Returns to the main session for action.

### 5. `mac/harness/agents/writer-reviewer.md`

A two-agent pattern for Phase 5 documentation. One agent writes the docs, the other reviews against the Quality Contract and SSDF practices. The pattern is documented here so Phase 5 can invoke it.

### 6. (Optional) Additional skills identified in Phase 2

If Phase 2's `ANSWERS.md` surfaced additional skills (e.g., domain-specific guidance for the projects Rock works on), produce them here. Each follows the same lazy-load pattern as the security-review skill.

### 7. Verification

After producing the artifacts, run:

```bash
./scripts/drift-check.sh
find mac/harness/skills mac/harness/agents -name '*.md' | xargs wc -l
```

The drift check must pass. Total skill content (`SKILL.md` plus all pattern files) should be 1500-3500 lines of focused content. Less means thin. More means the lazy-load is broken because everything is loading together.

Write a `phase-outputs/PHASE_4_VERIFICATION.md` documenting the verification result, the sec-context content quality assessment from the investigation step, and any patterns where the sec-context source was insufficient.

### 8. Commit

Produce the commit message following the AP.5 template. The commit lands all Phase 4 artifacts as one logical change. The Why field cites the relevant QC properties and threat IDs, plus the attribution chain for sec-context.
</instructions>

<deliverable>
The skill, pattern files, agents, the verification document, and the commit message.

A short report at the end summarizing: skill file count, total skill content line count, sec-context quality assessment, and any open issues for Phase 5.
</deliverable>

<verification>
Each pattern file in `mac/harness/skills/security-review/patterns/` must:

State a CWE ID that exists in the MITRE CWE database.

Reference at least one Semgrep rule that catches the pattern (verify the rule exists in the Semgrep rule registry).

Cite at least one primary source with proper attribution.

Stay under 400 lines.

The `SKILL.md` must stay under 200 lines.

If any pattern fails verification, fix before declaring Phase 4 complete.

Run `./scripts/drift-check.sh` and confirm it passes.
</verification>
