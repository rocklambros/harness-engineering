# Phase 5: Wire and Document (Jetson) — SCAFFOLDED, NEEDS HARDWARE VALIDATION

Integrates Phase 3 and Phase 4 on Jetson, runs end-to-end tests adjusted for the Tegra environment, and finalizes Jetson-specific documentation.

The "needs validation when ported" markers cover the integration test (which runs Jetson-specific tool invocations), the documentation (which references Jetson-specific install commands), and the SBOM (which captures Jetson-specific dependency hashes).

---

<role>
You are a senior harness engineer wiring together the Jetson harness layers and producing the final documentation for the Jetson section.

Use the writer/reviewer subagent pattern from `jetson/harness/agents/writer-reviewer.md`. One agent writes, one reviews against the Quality Contract and the parity requirement.
</role>

<effort>xhigh</effort>
<mode>default</mode>
<thinking>adaptive</thinking>
<context_budget>Run /context at start. Plan for compaction.</context_budget>
<parallel_tool_calls>Parallel reads of foundation, Mac reference, and prior Jetson phase outputs.</parallel_tool_calls>
<scope>Strict. Only artifacts named below.</scope>

<context>
Phases 3 and 4 produced the Jetson harness files. Phase 5:

Runs an end-to-end integration test adapted for the Jetson environment.

Finalizes Jetson-specific documentation: `jetson/README.md` updates, `jetson/USER_GUIDE.md` (Jetson-specific quickstart and operational notes), `jetson/HARNESS_GUIDE.md` (Jetson-specific technical reference).

Updates `JOURNEY.md` with the Jetson build narrative entry.

Produces a Jetson-specific SBOM at `jetson/harness/sbom.cdx.json`.
</context>

<validation_markers>
Integration test: the test sequence is identical to Mac in shape but runs on Jetson tooling. Verify that Semgrep on aarch64 catches the same synthetic SQL injection as on Mac. Verify the pre-commit hook chain executes cleanly on Jetson.

Documentation: the `jetson/USER_GUIDE.md` install commands must be runnable on a fresh JetPack install. Verify each command actually works on a representative Jetson AGX Orin.

SBOM: verify syft runs on aarch64 against the Jetson Python environment. If syft is unavailable for aarch64, document an alternative (e.g., `pip freeze` plus manual hash collection).

Document validations in `phase-outputs/PHASE_5_VALIDATION.md`.
</validation_markers>

<instructions>
### 1. `jetson/scripts/integration-test.sh`

Adapted from `mac/scripts/integration-test.sh` (created during Mac Phase 5). Jetson-specific differences:

Synthetic project directory path uses `/tmp/jetson-harness-test/`.

Tool install verification covers Jetson-specific paths.

Hook trigger sequence is identical to Mac.

### 2. `jetson/USER_GUIDE.md`

Jetson-specific quickstart and daily-use guide. Sections mirror the root `USER_GUIDE.md` with Jetson tool install commands and operational notes.

### 3. `jetson/HARNESS_GUIDE.md`

Jetson-specific technical reference. Covers the five layers with Jetson tool substitutions, the three-layer security stack on Jetson, and the Jetson-specific re-evaluation triggers for QC.5.

### 4. Update `jetson/README.md`

Build status table: all phases move to "Validated" if validation succeeds.

Link to `jetson/USER_GUIDE.md` and `jetson/HARNESS_GUIDE.md` from the routing section.

### 5. Update `JOURNEY.md`

Add a Jetson Phase 5 entry summarizing what was built, what was validated, and what limitations remain.

### 6. SBOM

Generate at `jetson/harness/sbom.cdx.json`. CycloneDX format. Document the generator and version.

### 7. Verification

```bash
pre-commit run --all-files
./scripts/drift-check.sh
jetson/scripts/integration-test.sh
```

All must pass.

Document in `phase-outputs/PHASE_5_VALIDATION.md`.

### 8. Commit and release tag

AP.5 commit. Tag `jetson-v1.0.0` annotating the validated Jetson release.

Use the writer/reviewer pattern for the documentation writes. Three iterations maximum per artifact.
</instructions>

<deliverable>
Integration test script, USER_GUIDE.md, HARNESS_GUIDE.md, README updates, JOURNEY entry, SBOM, validation document, commit, tag. Short summary report.
</deliverable>

<verification>
Integration test passes end-to-end on Jetson hardware.

All pre-commit hooks pass.

Drift check passes.

Writer/reviewer iterations on documentation: 3 or fewer per artifact.

If any verification fails, do not declare Phase 5 validated. Document and propose resolution.
</verification>
