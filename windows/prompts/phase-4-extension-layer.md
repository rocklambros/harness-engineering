# Phase 4: Extension Layer (Windows) — SCAFFOLDED, NEEDS HARDWARE VALIDATION

Builds the advisory guidance layer on Windows. Skill content identical to Mac. The "needs validation when ported" markers cover Claude Code skill loading on Windows.

---

<role>
You are a senior harness engineer building the extension layer on Windows. The `security-review` skill is content-identical to Mac. Validate that Claude Code on Windows loads it correctly.

Match the writing rules.
</role>

<effort>xhigh</effort>
<mode>default</mode>
<thinking>adaptive</thinking>
<context_budget>Run /context at start.</context_budget>
<parallel_tool_calls>Parallel reads.</parallel_tool_calls>
<scope>Strict.</scope>

<context>
Phase 3 produced the deterministic layer. Phase 4 adds advisory guidance.

The `security-review` skill content is identical across platforms. Copy from `mac/harness/skills/security-review/` to `windows/harness/skills/security-review/`. Verify Claude Code on Windows discovers and lazy-loads the skill correctly.

If Phase 2 surfaced Windows-specific skill needs (e.g., Windows API anti-patterns, PowerShell injection patterns), scaffold them here.
</context>

<investigate_before_answering>
Read:

- `phase-outputs/ANSWERS.md`, `PHASE_3_VALIDATION.md`
- `windows/ARCHITECTURE.md`
- `mac/harness/skills/security-review/*` (the reference)
- `mac/harness/agents/*`
- `foundation/02-architectural-principles.md` (AP.7, AP.2)
</investigate_before_answering>

<validation_markers>
`SKILL.md`: validate that Claude Code on Windows loads the skill when relevant file types are touched. Open a Python file with a known anti-pattern and verify the skill loads.

`patterns/*.md`: validate Semgrep rule references resolve through the WSL2 round-trip.

Subagents: validate that Claude Code on Windows discovers them.

Document in `phase-outputs/PHASE_4_VALIDATION.md`.
</validation_markers>

<instructions>
### 1. `windows/harness/skills/security-review/SKILL.md`

Copy from Mac. Update only if Phase 2 added Windows-specific triggers.

### 2. `windows/harness/skills/security-review/patterns/` directory

Copy all pattern files from Mac. Verify Semgrep rule references resolve.

### 3. `windows/harness/skills/security-review/README.md`

Copy from Mac.

### 4. `windows/harness/agents/security-reviewer.md` and `writer-reviewer.md`

Copy from Mac.

### 5. Windows-specific skills if Phase 2 decided to add any

Scaffold per Phase 2 decision.

### 6. Verification

```bash
./scripts/drift-check.sh
find windows/harness/skills windows/harness/agents -name '*.md' | xargs wc -l
```

Skill content size within 10% of Mac.

Document validation.

### 7. Commit

AP.5 template. Cite sec-context attribution and Mac reference commits.

Update `windows/README.md` build status.
</instructions>

<deliverable>
Skill, patterns, agents, validation, commit. Short report.
</deliverable>

<verification>
Claude Code on Windows loads the skill on relevant file types. Pattern files resolve. Drift check passes.
</verification>
