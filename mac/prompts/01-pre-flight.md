# Pre-flight Prompt (Mac)

This prompt is run once before Phase 0. It executes the bash to move the three research documents from the repo root into `research/`, normalizes the SAGE filename, and verifies the repo structure is in the expected shape.

This is not a build phase. It is a setup task.

---

<role>
You are a senior harness engineer setting up the working directory for a multi-phase Claude Code build. Your only job in this prompt is to run the pre-flight script and verify the result. Do not start any other work.
</role>

<effort>medium</effort>
<mode>default</mode>
<thinking>adaptive</thinking>
<scope>Strict. Apply only to the pre-flight setup. Do not touch any other directory or file.</scope>

<context>
The repo at `/Users/klambros/harness-engineering/` was seeded with three research documents in the root directory (legacy state). They need to be moved to `research/`. The SAGE document filename contains a space that needs to be normalized.

The `scripts/pre-flight.sh` script handles this. Your job is to run it, verify the result, and report.
</context>

<instructions>
Run the pre-flight script:

```bash
cd /Users/klambros/harness-engineering
chmod +x scripts/pre-flight.sh
./scripts/pre-flight.sh
```

After the script completes, verify three things:

The `research/` directory contains exactly three files: `Claude_Architecture.md`, `Harness_Engineering_for_Claude_Code_A_Systems_Architecture_Analysis.md`, and `NIST.SP.800-218-Secure-Software-Development-Framework.md`. If any are missing or there are extras, report what you found.

The repo root no longer contains any of the three research documents. If any remain in root, report which.

All shell scripts in `scripts/`, `mac/scripts/`, and `mac/harness/hooks/` are executable. The pre-flight script chmods them; verify with `ls -la`.

Report the result in a short prose block. State which files moved, which already were in place, and whether the verification passed.

If any verification fails, do not attempt to fix it. Report the failure and stop. The next step depends on understanding what's actually on disk, not what I expected to be on disk.
</instructions>

<deliverable>
A short prose report (3-6 sentences) describing the pre-flight result and verification status. No file changes beyond what the script does. No commit.
</deliverable>
