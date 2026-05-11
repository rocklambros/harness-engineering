# Phase 3 — Deterministic Layer (Windows) [SCAFFOLDED]

**This prompt is scaffolded, not validated.** The structure mirrors `mac/prompts/phase-3-deterministic-layer.md`. Windows-specific details carry `<NEEDS-WINDOWS-PORT-VALIDATION>` markers that resolve when Rock executes the Windows build.

<role>
You are writing the deterministic enforcement layer of the Windows harness: hook scripts, deny rules, sandbox configuration, permission-mode posture in `windows/harness/settings.json`. Every threat Phase 2 elected to enforce in hooks lands here. Every constraint that must hold every time the harness runs on Windows lands here.

This is the most consequential phase for harness security on Windows. The model has no veto over a hook. Hooks fire regardless of context, prompt design, or conversation length.
</role>

<effort>xhigh</effort>

<mode>default mode (writes). Phase 3 produces hook scripts, deny rule files, and the settings.json fill.</mode>

<thinking>adaptive</thinking>

<context_budget>Run /context at start and end. Phase 3 reads several foundation documents, Phase 2 outputs, and `Claude_Architecture.md` for hook-event specifics. Record in `phase-outputs/PHASE-3-CONTEXT.md`.</context_budget>

<parallel_tool_calls>
Read inputs in parallel: `phase-outputs/ANSWERS.md`, `phase-outputs/INVENTORY.md`, `windows/ARCHITECTURE.md`, `windows/harness/settings.json.template`, `windows/harness/rules/README.md`, `windows/harness/hooks/README.md`, `foundation/01-threat-model.md`, `foundation/02-architectural-principles.md`, relevant sections of `research/Claude_Architecture.md`. Also read the Mac and Jetson equivalents if those builds have run.
</parallel_tool_calls>

