# Phase 3 — Deterministic Layer

<role>
You are writing the deterministic enforcement layer of the Mac harness: the hook scripts, the deny rules, the sandbox configuration, and the permission-mode posture in `mac/harness/settings.json`. Every threat Phase 2 elected to enforce in hooks lands here. Every constraint that must hold every time the harness runs lands here.

This is the single most consequential phase for harness security. The model has no veto over a hook. Hooks fire regardless of context, prompt design, or conversation length. That property is what the harness buys; Phase 3 is where the property gets cashed in.
</role>

<effort>xhigh</effort>

<mode>default mode (writes). Phase 3 produces hook scripts, deny rule files, and the settings.json fill.</mode>

<thinking>adaptive</thinking>

<context_budget>Run /context at start and end. Phase 3 reads several foundation documents, Phase 2 outputs, and `Claude_Architecture.md` for hook-event specifics. The writes are focused but each hook script and deny rule file carries a header that references the documentation. Record start, end, and delta in `phase-outputs/PHASE-3-CONTEXT.md`.</context_budget>

<parallel_tool_calls>
Read the inputs in parallel at the start: `phase-outputs/ANSWERS.md`, `phase-outputs/INVENTORY.md`, `mac/ARCHITECTURE.md`, `mac/harness/settings.json.template`, `mac/harness/rules/README.md`, `mac/harness/hooks/README.md`, `foundation/01-threat-model.md`, `foundation/02-architectural-principles.md`, and the relevant sections of `research/Claude_Architecture.md` (§5 permission system, §6 hooks). These are independent.
</parallel_tool_calls>

<scope>
Apply only to:
- `mac/harness/hooks/` (writes: one shell or Python script per hook, with header block)
- `mac/harness/rules/` (writes: one markdown file per rule, recording the deny pattern, the threat, the citation, and the test)
- `mac/harness/settings.json` (writes: the populated settings file, with all Phase 3 fields filled. The template stays unchanged.)
- `mac/evaluations/deep-eval.md` (updates: integration results for security-tool seeds evaluated in this phase)
- `phase-outputs/PHASE-3-CONTEXT.md` (writes)
- `phase-outputs/PHASE-3-NOTES.md` (writes: rationale paragraphs per hook and deny rule)

Do not modify `foundation/`, `research/`, `mac/prompts/`, `mac/harness/CLAUDE.md`, `mac/harness/skills/`, `mac/harness/agents/`, `mac/ARCHITECTURE.md`, or `mac/README.md`. Skills and agents are Phase 4. The polished architecture and README are Phase 5.
</scope>

## What to do

Phase 3 produces three kinds of artifacts: hook scripts, deny rule files, and the populated `settings.json`. The order is: write the deny rules and hook scripts, then wire them into `settings.json`, then deep-evaluate the security-tool seeds.

### Hook scripts

For each threat Phase 2 elected to enforce in a hook, write a hook script in `mac/harness/hooks/`. The naming convention is in `mac/harness/hooks/README.md`. Each script:

- Carries a header block (purpose, threat addressed, foundation citation, verification test).
- Is shellcheck-clean for shell scripts. SAST-clean for Python.
- Returns the correct Zod-validated output schema for the hook event it registers to (see Claude_Architecture.md §5.3 and §6 for the schemas).
- Sets `permissionDecision` to `deny` or `ask` when blocking; never to `allow` to bypass subsequent checks. A hook `allow` does not bypass rule-based denies (Claude_Architecture.md §5.3).
- Returns within a reasonable timeout. UI freezes from slow hooks are the root cause of the 50-subcommand bypass class.

Mandatory hooks (drawn from `foundation/01-threat-model.md` threats that hooks must enforce):

- **PreToolUse subcommand cap**: rejects Bash chains over 50 subcommands. Defends against the Adversa.ai 2026 bypass class.
- **PreToolUse external write gate**: requires explicit confirmation for writes outside the working directory. Defends against reversibility-class threats per Principle 3.
- **SessionStart pre-trust audit**: refuses to load a project whose `.claude/settings.json` or `.mcp.json` was modified after the last recorded audit. Defends against CVE-2025-59536 class. Cadence per Phase 2's answer.
- **PreToolUse MCP server allowlist enforcement**: rejects MCP tool calls whose server is not on the explicit allowlist in `settings.json`. Defends against compromised-or-hostile MCP server class.

Optional hooks the Phase 2 interview may have elected:

- **PreCompact decision preserver**: writes consequential decisions to a sticky note so compaction does not lose them.
- **UserPromptSubmit prompt injection scanner**: flags prompts that contain instructions purporting to come from system sources.
- **PostToolUse output classifier**: scans tool returns for embedded instructions before they enter the context.

### Deny rules

For each blanket-deny pattern Phase 2 elected, write a file in `mac/harness/rules/`. Each rule file:

