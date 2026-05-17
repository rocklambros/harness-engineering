# Phase 3: Deterministic Layer

This phase builds the deterministic enforcement surfaces of the harness: the project CLAUDE.md, the settings.json, the rules directory, the hooks (including the SecureForge-style commit-time hardening hook), and the wired `.pre-commit-config.yaml` (already present at root, but this phase verifies and extends it).

Phase 3 is the first phase that writes production artifacts. Everything here is enforced at runtime by Claude Code or by pre-commit. Advisory guidance does not belong in Phase 3.

---

<role>
You are a senior harness engineer building the deterministic enforcement layer of a Claude Code harness for macOS. Your job is to produce the files in `mac/harness/CLAUDE.md`, `mac/harness/settings.json.template`, `mac/harness/rules/`, and `mac/harness/hooks/`.

The commit-time Semgrep hook in `mac/harness/hooks/post-tool-use-semgrep.sh` is the most consequential single artifact in this phase. It implements the SecureForge Appendix C commit-time hardening pattern (R.2.1). Get it right.

Match the writing rules in the root `CLAUDE.md`. Apply the verbatim anti-overengineering language from Anthropic's prompting documentation to any code you write.
</role>

<effort>xhigh</effort>
<mode>default</mode>
<thinking>adaptive</thinking>
<context_budget>Run /context at start. Phase 3 produces multiple artifacts; budget for at least one compaction. Document the delta.</context_budget>
<parallel_tool_calls>Use parallel reads for foundation and prior-phase outputs. Writes are serial.</parallel_tool_calls>
<scope>Strict. Produce only the artifacts named in deliverables below. Do not begin Phase 4 (skills are not in scope). Do not modify `foundation/` or `research/` from this phase.</scope>

<context>
Phase 2 locked the architecture in `phase-outputs/ANSWERS.md` and updated `mac/ARCHITECTURE.md`. Read both before producing any artifact.

The three-layer security stack lives across Phase 3 and Phase 4. This phase produces two of the three layers:

Commit-time hardening (Layer 2 of the security stack): `mac/harness/hooks/post-tool-use-semgrep.sh`. This is the SecureForge Appendix C pattern: after every Write or Edit, run Semgrep on the changed file, and if findings exist, return the rule, line, and message to Claude through hook output so the model can fix in the same session.

Post-generation validation (Layer 3 of the security stack): the `.pre-commit-config.yaml` at repo root is already in place from Batch 1. Phase 3 verifies it's wired and runs an integration test.

The pre-generation guidance layer (Layer 1) lives in Phase 4 as the `security-review` skill.

The hooks must fail closed per AP.8. The deterministic rules must be enforceable per AP.1. The hook scripts must be shellcheck-clean per the drift check.
</context>

<investigate_before_answering>
Read these files in full before producing any artifact:

- `phase-outputs/PHASE_0_GOALS.md`
- `phase-outputs/ANSWERS.md`
- `mac/ARCHITECTURE.md`
- `foundation/00-quality-contract.md` (QC.1, QC.2, QC.4b, QC.5)
- `foundation/01-threat-model.md` (T.1, T.2, T.4, T.5, T.6)
- `foundation/02-architectural-principles.md` (AP.1, AP.2, AP.8)
- `foundation/04-research-references.md` (R.1.1 for hook events, R.2.1 for SecureForge methodology)
- The relevant sections of `research/Claude_Architecture.md` on hooks and permission modes
- The SecureForge paper Appendix C on commit-time hardening (cited in R.2.1; if not in research/, reference the paper directly)
</investigate_before_answering>

<anti_overengineering>
The harness components you build in this phase should be the smallest version that meets the requirements. Specifically:

Hooks do one thing. The Semgrep hook runs Semgrep and returns findings. It does not also lint markdown, check dependencies, or measure code complexity. Those are separate concerns and may justify separate hooks.

Rules files contain only the patterns the hooks actually consult. No speculative rules for hypothetical attacks.

CLAUDE.md content passes the removal test: if removing a line would not cause Claude to make mistakes, the line comes out.

settings.json contains only the configuration the harness actually depends on. Defaults are accepted unless explicitly overridden.
</anti_overengineering>

<instructions>
Produce the following artifacts. Each must trace to one or more Quality Contract properties and one or more threat IDs.

### 1. `mac/harness/CLAUDE.md`

Seven-section pattern (Role, code standards, security rules, core constraints, things-that-break, operational, status). Under 200 lines hard cap, target 160.

This is the project-level CLAUDE.md that ships with the harness, distinct from the repo-root `/Users/klambros/harness-engineering/CLAUDE.md`. The harness CLAUDE.md goes into Claude Code projects that adopt the harness; the repo-root CLAUDE.md governs sessions against this repo.

Trace: QC.4b (under-400-line CLAUDE.md hierarchy). T.7 (config drift, version pin in status section).

### 2. `mac/harness/settings.json.template`

JSON template (with placeholders, not real credentials) configuring:

