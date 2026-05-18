# Jetson User Guide

How to adopt and use the harness on NVIDIA Jetson AGX Orin (or compatible Jetson devices running JetPack R36). This guide is written for a developer who has never seen the harness before. For the technical reference, see `HARNESS_GUIDE.md`. For the design reasoning, see `foundation/`.

## Before you start

You need:

A target project (any language). The harness adopts into existing projects.

Claude Code installed and configured. The harness is pinned to v2.1.x. Verify with `claude --version`.

Python on PATH. The Jetson ships with system Python 3.10 and may have Anaconda 3.12. The pre-commit framework requires Python 3.8+.

`apt` for system packages. The Jetson runs Ubuntu 22.04 (JetPack R36).

Git installed and configured.

If any of those is missing, the session-start hook tells you at the beginning of every Claude Code session.

## Quickstart on Jetson

### Step 1: install dependencies

Run the install script from the repo:

```bash
cd harness-engineering
./jetson/scripts/install-harness-tools.sh
```

This installs Semgrep 1.163.0 (in both conda base and system Python 3.10), pre-commit 4.6.0 (conda), gitleaks v8.21.2 (/usr/local/bin/), and shellcheck 0.8.0 (apt). It also installs jq if not already present.

If you prefer manual installation:

```bash
sudo apt install -y jq shellcheck
pip install semgrep==1.163.0
pip install pre-commit
```

For gitleaks, download the ARM64 Linux binary from the GitHub releases page and place it in `/usr/local/bin/`.

### Step 2: clone the reference repo

```bash
git clone https://github.com/rocklambros/harness-engineering.git
cd harness-engineering
./scripts/pre-flight.sh
```

The pre-flight script moves research documents to `research/` and chmods the hook scripts. It is idempotent.

### Step 3: read the foundation docs

In this order:

`foundation/00-quality-contract.md` (the five properties that bind everything).

`foundation/01-threat-model.md` (what we defend against).

`foundation/02-architectural-principles.md` (why the harness has this shape).

`jetson/ARCHITECTURE.md` (the Jetson-specific design).

Skipping this step makes adopting the harness harder, not easier. The configuration choices below have rationale in these docs.

### Step 4: adopt the harness into your target project

Copy the Jetson harness directory into your target project:

```bash
cp -r jetson/harness /path/to/your-project/harness
cd /path/to/your-project
```

Copy the settings template, replacing the placeholder with your absolute path:

```bash
mkdir -p .claude
sed "s|{{REPO_ROOT}}|$(pwd)|g" harness/settings.json.template > .claude/settings.json
```

Copy the pre-commit config from the reference repo:

```bash
cp /path/to/harness-engineering/.pre-commit-config.yaml .
cp /path/to/harness-engineering/.gitignore .gitignore.harness
```

Merge `.gitignore.harness` into your existing `.gitignore` (or rename it if your project has no existing gitignore).

Install the pre-commit hooks:

```bash
pre-commit install
pre-commit install --hook-type commit-msg
```

Verify everything is wired:

```bash
pre-commit run --all-files
shellcheck harness/hooks/*.sh
```

If both pass, the harness is adopted. Open the project in Claude Code and start a session.

## What to expect during a session

The session-start hook runs first. It does two things:

Runs the drift check. If anything looks wrong, you get a short advisory message. The session continues.

Checks the Claude Code version against the validated range. If out of range, you get a warning. Sessions still work, but the Quality Contract guarantees may be stale.

While you write code, the post-tool-use Semgrep hook runs after every Write or Edit. It scans the changed file and surfaces any findings to Claude in the same session. Claude reads the findings and fixes in place.

Expect to see hook output occasionally as you work. That is the system working. If you never see hook output, either the hook is misconfigured (run `scripts/drift-check.sh`) or your code is clean.

When you commit, the pre-commit hooks run the full SAST stack. If anything fails, the commit is blocked. Fix the findings, re-stage, re-commit.

## How the security-review skill loads

The skill is in `harness/skills/security-review/`. Claude Code discovers it automatically. You do not invoke it manually.

The skill loads its pattern content based on the file type you are touching. Editing a Python file loads the Python-relevant patterns (SQL injection, command injection, input validation, hardcoded secrets, dependency risks). Editing a JavaScript file loads the JS-relevant ones (XSS, input validation, hardcoded secrets, dependency risks, auth failures).

You will not see the skill content in your session output. It loads into Claude's context, not displayed to you. The effect is that Claude proactively avoids the patterns the skill covers when generating new code.

