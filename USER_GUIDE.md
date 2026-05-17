# User Guide

How to adopt and use the harness day to day. This guide is written for a developer who is not me, has never seen the harness before, and wants to start using it on their own project. For the technical reference, see `HARNESS_GUIDE.md`. For the design reasoning, see `foundation/`.

## Before you start

You need:

A target project (any language). The harness adopts into existing projects.

Claude Code installed and configured. The harness is pinned to v2.1.x. Verify with `claude --version`.

A package manager appropriate to your platform: Homebrew on macOS, apt on Jetson, Chocolatey or WSL2 on Windows.

Python 3.12+ on PATH. The pre-commit framework requires it.

Git, obviously.

If any of those is missing, the harness will tell you at session-start time. The session-start hook is your first line of "is this set up right."

## Quickstart on macOS

The Mac section is the validated reference. Jetson and Windows follow the same pattern with platform-specific tools (see `HARNESS_GUIDE.md` cross-platform equivalency table).

### Step 1: install dependencies

```bash
brew install jq semgrep gitleaks shellcheck pre-commit
pipx install pre-commit
```

If `pipx` is not available, install with `python3 -m pip install --user pre-commit`. Use whichever fits your Python environment management.

### Step 2: clone the reference repo

```bash
git clone https://github.com/rocklambros/harness-engineering.git
cd harness-engineering
./scripts/pre-flight.sh
```

The pre-flight script moves research documents to `research/` and chmods the hook scripts. It is idempotent. Safe to re-run.

### Step 3: read the foundation docs

In this order:

`foundation/00-quality-contract.md` (the five properties that bind everything).

`foundation/01-threat-model.md` (what we're defending against).

`foundation/02-architectural-principles.md` (why the harness has the shape it does).

`mac/ARCHITECTURE.md` (the Mac-specific design).

Skipping this step makes adopting the harness harder, not easier. The configuration choices below have rationale that lives in these docs.

### Step 4: adopt the harness into your target project

Copy the relevant `harness/` directory into your target project:

```bash
cp -r mac/harness /path/to/your-project/harness
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

Merge `.gitignore.harness` into your existing `.gitignore` (or just rename it if your project has no existing gitignore).

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

Expect to see hook output occasionally as you work. That is the system working. If you never see hook output, either the hook is misconfigured (run `./scripts/drift-check.sh`) or your code is squeaky clean (rare).

When you commit, the pre-commit hooks run the full SAST stack. If anything fails, the commit is blocked. Fix the findings, re-stage, re-commit.

## How the security-review skill loads

The skill is in `harness/skills/security-review/`. Claude Code's skill discovery loads it automatically. You do not invoke it manually.

The skill loads its pattern content based on the file type you are touching. Editing a Python file loads the Python-relevant patterns (SQL injection, command injection, input validation, hardcoded secrets, dependency risks). Editing a JavaScript file loads the JS-relevant ones (XSS, input validation, hardcoded secrets, dependency risks, auth failures).

You will not see the skill content in your session output. It is loaded into Claude's context, not displayed to you. The effect is that Claude proactively avoids the patterns the skill covers when generating new code.

## Daily commands

| Command | Purpose |
| --- | --- |
| `./scripts/drift-check.sh` | Verify references resolve and hook scripts pass shellcheck |
| `pre-commit run --all-files` | Run the full pre-commit SAST stack against the whole repo |
| `pre-commit run --files <path>` | Run pre-commit against a specific file |
| `tail -f ~/.claude-harness/hook.log` | Watch hook activity in real time |
| `tail -f ~/.claude-harness/shell-audit.log` | Watch shell command activity |

## Troubleshooting

**The post-tool-use Semgrep hook is silent on every file.** Either you have not touched a file the hook covers (check the extension allow-list in the hook script), or Semgrep is not installed. Run `which semgrep`. If missing, `brew install semgrep`.

**The hook errors with "jq is required."** Install jq: `brew install jq`. The harness depends on jq for hook payload parsing.

**Claude Code reports "the harness is asking me to read a file outside the allow list."** Check `harness/rules/paths.deny`. If the path is legitimately needed, add it to the allow list in `.claude/settings.json` with rationale in a commit.

**The pre-commit hook chain takes 30+ seconds on every commit.** This is expected on first run because Semgrep downloads rule packs. Subsequent runs use the cache. If it stays slow, check Semgrep's cache location at `~/.cache/semgrep/`.

**The drift check fails with "reference to undefined Quality Contract ID."** You probably cited a QC property that does not exist in `foundation/00-quality-contract.md`. Either fix the citation or add the property to the QC file (with rationale and a JOURNEY entry).

**A session is mid-build and context fills up.** The pre-compact hook writes a preservation file at `phase-outputs/.compact-preserve.md`. After compaction, the session-start hook on the next session can read it to restore context. If preservation does not happen, the most recently modified file in `phase-outputs/` is the recovery anchor.

**Semgrep on Windows misses a rule pack you expected.** Switch to WSL2 per the Windows ARCHITECTURE.md decision. The native Windows binary has spotty rule-pack coverage as of build time.

**The cache cost on direct API calls jumped after a Claude Code update.** Check whether telemetry got disabled or the cache TTL default changed. The March 2026 regression is the canonical example. Set `cache_control.ttl` to `"1h"` explicitly in your API calls per QC.4a.

## Customizing the harness for your project

The harness ships with defaults that work for most projects. Customize through commits with rationale.

To add a new rule, edit `harness/rules/paths.deny` or `commands.deny`. The change applies on the next session.

To add a new security pattern, create a file in `harness/skills/security-review/patterns/`. Add the entry to `SKILL.md` mapping the pattern to file types. The pattern loads on demand the next time a covered file is touched.

To add a new hook, write the script in `harness/hooks/`. Register it in `.claude/settings.json`. Add an entry to `harness/hooks/README.md` and trace it to a Quality Contract property.

To remove a layer of the security stack, file an issue with rationale. The three-layer composition is binding per AP.2. Removing a layer needs an explicit replacement that covers the same threats.

## What this guide does not cover

How to write Claude Code prompts well. Read `foundation/04-research-references.md` R.1.3 (Anthropic prompt engineering documentation) for that.

How to extend Claude Code itself (custom tools, MCP servers, model selection). Those are out of scope; the harness configures Claude Code, it does not extend it.

How to choose between the three platforms. They are not alternatives; the harness ships for all three so you can run the same workflow across machines. If you only have one platform, just use that section.

How to evaluate other harnesses. See `foundation/03-seed-evaluation-methodology.md`. The rubric there applies.
