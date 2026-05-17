# Phase 5: Wire and Document (Windows) — SCAFFOLDED, NEEDS HARDWARE VALIDATION

Integrates Phase 3 and Phase 4 on Windows. The integration test must verify the WSL2 round-trip works end-to-end.

---

<role>
You are a senior harness engineer wiring the Windows harness layers and producing Windows-specific documentation.

Use the writer/reviewer subagent pattern from `windows/harness/agents/writer-reviewer.md`.
</role>

<effort>xhigh</effort>
<mode>default</mode>
<thinking>adaptive</thinking>
<context_budget>Run /context at start. Plan for compaction.</context_budget>
<parallel_tool_calls>Parallel reads.</parallel_tool_calls>
<scope>Strict.</scope>

<context>
Phases 3 and 4 produced the Windows harness files. Phase 5:

End-to-end integration test that verifies the WSL2 round-trip works from a Claude Code session on Windows.

Windows-specific documentation: `windows/README.md` updates, `windows/USER_GUIDE.md` (Windows quickstart with WSL2 setup), `windows/HARNESS_GUIDE.md` (Windows technical reference).

`JOURNEY.md` entry for the Windows Phase 5 milestone.

Windows-specific SBOM.
</context>

<validation_markers>
Integration test: must verify the full WSL2 round-trip. Synthetic project at `C:\Users\<user>\harness-test\`, Claude Code on Windows triggers Write, hook runs inside WSL2, findings return to Claude Code.

Documentation: install commands in `windows/USER_GUIDE.md` must be runnable on a fresh Windows 11 + WSL2 install.

SBOM: generate via syft inside WSL2 against the WSL2 Python environment that runs the security tools.

Document validations in `phase-outputs/PHASE_5_VALIDATION.md`.
</validation_markers>

<instructions>
### 1. `windows/scripts/integration-test.sh`

Adapted from Mac. Runs inside WSL2. Tests the WSL2 round-trip explicitly: from a path on the Windows host, trigger a synthetic event, verify Semgrep findings round-trip back.

### 2. `windows/USER_GUIDE.md`

Windows-specific quickstart. Covers:

WSL2 installation and distribution selection.

Required tool install inside WSL2.

Git autocrlf configuration.

Adopting the harness into a Windows project.

Daily commands.

Troubleshooting (WSL2-specific failure modes).

### 3. `windows/HARNESS_GUIDE.md`

Windows-specific technical reference. Five layers with WSL2 substitutions, three-layer security stack on Windows, WSL2 round-trip latency considerations, QC.5 re-evaluation triggers specific to Windows.

### 4. Update `windows/README.md`

Phases move to "Validated" if validation succeeds. Add routing links to `USER_GUIDE.md` and `HARNESS_GUIDE.md`.

### 5. Update `JOURNEY.md`

Windows Phase 5 entry.

### 6. SBOM

`windows/harness/sbom.cdx.json`. CycloneDX format. Generated inside WSL2.

### 7. Verification

```bash
wsl.exe -e bash -c "cd /mnt/c/path/to/repo && pre-commit run --all-files"
./scripts/drift-check.sh
wsl.exe -e bash -c "/mnt/c/path/to/repo/windows/scripts/integration-test.sh"
```

All must pass.

### 8. Commit and tag

AP.5 commit. Tag `windows-v1.0.0`.

Use writer/reviewer pattern for documentation. Three iterations max per artifact.
</instructions>

<deliverable>
Integration test, USER_GUIDE.md, HARNESS_GUIDE.md, README updates, JOURNEY entry, SBOM, validation, commit, tag. Short summary report.
</deliverable>

<verification>
Integration test passes end-to-end through WSL2. Pre-commit hooks pass. Drift check passes. Writer/reviewer iterations 3 or fewer per artifact.
</verification>
