# Phase 1: Discovery (Jetson)

Produces a read-only inventory of the Jetson environment: JetPack version, installed tools, Python environment, package availability, and conflicts with the harness target state.

Same structure as Mac Phase 1, with the inventory commands adjusted for the Jetson environment.

---

<role>
You are a senior harness engineer in the discovery phase of a Claude Code harness build on Jetson AGX Orin. Your job is to inventory the existing state, surface conflicts with the Phase 0 goals, and produce a list of questions for Phase 2.

This is a read-only phase. Do not modify any file outside `phase-outputs/`.
</role>

<effort>high</effort>
<mode>plan</mode>
<thinking>adaptive</thinking>
<context_budget>Run /context at start. Document delta.</context_budget>
<parallel_tool_calls>Heavily preferred for inventory reads.</parallel_tool_calls>
<scope>Strict. Only `phase-outputs/INVENTORY.md`, `phase-outputs/CONFLICTS.md`, `phase-outputs/QUESTIONS.md`.</scope>

<context>
The Phase 0 goals live at `phase-outputs/PHASE_0_GOALS.md`. Read first.

Existing state on the Jetson includes:

JetPack version (`cat /etc/nv_tegra_release`) and CUDA/cuDNN versions.

The system Python from JetPack and any user-installed Python versions (pyenv, conda).

apt-installed security tools: semgrep (probably not present by default), gitleaks (probably not), shellcheck, jq.

pip-installed tools in the system Python and any user environments.

The user's Claude Code installation and global configuration at `~/.claude/`.

Existing project conventions and pre-existing pre-commit configurations elsewhere on the Jetson.
</context>

<investigate_before_answering>
Use parallel reads. Concrete checks:

JetPack and Tegra info:
```bash
cat /etc/nv_tegra_release 2>/dev/null
uname -a
lsb_release -a
nvcc --version 2>/dev/null
```

Python environment:
```bash
which python3
python3 --version
pip3 list --user 2>/dev/null | head -50
ls -la ~/.pyenv 2>/dev/null
which pyenv 2>/dev/null
```

Security tools:
```bash
which semgrep gitleaks shellcheck jq pre-commit
semgrep --version 2>/dev/null
gitleaks version 2>/dev/null
shellcheck --version 2>/dev/null
```

Claude Code:
```bash
claude --version 2>/dev/null
ls -la ~/.claude 2>/dev/null
```

apt status:
```bash
apt list --installed 2>/dev/null | grep -E 'semgrep|gitleaks|shellcheck|jq|python3' | head -20
```

Memory and disk:
```bash
free -h
df -h ~
```
</investigate_before_answering>

<instructions>
Produce three documents in `phase-outputs/`.

**`INVENTORY.md`** sections:

Jetson platform: JetPack version, kernel, CUDA toolkit version, total memory and free disk.

Python environments: system Python, pyenv if present, conda if present, key packages.

Security tools: tool, version, install method (apt, pip, manual, missing).

Claude Code: version, config location, current settings of interest.

Pre-existing conventions: any CLAUDE.md files in other projects on this Jetson.

**`CONFLICTS.md`** entries: each with what was found, what's expected per Phase 0/QC, severity (blocker/warning/note), proposed resolution.

Likely conflicts on a fresh Jetson:

Semgrep not installed (blocker; install via pip).

gitleaks not present (blocker; install via apt or download aarch64 binary).

Python version too old or too new for pinned Semgrep (warning; resolve in Phase 2).

JetPack-shipped tool versions don't match `.pre-commit-config.yaml` pins.

**`QUESTIONS.md`** numbered multiple-choice questions for Phase 2. Surface 8-15. Examples:

"Install Semgrep via pip into JetPack Python (A), pyenv-managed Python (B), or container (C)?"

"How should the harness handle Jetson power-management commands in `commands.deny`: block all `nvpmodel` calls (A), allow read-only `nvpmodel -q` (B), or allow with explicit user confirmation (C)?"

"Do we want the security-review skill to load CUDA-specific anti-patterns when CUDA C files are touched, or leave that for a separate skill addition (A) vs. (B)?"

Match the writing rules.
</instructions>

<deliverable>
Three files in `phase-outputs/`. Short summary report at the end.
</deliverable>

<verification>
`wc -l` on the three outputs. Expected: INVENTORY 80-300, CONFLICTS 0-100, QUESTIONS 30-120.

Run `./scripts/drift-check.sh`. It must pass.
</verification>
