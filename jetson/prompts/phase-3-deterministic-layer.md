# Phase 3 — Deterministic Layer (Jetson) [SCAFFOLDED]

**This prompt is scaffolded, not validated.** The structure mirrors `mac/prompts/phase-3-deterministic-layer.md`. Jetson-specific details carry `<NEEDS-JETSON-PORT-VALIDATION>` markers that resolve when Rock executes the Jetson build. Treat each marker as a live question the executing Claude Code session must answer.

<role>
You are writing the deterministic enforcement layer of the Jetson harness: hook scripts, deny rules, sandbox configuration, permission-mode posture in `jetson/harness/settings.json`. Every threat Phase 2 elected to enforce in hooks lands here. Every constraint that must hold every time the harness runs on Jetson lands here.

This is the most consequential phase for harness security on Jetson. The model has no veto over a hook. Hooks fire regardless of context, prompt design, or conversation length.
</role>

<effort>xhigh</effort>

<mode>default mode (writes). Phase 3 produces hook scripts, deny rule files, and the settings.json fill.</mode>

<thinking>adaptive</thinking>

<context_budget>Run /context at start and end. Phase 3 reads several foundation documents, Phase 2 outputs, and `Claude_Architecture.md` for hook-event specifics. Record in `phase-outputs/PHASE-3-CONTEXT.md`.</context_budget>

<parallel_tool_calls>
Read inputs in parallel: `phase-outputs/ANSWERS.md`, `phase-outputs/INVENTORY.md`, `jetson/ARCHITECTURE.md`, `jetson/harness/settings.json.template`, `jetson/harness/rules/README.md`, `jetson/harness/hooks/README.md`, `foundation/01-threat-model.md`, `foundation/02-architectural-principles.md`, relevant sections of `research/Claude_Architecture.md`. Also read the Mac equivalent (`mac/harness/hooks/`, `mac/harness/rules/`, `mac/harness/settings.json`) if Mac has built, for porting reference.
</parallel_tool_calls>

<scope>
Apply only to:
- `jetson/harness/hooks/` (writes: one shell or Python script per hook)
- `jetson/harness/rules/` (writes: one markdown file per rule)
- `jetson/harness/settings.json` (writes: populated settings file. Template stays unchanged.)
- `jetson/evaluations/deep-eval.md` (updates: integration results for security-tool seeds)
- `phase-outputs/PHASE-3-CONTEXT.md` (writes)
- `phase-outputs/PHASE-3-NOTES.md` (writes: rationale per hook and per rule)

Do not modify `foundation/`, `research/`, `jetson/prompts/`, `jetson/harness/CLAUDE.md`, `jetson/harness/skills/`, `jetson/harness/agents/`, `jetson/ARCHITECTURE.md`, or `jetson/README.md`.
</scope>

## What to do

Three kinds of artifacts: hook scripts, deny rule files, populated `settings.json`. Same as Mac Phase 3 with port validations.

### Hook scripts

For each threat Phase 2 elected to enforce in a hook, write a hook script in `jetson/harness/hooks/`. Each script:

- Carries a header block (purpose, threat addressed, foundation citation, verification test).
- Is shellcheck-clean for shell scripts. SAST-clean for Python.
- Returns the correct Zod-validated output schema per Claude_Architecture.md §5.3 and §6.
- Sets `permissionDecision` to `deny` or `ask` when blocking; never to `allow` to bypass subsequent checks.
- Returns within a reasonable timeout.

Mac wrote 6 Python hooks uniformly (per `phase-outputs/PHASE-3-NOTES.md`), choosing Python over shell because every hook parses JSON on stdin. If Jetson follows the same Python uniformity, the port verification narrows to Python runtime parity (interpreter path, `json` stdlib, ARM64 wheels for any imported libs). If Jetson elects shell scripts, the per-hook port verifies:

- GNU vs BSD coreutils command compatibility (`grep`, `sed`, `find`, `xargs`). Mac runs BSD; Jetson runs GNU.
- Linux-specific path constructs (e.g., `/proc/`, `/sys/`, `/dev/shm/`) that do not exist on Mac.
- Linux signal handling differences from macOS.
- Bash version (`echo $BASH_VERSION`) matches expectations on the JetPack base.

Mandatory hooks (drawn from `foundation/01-threat-model.md`):

- **PreToolUse subcommand cap**: rejects Bash chains over 50 subcommands. Adversa.ai 2026 bypass class.
- **PreToolUse external write gate**: requires explicit confirmation for writes outside the working directory. Principle 3 reversibility.
- **SessionStart pre-trust audit**: refuses to load a project whose `.claude/settings.json` or `.mcp.json` was modified after the last recorded audit. CVE-2025-59536 class. Cadence per Phase 2.
- **PreToolUse MCP server allowlist enforcement**: rejects MCP tool calls whose server is not on the allowlist.

Optional hooks Phase 2 may have elected: same as Mac (PreCompact preserver, UserPromptSubmit injection scanner, PostToolUse output classifier).

