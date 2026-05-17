# Phase 4: Extension Layer (Jetson) — SCAFFOLDED, NEEDS HARDWARE VALIDATION

Builds the advisory guidance layer on Jetson: the `security-review` skill and any subagents. The skill content is identical to Mac because anti-patterns do not vary by platform.

The "needs validation when ported" markers in this prompt cover Tegra-specific Semgrep rule-pack behavior and any Jetson-specific skill additions surfaced in Phase 2.

---

<role>
You are a senior harness engineer building the extension layer on Jetson. The `security-review` skill is the headline artifact. Content is byte-identical to Mac unless Phase 2 surfaced a Jetson-specific addition (e.g., a CUDA-anti-patterns skill).

Match the writing rules.
</role>

<effort>xhigh</effort>
<mode>default</mode>
<thinking>adaptive</thinking>
<context_budget>Run /context at start. Document delta.</context_budget>
<parallel_tool_calls>Parallel reads.</parallel_tool_calls>
<scope>Strict. Only artifacts named below.</scope>

<context>
Phase 3 produced the deterministic layer. Phase 4 adds the advisory guidance.

The `security-review` skill content is identical across all three platforms. The skill manifest and pattern files in `mac/harness/skills/security-review/` are the reference. Copy them to `jetson/harness/skills/security-review/` and verify the file-type triggers cover Jetson-specific concerns surfaced in Phase 2.

If Phase 2 decided to add a CUDA anti-patterns skill or other Jetson-specific guidance, scaffold it here. Otherwise the skill content is a direct copy.
</context>

<investigate_before_answering>
Read:

- `phase-outputs/ANSWERS.md`, `PHASE_3_VALIDATION.md`
- `jetson/ARCHITECTURE.md`
- `mac/harness/skills/security-review/SKILL.md`, `README.md`, and all `patterns/*.md` (the reference content)
- `mac/harness/agents/*` (agent definitions)
- `foundation/02-architectural-principles.md` (AP.7 lazy load, AP.2 three-layer)
</investigate_before_answering>

<validation_markers>
For each artifact:

`SKILL.md`: validate that the file-type triggers include any Jetson-specific extensions Phase 2 identified (e.g., `.cu` for CUDA C if a CUDA skill was added).

`patterns/*.md`: validate that Semgrep rule references in each pattern file resolve on the Jetson Semgrep install (`semgrep --validate --config <rule-pack>`). If any rule pack is missing on aarch64, document the gap and propose a workaround.

Subagent files: validate that Claude Code's subagent discovery picks them up on the Jetson installation.

Document each validation in `phase-outputs/PHASE_4_VALIDATION.md`.
</validation_markers>

<instructions>
### 1. `jetson/harness/skills/security-review/SKILL.md`

Copy from `mac/harness/skills/security-review/SKILL.md`. Update only if Phase 2 added Jetson-specific file-type triggers.

### 2. `jetson/harness/skills/security-review/patterns/` directory

Copy all pattern files from the Mac equivalent. Content is identical. Verify Semgrep rule references resolve on Jetson.

### 3. `jetson/harness/skills/security-review/README.md`

Copy from Mac. Update attribution section if anything changes.

### 4. `jetson/harness/agents/security-reviewer.md` and `writer-reviewer.md`

Copy from Mac. Content identical.

### 5. Jetson-specific skills if Phase 2 decided to add any

Scaffold per Phase 2 decision. For each, follow the same structure as `security-review/`.

### 6. Verification

```bash
./scripts/drift-check.sh
find jetson/harness/skills jetson/harness/agents -name '*.md' | xargs wc -l
```

Drift check must pass. Total skill content should be within 10% of the Mac equivalent line counts (parity check).

Document validation in `phase-outputs/PHASE_4_VALIDATION.md`.

### 7. Commit

AP.5 template. Cite QC properties, threat IDs, sec-context attribution, and the Mac reference commits this work parallels.

Update `jetson/README.md` build status: Phase 4 moves from "Scaffolded" to "Validated" if all validation steps pass.
</instructions>

<deliverable>
Skill, pattern files, agents, validation document, commit. Short summary report.
</deliverable>

<verification>
Each pattern file's Semgrep rule references must resolve on the Jetson install. Document any gaps.

Drift check passes.

Skill file count and content size match Mac within 10%.
</verification>