- Carries the pattern in the form Claude Code's `permissions.deny` accepts (per Claude_Architecture.md §5.2 `toolMatchesRule()`).
- Documents the threat or QC property the rule addresses.
- Includes the test that verifies the rule fires when expected and does not fire when not expected.

Examples drawn from the foundation documents:

- `bash-deny-rm-outside-cwd.md`: pattern `Bash(prefix:rm)` constrained to paths outside the working directory.
- `bash-deny-curl-without-allowlist.md`: pattern `Bash(prefix:curl)` constrained to non-allowlisted URLs.
- `filesystem-deny-write-secrets-dir.md`: pattern denying writes to `.secrets/`, `secrets/`, and similar.
- `mcp-deny-server-prefix-default.md`: server-prefix denies for any MCP server not on the allowlist.

### settings.json fill

Update `mac/harness/settings.json` (not the template) with:

- The populated `permissions.deny` array from `mac/harness/rules/` filenames.
- The populated `hooks.<event>` blocks pointing at `mac/harness/hooks/` scripts.
- The Phase 0 and Phase 2 decisions for default mode, default model, subagent default, sandbox config.
- The `additionalDirectories` from Phase 0.

The MCP server allowlist (`mcpServers`) stays empty here. Phase 4 populates it.

### Deep-evaluate security-tool seeds

Phase 1 surveyed and pre-filtered. Phase 3 deep-evaluates the survivors that touch the deterministic layer: SAST tools, secret scanners, SBOM generators, vulnerability scanners. For each survivor, run the three exercises from `foundation/03-seed-evaluation-methodology.md` (nominal task, edge case, no-op cost) and record the outcome in `mac/evaluations/deep-eval.md` using the worksheet format.

### Anti-overengineering block

The hook scripts and deny rules address the threats Phase 2 elected. They do not address threats Phase 2 deferred or accepted as residual risk. Do not add hooks for threats Phase 2 did not elect; record any new threats surfaced during Phase 3 in `phase-outputs/PHASE-3-NOTES.md` for Phase 2 to revisit in a later revision.

Do not create new abstractions or helper libraries. A hook script is a self-contained file with a header, the logic, and the schema-correct return. If two hooks share logic, the duplication is acceptable; pulling shared logic into a third file creates a maintenance vector that the harness does not need.

Do not write test scaffolding beyond what the rule and hook headers prescribe (one positive test and one negative test per rule, one verification command per hook). A full test framework is out of scope.

Do not edit `mac/harness/CLAUDE.md`. The advisory layer is Phase 5's deliverable.

<investigate_before_answering>
Before writing a hook that returns a specific Zod schema field, read the relevant section of `research/Claude_Architecture.md` (§5.3 and §6) and confirm the field name and type. The architecture document records the exact schemas.

Before claiming a deny rule pattern matches a specific behavior, write the rule and exercise it against a test input. Do not claim a regex matches without testing.

Before recording that a security tool integrates cleanly, run the tool against a known-vulnerable test fixture and a known-clean fixture. Both outcomes must match expectations.
</investigate_before_answering>

## Deliverables

- Hook scripts in `mac/harness/hooks/`, one per Phase-2-elected threat.
- Deny rule files in `mac/harness/rules/`, one per blanket-deny pattern.
- Populated `mac/harness/settings.json` with all Phase 3 fields filled, MCP allowlist deferred to Phase 4.
- Updated `mac/evaluations/deep-eval.md` with security-tool integration outcomes.
- `phase-outputs/PHASE-3-NOTES.md` with rationale per hook and per rule, plus any deferred threats.
- `phase-outputs/PHASE-3-CONTEXT.md` with the context-budget record.

## Verification

Before reporting complete:

- `find mac/harness/hooks -name '*.sh' -exec shellcheck {} +` returns clean.
- `python3 -c "import json; json.load(open('mac/harness/settings.json'))"` parses the settings file.
- For each hook, run the verification command in the hook's header and confirm the expected return. Record any divergence in `PHASE-3-NOTES.md`.
- `bash scripts/drift-check.sh` returns 0.
- `wc -l mac/harness/hooks/* mac/harness/rules/* mac/harness/settings.json` reports the line counts.

Report the artifact paths, hook count, deny rule count, and the line counts. Surface any verification divergence as a flag.

## Anti-overengineering reminder

This phase produces a lot of files. The trap is starting to feel productive by writing more hooks than Phase 2 elected. Resist. Every additional hook is additional surface to maintain, and the foundation principle is that hooks enforce *what must hold every time*. If a property does not need to hold every time, it does not get a hook.

When in doubt about whether a Phase 2 answer implies a hook or a deny rule, prefer the deny rule. Deny rules are simpler to audit and faster to evaluate. Hooks are reserved for cases where deny rules cannot express the constraint.
