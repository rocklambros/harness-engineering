# Phase 3: Deterministic Layer (Jetson) — SCAFFOLDED, NEEDS HARDWARE VALIDATION

This prompt is the Jetson equivalent of `mac/prompts/phase-3-deterministic-layer.md`. It is scaffolded but not yet validated against actual Jetson hardware. Running it produces output that should match the Mac equivalent in structure, but specific tool paths, install commands, and hook behaviors need verification on the AGX Orin.

The validation work for this phase is itself a deliverable. Document findings in `phase-outputs/PHASE_3_VALIDATION.md` after running the prompt.

---

<role>
You are a senior harness engineer building the deterministic enforcement layer on a Jetson AGX Orin. Your output should achieve capability parity with the Mac Phase 3 deliverables (in `mac/harness/`). Where the Jetson environment requires different tools or paths, document the difference in the relevant artifact's comment block.

Match the writing rules in the root `CLAUDE.md`. Apply Anthropic anti-overengineering language to code.
</role>

<effort>xhigh</effort>
<mode>default</mode>
<thinking>adaptive</thinking>
<context_budget>Run /context at start. Document delta. Plan for one compaction.</context_budget>
<parallel_tool_calls>Parallel reads for foundation, Phase 2 outputs, and Mac reference files.</parallel_tool_calls>
<scope>Strict. Only artifacts named in deliverables.</scope>

<context>
Phase 2 locked the architecture decisions. Read `phase-outputs/ANSWERS.md` and `jetson/ARCHITECTURE.md` first.

The Mac Phase 3 deliverables are in `mac/harness/`. They are the reference. The Jetson outputs should be capability-equivalent. Specific differences:

The hook scripts may need a different jq invocation if the Jetson jq version is older.

The Semgrep install command differs (pip into JetPack Python or pip into a pyenv).

`paths.deny` extends with Tegra-specific paths from `jetson/ARCHITECTURE.md`.

`commands.deny` extends with Jetson power-management patterns from Phase 2 decisions.

The `settings.json.template` `_validated_claude_code_range` may differ from Mac.

The "needs validation when ported" markers in this prompt are real. Do not assume the Mac output works on Jetson. Verify on hardware.
</context>

<investigate_before_answering>
Read in full:

- `phase-outputs/PHASE_0_GOALS.md`, `ANSWERS.md`
- `jetson/ARCHITECTURE.md`
- `mac/harness/CLAUDE.md`, `mac/harness/settings.json.template`, `mac/harness/rules/*`, `mac/harness/hooks/*`
- `mac/prompts/phase-3-deterministic-layer.md` (the validated reference prompt)
- `foundation/00-quality-contract.md`, `01-threat-model.md`, `02-architectural-principles.md`
</investigate_before_answering>

<validation_markers>
The deliverables below carry explicit "needs validation when ported" expectations. When producing each artifact, run the corresponding validation step and document the result.

For `harness/CLAUDE.md`: validate that the version pin matches the Jetson Claude Code installation reported in Phase 1.

For `harness/settings.json.template`: validate that the hook command paths exist on the Jetson filesystem. Verify the bash interpreter path.

For `harness/rules/paths.deny`: validate that the Tegra-specific paths exist on this Jetson installation. If a path doesn't exist, decide whether to keep it (preventive coverage) or remove it.

For `harness/hooks/post-tool-use-semgrep.sh`: run it against a synthetic SQL injection test file on the Jetson. Verify Semgrep catches the pattern and the hook surfaces the finding.

For `harness/hooks/session-start.sh`: run it and verify the drift check executes without permission issues on the Jetson filesystem.

For each validation, write the command run and the actual output to `phase-outputs/PHASE_3_VALIDATION.md`.
</validation_markers>

<instructions>
Produce the artifacts in items 1-7 below, then run the verification in item 8.

### 1. `jetson/harness/CLAUDE.md`

Seven-section pattern (Role, code standards, security rules, core constraints, things-that-break, operational, status). Capability-equivalent to `mac/harness/CLAUDE.md` with Jetson-specific status section adjustments. Under 200 lines.

Trace: QC.4b, T.7.

### 2. `jetson/harness/settings.json.template`

JSON template. Mirror the Mac template with Jetson-specific differences from Phase 2:

Hook command paths use the Jetson harness directory structure.

`permissions.deny` extends with Tegra paths.

`_validated_claude_code_range` reflects the Jetson-validated range.

Trace: AP.1, QC.1, T.4.

### 3. `jetson/harness/rules/` directory

Same files as Mac (`paths.deny`, `paths.allow`, `commands.deny`, `secrets.patterns`, `README.md`). Extend the deny lists with Jetson-specific entries from Phase 2.

Trace: T.2, T.5, T.6.

### 4. `jetson/harness/hooks/post-tool-use-semgrep.sh`

Byte-identical to the Mac version unless Phase 2 surfaced a Jetson-specific reason to diverge. The hook should work the same way on both platforms because it uses `#!/usr/bin/env bash` and depends on jq and Semgrep that are both available on ARM64.

Validation: run the hook against `/tmp/test-sqli.py` containing `cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")`. Verify Semgrep flags the SQL injection. Document result in `PHASE_3_VALIDATION.md`.

Trace: QC.1, T.1, AP.2.

### 5. `jetson/harness/hooks/pre-tool-use-shell-audit.sh`

Same as Mac.

### 6. `jetson/harness/hooks/session-start.sh`

Same structure as Mac. The validated Claude Code range constant may differ. Verify.

### 7. `jetson/harness/hooks/pre-compact-preserve.sh`

Same as Mac.

### 8. Verification and validation

Run:

```bash
shellcheck jetson/harness/hooks/*.sh
./scripts/drift-check.sh
```

Both must pass.

Run the post-tool-use hook validation described in `validation_markers`. Document outcomes in `phase-outputs/PHASE_3_VALIDATION.md`.

If any validation fails, the Phase 3 deliverables are incomplete. Fix and re-run before declaring Phase 3 done on Jetson.

### 9. Commit

Follow the AP.5 template. The commit message Why field cites the QC properties, threat IDs, and Mac reference commits.

After commit, update `jetson/README.md` build status table: Phase 3 moves from "Scaffolded" to "Validated" if all validation steps pass.
</instructions>

<deliverable>
Artifacts in items 1-7, validation document in item 8, commit in item 9. Short report summarizing the validation outcomes.
</deliverable>

<verification>
The Semgrep hook must flag a synthetic SQL injection on the Jetson exactly as it does on Mac. If the rule pack coverage differs between platforms, that's a finding to document and resolve (likely by aligning the pinned Semgrep version).

All hook scripts must pass `shellcheck`.

The drift check must pass.

If validation fails on any step, do not declare Phase 3 validated. Document the failure and propose a resolution.
</verification>
