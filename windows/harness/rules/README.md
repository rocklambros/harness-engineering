# rules/ (Windows)

Static permission rules for Claude Code on Windows. Each rule is a deny pattern or allow pattern that the Claude Code permission system evaluates at tool-pool assembly time and at every tool invocation.

Rules live here so Phase 3 (deterministic layer) can write them as small, focused files with rationale comments, then wire them into `windows/harness/settings.json`.

## Naming convention

`<scope>-<verb>.md` per rule. Same convention as Mac and Jetson. Examples: `powershell-deny.md`, `filesystem-write-outside-cwd.md`, `mcp-server-allowlist.md`.

Each file holds the rule pattern, the threat or policy it addresses, the citation in `foundation/01-threat-model.md` or `foundation/02-architectural-principles.md`, and the test that verifies the rule fires.

## Security posture

Deny-first. A broad deny beats a narrow allow per Claude_Architecture.md §5.2. Server-prefix patterns strip whole tool families from the model's view before invocation.

Rules are deterministic. Same property as Mac and Jetson. The platform delta is path conventions in the patterns: Windows accepts forward slash in most modern tools, requires backslash for some PowerShell-native cmdlets and registry calls. Each Windows rule file records which convention it uses and why.

## Phase coverage

Phase 3 populates this directory. `<NEEDS-WINDOWS-PORT-VALIDATION>`: rule patterns ported from Mac Phase 3 are verified to express the same constraint on Windows before adoption. Phase 5 audits each rule against the threat model and the Quality Contract through the Writer/Reviewer subagent pattern.