## Daily commands

| Command | Purpose |
| --- | --- |
| `./scripts/drift-check.sh` | Verify references resolve and hook scripts pass shellcheck |
| `pre-commit run --all-files` | Run the full pre-commit SAST stack against the whole repo |
| `pre-commit run --files <path>` | Run pre-commit against a specific file |
| `jetson/scripts/integration-test.sh` | Run the end-to-end harness integration test |
| `tail -f ~/.claude-harness/hook.log` | Watch hook activity in real time |
| `tail -f ~/.claude-harness/shell-audit.log` | Watch shell command activity |

## Jetson-specific notes

**CUDA files.** The PostToolUse Semgrep hook scans `.cu` and `.cuh` files. The `security-review` skill does not load CUDA-specific guidance patterns. Semgrep's default and security-audit rule packs provide baseline coverage for CUDA source files.

**Power management.** The harness blocks `nvpmodel -m` (mode-switching) through the settings.json deny list. Read-only commands like `nvpmodel -q` and `jetson_clocks --show` are allowed. Bare `jetson_clocks` (which enables max clocks) is not blocked by the deny list because Claude Code's prefix-matching cannot distinguish it from `jetson_clocks --show`. Exercise caution with power management commands during sessions.

**GNU coreutils.** The Jetson uses GNU coreutils, not BSD. The harness hooks account for this. The `stat` command uses `-c '%Y %n'` (GNU) instead of `-f '%m %N'` (macOS). If you port a hook from Mac, check for BSD-specific flags.

**Tegra paths.** The paths deny list blocks reads from `/proc/nvtegra/*` and `~/.nvidia-jetson/**`. These are Tegra-specific hardware configuration paths that should not be modified through Claude Code sessions.

## Troubleshooting

**The post-tool-use Semgrep hook is silent on every file.** Either you have not touched a file the hook covers (check the extension allow-list in the hook script), or Semgrep is not installed. Run `which semgrep`. If missing, `pip install semgrep==1.163.0`.

**The hook errors with "jq is required."** Install jq: `sudo apt install jq`. The harness depends on jq for hook payload parsing.

**Claude Code reports "the harness is asking me to read a file outside the allow list."** Check `harness/rules/paths.deny`. If the path is legitimately needed, add it to the allow list in `.claude/settings.json` with rationale in a commit.

**The pre-commit hook chain takes 30+ seconds on every commit.** This is expected on first run because Semgrep downloads rule packs. Subsequent runs use the cache. If it stays slow, check Semgrep's cache location at `~/.cache/semgrep/`.

**The drift check fails with "reference to undefined Quality Contract ID."** You probably cited a QC property that does not exist in `foundation/00-quality-contract.md`. Either fix the citation or add the property to the QC file with rationale and a JOURNEY entry.

**A session is mid-build and context fills up.** The pre-compact hook writes a preservation file at `phase-outputs/.compact-preserve.md`. After compaction, the session-start hook on the next session can read it to restore context. If preservation does not happen, the most recently modified file in `phase-outputs/` is the recovery anchor.

**Semgrep fails to install with a wheel error.** Verify your Python version. Semgrep 1.163.0 supports Python 3.10 and 3.12 on aarch64. Older Python versions or 3.11 may lack pre-built wheels.

## Customizing the harness for your project

The harness ships with defaults that work for most projects. Customize through commits with rationale.

To add a new rule, edit `harness/rules/paths.deny` or `commands.deny`. The change applies on the next session.

To add a new security pattern, create a file in `harness/skills/security-review/patterns/`. Add the entry to `SKILL.md` mapping the pattern to file types. The pattern loads on demand the next time a covered file is touched.

To add a new hook, write the script in `harness/hooks/`. Register it in `.claude/settings.json`. Add an entry to `harness/hooks/README.md` and trace it to a Quality Contract property.

To remove a layer of the security stack, file an issue with rationale. The three-layer composition is binding per AP.2. Removing a layer needs an explicit replacement that covers the same threats.

## What this guide does not cover

How to write Claude Code prompts well. Read `foundation/04-research-references.md` R.1.3 for that.

How to extend Claude Code itself (custom tools, MCP servers, model selection). Those are out of scope. The harness configures Claude Code, it does not extend it.

How to choose between the three platforms. They are not alternatives. The harness ships for all three so you can run the same workflow across machines. If you only have one platform, use that section.

How to evaluate other harnesses. See `foundation/03-seed-evaluation-methodology.md`. The rubric there applies.
