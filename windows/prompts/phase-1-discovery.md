# Phase 1: Discovery (Windows)

Read-only inventory of the Windows + WSL2 environment.

---

<role>
You are a senior harness engineer in the discovery phase on Windows + WSL2. Inventory the Windows host, the WSL2 environment, and surface conflicts.
</role>

<effort>high</effort>
<mode>plan</mode>
<thinking>adaptive</thinking>
<context_budget>Run /context at start.</context_budget>
<parallel_tool_calls>Heavy use.</parallel_tool_calls>
<scope>Strict. `phase-outputs/INVENTORY.md`, `CONFLICTS.md`, `QUESTIONS.md` only.</scope>

<context>
The Windows host runs Claude Code natively. The WSL2 instance runs the security tooling. Inventory both.

Mac Phase 1 (`mac/phase-outputs/INVENTORY.md` if available) is the structural reference. Adapt to the Windows + WSL2 environment.
</context>

<investigate_before_answering>
Concrete checks (run in parallel where possible):

Windows host:
```powershell
wsl.exe --status
wsl.exe --list --verbose
claude --version
choco list --localonly 2>&1 | findstr /i "semgrep gitleaks shellcheck jq"
where claude
```

WSL2 environment:
```powershell
wsl.exe -e bash -c "uname -a && lsb_release -a"
wsl.exe -e bash -c "which semgrep gitleaks shellcheck jq pre-commit python3"
wsl.exe -e bash -c "semgrep --version 2>&1 | head -1; gitleaks version 2>&1; shellcheck --version 2>&1 | head -2"
wsl.exe -e bash -c "python3 --version && pip3 list --user 2>&1 | head -30"
```

Path translation:
```powershell
wsl.exe -e bash -c "ls /mnt/c/Users/$env:USERNAME/harness-engineering/ 2>&1 | head -5"
```

Git configuration on Windows:
```powershell
git config --get core.autocrlf
git config --get core.eol
```

Memory and disk on the host and inside WSL2.
</investigate_before_answering>

<instructions>
Produce three files in `phase-outputs/`.

**`INVENTORY.md`** sections:

Windows host: OS version, Claude Code version, Chocolatey packages of interest.

WSL2 environment: distribution, kernel, key packages, Python environment.

Path translation: Windows-vs-WSL2 path conventions, autocrlf settings.

Security tools: tool, version, install method (WSL2 apt, WSL2 pip, Windows Chocolatey, missing).

Pre-existing conventions: CLAUDE.md files, pre-commit configs.

**`CONFLICTS.md`** entries with severity. Likely Windows-specific conflicts:

WSL2 not installed or wrong distribution (blocker).

`core.autocrlf=true` on Windows side (blocker; can corrupt hook script line endings).

Old WSL2 distribution with outdated package versions (warning).

Semgrep not in WSL2 (blocker).

**`QUESTIONS.md`** numbered multiple-choice. Examples:

"Set Windows-side git to `core.autocrlf=false` for this repo (A), `core.autocrlf=input` (B), or rely on .gitattributes (C)?"

"Invoke hooks through `wsl.exe -e bash` (A), `wsl.exe -d <distro> -e bash` (B), or `wsl.exe -- bash` (C)?"

"How should the harness handle WSL2 cold-start latency on the first hook of a session: pre-warm WSL2 in session-start (A), accept the cold-start cost (B), or use a long-running WSL2 daemon (C)?"

Match the writing rules.
</instructions>

<deliverable>
Three files in `phase-outputs/`. Short summary report.
</deliverable>

<verification>
`./scripts/drift-check.sh` passes.

Line count: INVENTORY 80-300, CONFLICTS 0-100, QUESTIONS 30-120.
</verification>