### Deny rules

For each blanket-deny pattern Phase 2 elected, write a file in `jetson/harness/rules/`. Each rule file holds the pattern, the threat or QC property addressed, the citation, and the test verifying the rule fires.

Mac wrote 6 deny rules (per `phase-outputs/PHASE-3-NOTES.md`): bash-deny-git-push-force, bash-deny-dangerously-skip-permissions, bash-deny-sudo, bash-deny-rm-rf-root, filesystem-deny-write-secrets, mcp-deny-server-prefix-default. Pattern-syntax caveat from Mac Phase 5 audit (F02): empty-prefix patterns like `Bash(:*--dangerously-skip-permissions*)` do not enforce in Claude Code v2.1.138; the Mac rule was simplified to `Bash(claude --dangerously-skip-permissions:*)`. Per-rule port verifies:

- Linux path conventions in the pattern match the Jetson filesystem layout. Path separators are forward slash (same as Mac, no change). Absolute paths start at `/` (same).
- `bash-deny-rm-rf-root` Mac patterns target `~/`, `$HOME`, `/Users/`. Jetson equivalents add `/home/`, `/root/` and drop `/Users/`.
- Rules using regex match GNU `grep -E` extended regex semantics (verify any pattern that worked under Mac BSD `grep`).

Examples ported from Mac patterns:

- `bash-deny-rm-outside-cwd.md`: same pattern, Linux verification.
- `bash-deny-curl-without-allowlist.md`: same pattern, Linux verification.
- `filesystem-deny-write-secrets-dir.md`: same pattern, Linux verification.
- `mcp-deny-server-prefix-default.md`: same pattern, no platform delta.

### settings.json fill

Update `jetson/harness/settings.json` (not the template) with the populated values. Same structure as Mac but with the Jetson-specific paths and the ARM64 Linux Claude Code version pin from Phase 0.

The MCP server allowlist stays empty. Phase 4 populates.

### Deep-evaluate security-tool seeds

Phase 1 surveyed and pre-filtered. Phase 3 deep-evaluates survivors that touch the deterministic layer, with the Jetson-specific architecture-validation check added per `jetson/evaluations/deep-eval.md` format.

### Anti-overengineering block

Hooks and rules address Phase 2 elected threats. Do not add hooks for threats Phase 2 did not elect. Record new threats surfaced in Phase 3 in `PHASE-3-NOTES.md` for Phase 2 to revisit.

Do not create new abstractions or helper libraries. Hook script is self-contained: header, logic, schema-correct return. If two hooks share logic, duplication is acceptable.

Do not write test scaffolding beyond what the rule and hook headers prescribe.

Do not edit `jetson/harness/CLAUDE.md`. Phase 5.

<investigate_before_answering>
Before writing a hook that returns a specific Zod schema field, read `research/Claude_Architecture.md` §5.3 and §6.

Before claiming a deny rule pattern matches a specific behavior, write the rule and exercise it against a test input on Linux.

Before recording that a security tool integrates cleanly on Jetson, run the tool against known-vulnerable and known-clean fixtures.

Marker resolution: for each ported Mac pattern, run the equivalent on Jetson and confirm behavior matches. Mac Phase 3 validated all 15 hook+rule test cases first run (per `phase-outputs/PHASE-3-NOTES.md`); ARM64 Linux baselines its own equivalent set. The validation outcome lands in the hook or rule header.
</investigate_before_answering>

## Deliverables

- Hook scripts in `jetson/harness/hooks/`, one per Phase-2-elected threat, each with Jetson port validation outcome in header.
- Deny rule files in `jetson/harness/rules/`, one per blanket-deny pattern.
- Populated `jetson/harness/settings.json` with all Phase 3 fields filled; MCP allowlist deferred to Phase 4.
- Updated `jetson/evaluations/deep-eval.md` with security-tool integration outcomes (including ARM64 Linux validation).
- `phase-outputs/PHASE-3-NOTES.md` with rationale.
- `phase-outputs/PHASE-3-CONTEXT.md`.

## Verification

Before reporting complete:

- `find jetson/harness/hooks -name '*.sh' -exec shellcheck {} +` clean.
- `python3 -c "import json; json.load(open('jetson/harness/settings.json'))"` parses.
- For each hook, run its header verification command and confirm expected return.
- `bash scripts/drift-check.sh` returns 0.
- `wc -l jetson/harness/hooks/* jetson/harness/rules/* jetson/harness/settings.json` reports counts.

Report hook count, deny rule count, line counts, validation outcomes.

## Anti-overengineering reminder

The trap is starting to feel productive by writing more hooks than Phase 2 elected. Resist. Every additional hook is additional surface. The foundation principle: hooks enforce what must hold every time.

When in doubt about hook vs deny rule, prefer deny rule. Simpler to audit, faster to evaluate. Hooks reserved for cases deny rules cannot express.
