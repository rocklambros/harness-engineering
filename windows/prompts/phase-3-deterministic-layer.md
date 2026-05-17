# Phase 3: Deterministic Layer (Windows) — SCAFFOLDED, NEEDS HARDWARE VALIDATION

The Windows equivalent of `mac/prompts/phase-3-deterministic-layer.md`. Scaffolded but not validated against actual Windows + WSL2. Running it produces output that should match Mac in structure, with `wsl.exe` invocation wrappers in the settings template and Windows-specific path additions in the deny lists.

Validation work for this phase is itself a deliverable. Document in `phase-outputs/PHASE_3_VALIDATION.md`.

---

<role>
You are a senior harness engineer building the deterministic enforcement layer on Windows + WSL2. The capability surface must equal Mac. The implementation must use the WSL2 indirection per `windows/ARCHITECTURE.md`.

Match the writing rules.
</role>

<effort>xhigh</effort>
<mode>default</mode>
<thinking>adaptive</thinking>
<context_budget>Run /context at start. Plan for one compaction.</context_budget>
<parallel_tool_calls>Parallel reads.</parallel_tool_calls>
<scope>Strict.</scope>

<context>
Phase 2 locked the architecture. Read `phase-outputs/ANSWERS.md` and `windows/ARCHITECTURE.md` first.

Mac Phase 3 deliverables in `mac/harness/` are the reference. Windows differences:

`settings.json.template` hook commands wrap bash scripts in `wsl.exe -e bash` invocations.

`paths.deny` extends with Windows credential paths (`AppData`, `LocalAppData`, registry export files).

`commands.deny` extends with Windows-specific dangerous patterns (`powershell -EncodedCommand`, `reg add HKLM:\`, `wmic process call create`).

Hook scripts are byte-identical to Mac because they run inside WSL2.

The `session-start.sh` hook gets a WSL2 health-check section appended.

The `_validated_claude_code_range` may differ if Windows lags Mac on a Claude Code release.

"Needs validation when ported" markers in this prompt are real. Verify on actual Windows + WSL2 hardware.
</context>

<investigate_before_answering>
Read:

- `phase-outputs/PHASE_0_GOALS.md`, `ANSWERS.md`
- `windows/ARCHITECTURE.md`
- `mac/harness/*` (the reference)
- `mac/prompts/phase-3-deterministic-layer.md`
- `foundation/00-quality-contract.md`, `01-threat-model.md`, `02-architectural-principles.md`
</investigate_before_answering>

<validation_markers>
For `harness/CLAUDE.md`: validate that the version pin matches the Windows Claude Code installation.

For `harness/settings.json.template`: validate that `wsl.exe -e bash` invocations work from a clean Claude Code session on Windows. Run a synthetic Write event and confirm the hook fires and returns output.

For `harness/rules/paths.deny`: validate that the Windows-specific paths exist on the host. Test that the deny patterns trigger when Claude Code tries to read them.

For `harness/hooks/post-tool-use-semgrep.sh`: byte-identical to Mac. Validate by running it inside WSL2 against a synthetic SQL injection file. Verify the WSL2 round-trip from Claude Code on Windows works and the model sees the findings.

For `harness/hooks/session-start.sh`: validate the appended WSL2 health-check section detects a stopped WSL2 distribution correctly.

For path translation: validate that paths in hook payloads (which Claude Code on Windows may send as `C:\...`) are correctly translated to WSL2 paths (`/mnt/c/...`) inside the script.

Document each validation in `phase-outputs/PHASE_3_VALIDATION.md`.
</validation_markers>

<instructions>
Produce artifacts 1-7, run verification in item 8, commit in item 9.

### 1. `windows/harness/CLAUDE.md`

TRACT pattern. Same as Mac with Windows-specific status section notes (WSL2 dependency, version pin, working-directory convention `/mnt/c/...`). Under 200 lines.

### 2. `windows/harness/settings.json.template`

JSON template. Mirror Mac structure with Windows differences:

Hook command paths wrap in `wsl.exe -e bash <wsl-path>`.

`permissions.deny` extends with Windows credential paths and registry-related dangerous patterns.

`_validated_claude_code_range` reflects Windows validation.

Add a `_comment_wsl_dependency` field documenting that WSL2 is required and what distribution is validated.

### 3. `windows/harness/rules/` directory

Same files as Mac. `paths.deny` adds Windows-specific entries. `commands.deny` adds Windows-specific patterns. `paths.allow` notes the WSL2-vs-Windows path duality. `secrets.patterns` is identical.

### 4. `windows/harness/hooks/post-tool-use-semgrep.sh`

Byte-identical to Mac. Add a path-translation helper at the top of the script that detects Windows-style paths (`C:\...`, `c:/...`) in the payload and converts them to WSL2 paths (`/mnt/c/...`). This makes the script callable equally from Mac/Jetson (where translation is a no-op) and Windows (where it actively converts).

Validation: run inside WSL2 against a Windows-style payload. Verify the path translation works and Semgrep flags the synthetic injection.

### 5. `windows/harness/hooks/pre-tool-use-shell-audit.sh`

Same as Mac with the same path-translation helper.

### 6. `windows/harness/hooks/session-start.sh`

Same as Mac with an appended WSL2 health-check section. The section verifies the WSL2 distribution is running, Semgrep is reachable, and `/mnt/c/` is mounted. Fails advisory (warns) if any check fails; does not block the session.

### 7. `windows/harness/hooks/pre-compact-preserve.sh`

Same as Mac.

### 8. Verification and validation

```bash
wsl.exe -e bash -c "shellcheck /mnt/c/path/to/repo/windows/harness/hooks/*.sh"
./scripts/drift-check.sh
```

Both must pass.

Run the Semgrep hook validation described in `validation_markers`. Document outcomes in `phase-outputs/PHASE_3_VALIDATION.md`.

If validation fails, Phase 3 is incomplete on Windows. Fix and re-run.

### 9. Commit

AP.5 template. Why field cites QC properties, threat IDs, Mac reference commits, and the WSL2 decision in `windows/ARCHITECTURE.md`.

Update `windows/README.md` status table: Phase 3 moves to "Validated" if validation passes.
</instructions>

<deliverable>
Artifacts 1-7, validation document, commit. Short summary report.
</deliverable>

<verification>
The Semgrep hook must flag a synthetic SQL injection through the WSL2 round-trip exactly as it does on Mac directly.

All hook scripts pass `shellcheck` inside WSL2.

Drift check passes.

Path translation works for both Windows-style and WSL2-style paths in payloads.
</verification>
