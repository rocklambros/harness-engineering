# Phase 5: Wire and Document

This phase integrates Phase 3 and Phase 4 artifacts, runs end-to-end tests, finalizes documentation, and prepares the harness for public release. The writer/reviewer subagent pattern from Phase 4 drives the documentation work.

Phase 5 is where the repo transitions from "build in progress" to "public reference repo." Every document must read for a non-author audience.

---

<role>
You are a senior harness engineer wiring together the deterministic and extension layers of a Claude Code harness and producing the final documentation for public release.

Use the writer/reviewer subagent pattern defined in `mac/harness/agents/writer-reviewer.md`. One agent writes; the other reviews against the Quality Contract and SSDF practices. Iterate until the reviewer signs off.
</role>

<effort>xhigh</effort>
<mode>default</mode>
<thinking>adaptive</thinking>
<context_budget>Run /context at start. Phase 5 reads and reviews extensively; budget for at least one compaction. Document delta.</context_budget>
<parallel_tool_calls>Use parallel reads for foundation, prior-phase outputs, and existing harness files.</parallel_tool_calls>
<scope>Strict. Produce only the artifacts in deliverables. Do not redo Phase 3 or Phase 4 work unless explicit bugs surface during integration testing.</scope>

<use_writer_reviewer_pattern>
For each documentation artifact in this phase:

1. Spawn the writer subagent with the artifact specification.
2. Writer produces a draft.
3. Spawn the reviewer subagent against the draft, with the Quality Contract and the SSDF practice list as the review criteria.
4. Reviewer produces a critique with specific line references.
5. Writer revises against the critique.
6. Loop until the reviewer signs off or three iterations have happened (whichever comes first).
7. Main session takes the final draft and writes the file.

Document the iteration count for each artifact in `phase-outputs/PHASE_5_VERIFICATION.md`.
</use_writer_reviewer_pattern>

<context>
Phases 3 and 4 produced the harness files. Phase 5:

Runs end-to-end integration tests that exercise the full three-layer security stack.

Finalizes the user-facing documentation: README files at each level, the user guide, and the architecture guide.

Updates the JOURNEY.md with the build narrative.

Produces release artifacts: SBOM, signed commit instructions, the release commit.

Documents any known issues, deferred work, or open questions in a structured way that a public reader can follow.
</context>

<investigate_before_answering>
Read these files in full:

- All Phase 3 and Phase 4 deliverables in `mac/harness/`
- `phase-outputs/PHASE_3_VERIFICATION.md`, `phase-outputs/PHASE_4_VERIFICATION.md`
- `mac/ARCHITECTURE.md` (updated through Phase 2)
- `mac/README.md` (the section README)
- The root `README.md`, `CLAUDE.md`, `JOURNEY.md`
- All `foundation/` files (re-read; their citations are about to land in the final docs)
</investigate_before_answering>

<instructions>
### 1. End-to-end integration test

Create `mac/scripts/integration-test.sh` that:

Starts a clean Claude Code session against a synthetic project directory.

Triggers the security-review skill by writing a Python file with a known SQL injection pattern.

Verifies the PostToolUse Semgrep hook fires and surfaces the finding.

Triggers Claude to fix the file in the same session.

Verifies the second hook invocation shows no findings.

Runs the pre-commit hook against the changed files and verifies all checks pass.

Cleans up the synthetic project.

Write a `phase-outputs/PHASE_5_INTEGRATION_TEST.md` documenting the test sequence, expected outputs, and actual outputs. Test must pass before moving to documentation.

### 2. User guide

Create `mac/USER_GUIDE.md` with these sections:

Quickstart: how to adopt the harness in a new Claude Code project, in 5-10 concrete steps.

Daily use: what to expect during a session, including how the security-review skill loads, how the commit-time hook works, and how to interpret findings.

Troubleshooting: common issues and how to diagnose them. Include the cache-TTL silent regression, the hook-failure-closed behavior, and the drift-check failure modes.

Customization: how to extend the harness with project-specific rules, skills, and agents without breaking the Quality Contract.

Target 400-800 lines. Written for a developer who is not Rock, not the author. First-person voice but addressed to "you."

### 3. Harness guide

Create `mac/HARNESS_GUIDE.md` with these sections:

The five layers, with one paragraph each pointing to the relevant files.

The three-layer security stack, with one paragraph each explaining when each layer fires and what it catches.

The relationship between the harness and Claude Code (what's our config vs. what's upstream).

How to update the harness when Claude Code releases a new minor version (the QC.5 re-evaluation checklist).

Target 300-600 lines. More technical than USER_GUIDE.md, less narrative than ARCHITECTURE.md.

### 4. README updates

Update `mac/README.md` to reflect the completed state. Phase status table moves from "Pending" to "Validated" for all phases. Add links to the new USER_GUIDE.md and HARNESS_GUIDE.md.

Update the root `README.md` to reflect the completed state. Update the "What ships in the harness" section if anything changed. Add a link to the mac/USER_GUIDE.md for quickstart.

### 5. JOURNEY update

Add a Phase 5 entry to `JOURNEY.md` summarizing what was built, what was decided, and what remains open as known limitations.

### 6. SBOM and release artifacts

Run `scripts/generate-sbom.sh` (create this script if it doesn't exist; it should run syft against the harness directory and produce a CycloneDX SBOM at `mac/harness/sbom.cdx.json`).

Document the signed-commit process in `SECURITY.md` if not already documented.

### 7. Final verification

Run the full pre-commit suite:

```bash
pre-commit run --all-files
./scripts/drift-check.sh
mac/scripts/integration-test.sh
```

All must pass. Document the results in `phase-outputs/PHASE_5_VERIFICATION.md`.

### 8. Commit and tag

Produce the release commit message following AP.5. The commit lands all Phase 5 artifacts plus any documentation updates as one logical change.

Produce the v1.0.0 tag annotation with the release notes summarizing the three-layer security stack, the cross-platform parity statement (with Jetson and Windows in scaffolded state), and the known limitations.
</instructions>

<deliverable>
Integration test script and results document.

User guide, harness guide, README updates, JOURNEY entry, SBOM, verification document.

Release commit message and v1.0.0 tag annotation.

A short report summarizing: total artifact count for Phase 5, integration test result, drift check pass/fail, and any known limitations carried into the public release.
</deliverable>

<verification>
Integration test must pass end to end. The Semgrep hook must demonstrate the SecureForge Appendix C feedback loop with a real synthetic vulnerability.

All four pre-commit hook categories must run cleanly: trailing whitespace and EOF, gitleaks, semgrep, shellcheck.

The drift check must pass.

USER_GUIDE.md and HARNESS_GUIDE.md must pass the reviewer subagent's Quality Contract review with three or fewer iterations. If more iterations are needed, the docs likely have a structural issue that should be addressed before declaring Phase 5 complete.

Total CLAUDE.md hierarchy (root plus `mac/harness/CLAUDE.md`) must remain under 400 lines per QC.4b.

Document each verification result in `phase-outputs/PHASE_5_VERIFICATION.md`.
</verification>
