# Pre-flight Prompt (Jetson)

This prompt is run once before Phase 0 against the Jetson AGX Orin. It executes the bash to move the three research documents from the repo root into `research/` and normalizes paths.

This is not a build phase. It is a setup task.

---

<role>
You are a senior harness engineer setting up the working directory for a multi-phase Claude Code build on an NVIDIA Jetson AGX Orin. Your only job in this prompt is to run the pre-flight script and verify the result. Do not start any other work.
</role>

<effort>medium</effort>
<mode>default</mode>
<thinking>adaptive</thinking>
<scope>Strict. Apply only to the pre-flight setup. Do not touch any other directory or file.</scope>

<context>
The repo at the project root on the Jetson (typically `/home/jetson/harness-engineering/`) was seeded with three research documents in the root directory. They need to be moved to `research/`. The SAGE document filename contains a space that needs to be normalized.

The `scripts/pre-flight.sh` script handles this. It is the same script used on Mac because the operation is platform-agnostic.
</context>

<instructions>
Run the pre-flight script:

```bash
cd "$HOME/harness-engineering" || cd /home/jetson/harness-engineering
chmod +x scripts/pre-flight.sh
./scripts/pre-flight.sh
```

After the script completes, verify three things:

The `research/` directory contains exactly three files: `Claude_Architecture.md`, `Harness_Engineering_for_Claude_Code_A_Systems_Architecture_Analysis.md`, and `NIST.SP.800-218-Secure-Software-Development-Framework.md`.

The repo root no longer contains any of the three research documents.

All shell scripts in `scripts/`, `jetson/scripts/`, and `jetson/harness/hooks/` are executable.

Report the result in a short prose block. If any verification fails, do not attempt to fix it. Report the failure and stop.

Additionally, verify the JetPack version and CUDA availability for context (these inform Phase 1 inventory):

```bash
cat /etc/nv_tegra_release 2>/dev/null | head -n 1 || echo "JetPack info unavailable"
nvcc --version 2>/dev/null | tail -n 1 || echo "CUDA toolkit not on PATH"
```

Report what you find. The information feeds Phase 1.
</instructions>

<deliverable>
A short prose report (4-7 sentences) describing the pre-flight result, the JetPack/CUDA context, and verification status.
</deliverable>
