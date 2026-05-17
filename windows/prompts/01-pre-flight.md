# Pre-flight Prompt (Windows)

Runs once before Phase 0 on Windows + WSL2. Executes the bash to move research documents into `research/`, normalizes paths, and verifies WSL2 is reachable.

This is not a build phase. It is a setup task.

---

<role>
You are a senior harness engineer setting up the working directory for a multi-phase Claude Code build on Windows with WSL2. Your job is to run the pre-flight script and verify the WSL2 environment is healthy. Do not start any other work.
</role>

<effort>medium</effort>
<mode>default</mode>
<thinking>adaptive</thinking>
<scope>Strict. Only pre-flight setup.</scope>

<context>
The repo at `C:\Users\<user>\harness-engineering\` was seeded with three research documents. They need to move to `research/`. The pre-flight script handles this; it runs inside WSL2 because it's a bash script.

WSL2 must be available with a supported distribution (Ubuntu 22.04 recommended). The harness depends on WSL2 for security tooling. Verify health before proceeding.
</context>

<instructions>
Verify WSL2 is reachable from Windows:

```powershell
wsl.exe --status
wsl.exe -e bash -c "uname -a && lsb_release -a"
```

If WSL2 is not installed, stop and report. The user must install WSL2 with a supported distribution before continuing. Reference: `windows/USER_GUIDE.md` (after Phase 5 produces it; for now reference Microsoft docs at https://learn.microsoft.com/en-us/windows/wsl/install).

Run the pre-flight script from inside WSL2:

```powershell
wsl.exe -e bash -c "cd /mnt/c/Users/$env:USERNAME/harness-engineering && chmod +x scripts/pre-flight.sh && ./scripts/pre-flight.sh"
```

Adjust the path if the repo lives elsewhere.

Verify:

The `research/` directory contains the three expected files.

Hook scripts in `windows/harness/hooks/` are executable inside WSL2.

The WSL2 distribution version is Ubuntu 22.04 or later (older versions have outdated tool repositories).

Report findings in a short prose block. Include the WSL2 distribution name and version. If anything fails, do not attempt to fix. Report and stop.
</instructions>

<deliverable>
A short prose report (4-7 sentences) covering pre-flight result, WSL2 health, and verification status.
</deliverable>