<scope>
Apply only to:
- `windows/harness/hooks/` (writes: one PowerShell, Python, or WSL2-bash script per hook, per Phase 2's language decision)
- `windows/harness/rules/` (writes: one markdown file per rule)
- `windows/harness/settings.json` (writes: populated settings file. Template stays unchanged.)
- `windows/evaluations/deep-eval.md` (updates: integration results for security-tool seeds)
- `phase-outputs/PHASE-3-CONTEXT.md` (writes)
- `phase-outputs/PHASE-3-NOTES.md` (writes: rationale per hook and per rule)

Do not modify `foundation/`, `research/`, `windows/prompts/`, `windows/harness/CLAUDE.md`, `windows/harness/skills/`, `windows/harness/agents/`, `windows/ARCHITECTURE.md`, or `windows/README.md`.
</scope>

## What to do

Three kinds of artifacts: hook scripts, deny rule files, populated `settings.json`. Same as Mac and Jetson Phase 3 with Windows port validations.

### Hook scripts

For each threat Phase 2 elected to enforce in a hook, write a hook script in `windows/harness/hooks/`. Script language follows Phase 2's decision (PowerShell 5.1, PowerShell 7+, Python, or WSL2-bash routed). Each script:

- Carries a header block (purpose, threat addressed, foundation citation, verification test, execution context).
- Is PSScriptAnalyzer-clean for PowerShell. SAST-clean for Python. Shellcheck-clean for any WSL2-routed bash.
- Returns the correct Zod-validated output schema per Claude_Architecture.md §5.3 and §6.
- Sets `permissionDecision` to `deny` or `ask` when blocking. Never to `allow` to bypass subsequent checks.
- Returns within a reasonable timeout. WSL2 routing latency is a known cost; Phase 3 measures and confirms within budget.

Mac wrote 6 Python hooks uniformly (per `phase-outputs/PHASE-3-NOTES.md`), choosing Python over shell because every hook parses JSON on stdin. If Windows follows the same Python uniformity, the verification narrows to Python runtime parity (interpreter path, `json` stdlib, native vs WSL2 placement per Phase 2). If Windows elects PowerShell or WSL2-bash, the per-hook port verifies:

- PowerShell version compatibility (5.1 vs 7+) if PowerShell is the chosen language.
- Path canonicalization. Forward slash vs backslash applied consistently per Phase 2's decision.
- Line endings. Bash scripts under WSL2 require LF. PowerShell tolerates both.
- Execution policy. `RemoteSigned` minimum. Hook scripts run under this policy without bypass flags.
- WSL2 routing latency (if applicable). Startup cost measured; if exceeding PreToolUse budget, the routing decision gets revisited.
- Process invocation semantics. PowerShell `Start-Process` vs direct invocation. Exit codes captured via `$LASTEXITCODE` when needed.

Mandatory hooks (drawn from `foundation/01-threat-model.md`):

- **PreToolUse subcommand cap**: rejects Bash chains over 50 subcommands. Adversa.ai 2026 bypass class.
- **PreToolUse external write gate**: requires explicit confirmation for writes outside the working directory. Principle 3 reversibility.
- **SessionStart pre-trust audit**: refuses to load a project whose `.claude/settings.json` or `.mcp.json` was modified after the last recorded audit. CVE-2025-59536 class.
- **PreToolUse MCP server allowlist enforcement**: rejects MCP tool calls whose server is not on the allowlist.

Optional hooks Phase 2 may have elected: same as Mac and Jetson (PreCompact preserver, UserPromptSubmit injection scanner, PostToolUse output classifier).

### Deny rules

For each blanket-deny pattern Phase 2 elected, write a file in `windows/harness/rules/`. Each rule file holds the pattern, the threat or QC property addressed, the citation, and the test.

Mac wrote 6 deny rules (per `phase-outputs/PHASE-3-NOTES.md`): bash-deny-git-push-force, bash-deny-dangerously-skip-permissions, bash-deny-sudo, bash-deny-rm-rf-root, filesystem-deny-write-secrets, mcp-deny-server-prefix-default. Pattern-syntax caveat from Mac Phase 5 audit (F02): empty-prefix patterns like `Bash(:*--dangerously-skip-permissions*)` do not enforce in Claude Code v2.1.138; Mac simplified to `Bash(claude --dangerously-skip-permissions:*)`. Per-rule port verifies:

- Windows path conventions in the pattern match the Phase 2 canonicalization decision. Forward slash where accepted, backslash where required, consistent within a rule.
- `bash-deny-rm-rf-root` Mac patterns target `~/`, `$HOME`, `/Users/`. Windows equivalents target `%USERPROFILE%`, `C:\Users\`, and the WSL2-distribution roots if WSL2 is in play. `bash-deny-sudo` has no Windows equivalent (UAC elevation differs structurally); the deny rule may swap to a `runas` or `Start-Process -Verb RunAs` pattern.
- Rules using regex match the regex engine the rule will be evaluated against (PowerShell's .NET regex differs from POSIX ERE on edges).

Examples ported from Mac and Jetson patterns:

- `powershell-deny-recursive-delete-outside-cwd.md`: same intent as `bash-deny-rm-outside-cwd.md`, adapted to PowerShell semantics.
- `bash-deny-curl-without-allowlist.md`: same pattern (curl works on PowerShell as a `Invoke-WebRequest` alias unless removed; rule constrains the underlying behavior).
- `filesystem-deny-write-secrets-dir.md`: same pattern, Windows path verification.
- `mcp-deny-server-prefix-default.md`: same pattern, no platform delta.

### settings.json fill

Update `windows/harness/settings.json` (not the template) with the populated values. Same structure as Mac and Jetson but with Windows-specific paths, the Windows Claude Code version pin from Phase 0, and the subsystem field reflecting Phase 2's WSL2 decision.

The MCP server allowlist stays empty. Phase 4 populates.

### Deep-evaluate security-tool seeds

Phase 1 surveyed and pre-filtered. Phase 3 deep-evaluates survivors that touch the deterministic layer, with Windows-specific validation per `windows/evaluations/deep-eval.md` format.

### Anti-overengineering block

Hooks and rules address Phase 2 elected threats. Do not add hooks for threats Phase 2 did not elect. Record new threats surfaced in Phase 3 in `PHASE-3-NOTES.md` for Phase 2 to revisit.

Do not create new abstractions or helper libraries.

Do not write test scaffolding beyond what the rule and hook headers prescribe.

Do not edit `windows/harness/CLAUDE.md`. Phase 5.

<investigate_before_answering>
Before writing a hook that returns a specific Zod schema field, read `research/Claude_Architecture.md` §5.3 and §6.

Before claiming a deny rule pattern matches a specific behavior, write the rule and exercise it against a test input on Windows.

Before recording that a security tool integrates cleanly on Windows, run the tool against known-vulnerable and known-clean fixtures.

Marker resolution: for each ported pattern, run the equivalent on Windows and confirm behavior matches. Mac Phase 3 validated all 15 hook+rule test cases first run (per `phase-outputs/PHASE-3-NOTES.md`); Windows baselines its own equivalent set. The validation outcome lands in the hook or rule header.
</investigate_before_answering>

## Deliverables

- Hook scripts in `windows/harness/hooks/`, one per Phase-2-elected threat, each with Windows port validation outcome in header.
- Deny rule files in `windows/harness/rules/`, one per blanket-deny pattern.
- Populated `windows/harness/settings.json` with all Phase 3 fields filled; MCP allowlist deferred to Phase 4.
- Updated `windows/evaluations/deep-eval.md` with security-tool integration outcomes (including Windows-specific validation).
- `phase-outputs/PHASE-3-NOTES.md` with rationale.
- `phase-outputs/PHASE-3-CONTEXT.md`.

## Verification

Before reporting complete:

- PowerShell hooks pass `Invoke-ScriptAnalyzer`.
- Python hooks pass SAST.
- WSL2-bash hooks pass `shellcheck`.
- `windows/harness/settings.json` parses as strict JSON.
- Each hook's header verification command returns expected.
- The drift check returns 0 from a bash environment.
- Line counts reported.

Report hook count, deny rule count, line counts, validation outcomes.

## Anti-overengineering reminder

The trap is starting to feel productive by writing more hooks than Phase 2 elected. Resist. Every additional hook is additional surface. Hooks enforce what must hold every time.

When in doubt about hook vs deny rule, prefer deny rule. Simpler to audit, faster to evaluate. Hooks reserved for cases deny rules cannot express.