Permission mode defaults: plan for read-heavy commands, default for writes.

Hook registrations: PostToolUse on Write and Edit pointing to `harness/hooks/post-tool-use-semgrep.sh`. PreToolUse on Bash pointing to `harness/hooks/pre-tool-use-shell-audit.sh`. PreCompact pointing to `harness/hooks/pre-compact-preserve.sh`. SessionStart pointing to `harness/hooks/session-start.sh`.

MCP server list: empty by default. MCP servers load on demand per AP.7.

Comments in the template (using `_comment` keys since JSON doesn't support comments) explain why each setting is set the way it is.

Trace: AP.1 (deterministic enforcement). QC.1 (security alignment). T.4 (hook bypass coverage).

### 3. `mac/harness/rules/` directory contents

Produce these files:

`paths.deny` — newline-separated list of path patterns that must never be read or written. Includes `~/.ssh/`, `~/.aws/credentials`, `/etc/shadow`, and similar.

`paths.allow` — explicit allow list for sensitive operations. Defaults to the user's working directories.

`commands.deny` — patterns for shell commands that must be blocked: `curl | sh`, `wget | bash`, `rm -rf /`, `rm -rf $HOME`, and similar high-risk one-liners.

`secrets.patterns` — regex patterns for detecting secrets in generated code, supplementing gitleaks. Project-specific patterns (e.g., the format of internal API tokens).

`README.md` in the rules directory describing what each file does and how the hooks consume them.

Trace: T.2 (prompt injection), T.5 (dependency compromise), T.6 (secret exposure).

### 4. `mac/harness/hooks/post-tool-use-semgrep.sh`

The commit-time hardening hook. This is the most important file in Phase 3.

Behavior:

Receives Claude Code hook event payload on stdin (JSON with file path and tool call context).

Extracts the file path that was written or edited.

Runs Semgrep against that single file using the default and security-audit rule packs.

If Semgrep finds nothing, exits 0 silently.

If Semgrep finds findings, emits structured output on stdout with rule ID, line number, and message for each finding. Exit code is 0 (the hook surfaces findings; it does not block writes).

Fails closed on internal errors: if the hook script errors, the action is blocked.

Logs invocations to `~/.claude-harness/hook.log` with timestamp, file, finding count.

The hook implements R.2.1 SecureForge Appendix C. The in-file comment cites the methodology and the published 48% CWE-rate reduction with the appropriate confidence interval.

Trace: QC.1 (PW.7, PW.8 SSDF practices). T.1 (benign vulnerability generation). AP.2 (three-layer security, commit-time hardening layer).

### 5. `mac/harness/hooks/pre-tool-use-shell-audit.sh`

Logs shell command invocations before execution. Does not block (audit only). Output goes to `~/.claude-harness/shell-audit.log`.

Trace: T.2, T.4. AP.8 (fail closed on errors).

### 6. `mac/harness/hooks/session-start.sh`

Runs the drift check at session start. If drift detected, surfaces the drift summary in the hook output but does not block (advisory).

Runs the version check against the pinned Claude Code minor-version range. If out of range, surfaces a warning.

Trace: QC.5 (versioning), T.7 (config drift).

### 7. `mac/harness/hooks/pre-compact-preserve.sh`

Ensures the active phase context survives a compaction event. Specifically: if the session is mid-phase (per session metadata), the hook writes the current phase ID and relevant context summary into a small preserved file that the compaction process retains.

Trace: AP.7 (lazy load, against compaction collapsing essential phase state).

### 8. Verification: integration test

After writing all artifacts, run:

```bash
shellcheck mac/harness/hooks/*.sh
./scripts/drift-check.sh
```

Both must pass. If either fails, fix before declaring Phase 3 complete.

Write a `phase-outputs/PHASE_3_VERIFICATION.md` documenting the integration test result.

### 9. Commit

After verification, produce the commit message following the template in `foundation/02-architectural-principles.md` AP.5. The commit groups the Phase 3 deliverables into one logical landing. The Why field cites the relevant QC properties and threat IDs.
</instructions>

<deliverable>
The artifacts in items 1 through 7, the verification document in item 8, and the commit message in item 9.

A short report at the end summarizing: artifact count, verification status, drift check pass/fail, hooks shellcheck pass/fail, and any open issues that need to land in Phase 4 or 5.
</deliverable>

<verification>
The commit-time Semgrep hook must:

Run cleanly against a synthetic test file containing a known SQL injection pattern (e.g., `cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")` in Python). Verify Semgrep flags it and the hook surfaces the finding with rule ID and line number.

Exit cleanly against a synthetic test file with no issues. Verify exit code 0 and no false output.

Fail closed when Semgrep is not installed. Verify the hook returns non-zero and surfaces a clear error.

All four hook scripts must pass `shellcheck` with no warnings.

The drift check must pass against the post-Phase-3 repo state.

Document each verification result in `phase-outputs/PHASE_3_VERIFICATION.md`.
</verification>
