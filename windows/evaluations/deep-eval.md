# Deep-evaluation worksheet (Windows)

Records the integration outcomes for pre-filter survivors on Windows 11 x86_64. The methodology is in `foundation/03-seed-evaluation-methodology.md`. This file is the operational log for the Windows build.

Deep evaluation is integration, not scoring. Each survivor gets wired into a sandboxed harness session on Windows and exercised against three workloads. The output is a paragraph per candidate, not a rubric.

## The three exercises per candidate

1. **Nominal task**: A task the candidate is supposed to do well. Measures expected-case quality on Windows.
2. **Edge case**: A task that exercises the failure mode the threat model worries about. Measures resilience.
3. **No-op interaction**: The cost of having the candidate installed and idle. Cache footprint, startup latency, tool pool inflation, mental complexity.

## Windows-specific checks per candidate

In addition to the three exercises, every deep-eval on Windows records:

- **Native or WSL2 routing**: which execution context the candidate runs in. Native preferred; WSL2 routing is acceptable with documented rationale.
- **Path convention used**: forward slash, backslash, or canonicalized at boundary. Recorded for cross-platform-debugging clarity.
- **PowerShell version requirement**: 5.1, 7+, or version-agnostic.
- **Execution policy requirement**: `RemoteSigned` minimum; any candidate that requires `Bypass` is rejected.
- **Line ending tolerance**: tolerates CRLF, tolerates LF, requires one specifically.

## Format per candidate

```
### <candidate>

Stage 2 entry: Phase <3 or 4>
Date evaluated: <YYYY-MM-DD>
Decision: integrate / integrate-with-constraints / reject

Windows-specific validation:
- Execution context: native PowerShell / WSL2 bash / Python / Node / cmd
- Path convention: forward-slash / backslash / canonicalized
- PowerShell version: 5.1-compatible / 7+ / n/a
- Execution policy: RemoteSigned acceptable / requires custom
- Line ending tolerance: CRLF / LF / either

Nominal task: <one paragraph on what worked>
Edge case: <one paragraph on what broke or held>
No-op cost: <one paragraph on what it costs to keep idle>

Constraints (if integrate-with-constraints):
- <constraint 1, with the hook or deny rule that enforces it>
- <constraint 2>

Rationale: <one paragraph naming the failure mode this prevents and the alternatives rejected>

Drift trigger: <upstream major version | security advisory | periodic review date>
Version pin: <semver>
```

## Worked examples

Phase 3 and Phase 4 populate this file with real evaluations. Templates below give the shape Phase 3 and Phase 4 fill against.

### Example template for a security tool

```
### <security-tool-name>

Stage 2 entry: Phase 3
Date evaluated: <YYYY-MM-DD>
Decision: integrate-with-constraints

Windows-specific validation:
- Execution context: native (Windows x86_64 binary from upstream releases)
- Path convention: forward slash (tool accepts both)
- PowerShell version: 7+ for invocation; 5.1 untested
- Execution policy: RemoteSigned acceptable
- Line ending tolerance: either

Nominal task: Ran <tool> against a known-vulnerable test fixture. Flagged the expected
finding. Output format matches Mac and Jetson.

Edge case: Ran <tool> against the file class that previous versions falsely flagged.
Current version handles correctly.

No-op cost: Startup adds ~<X>ms to PreToolUse latency on Bash invocations on Windows.
Cache footprint negligible. No additional tool slot consumed.

Constraints:
- Hook script PreToolUse-<tool>-scan.ps1 enforces a 30-second timeout
- Tool runs only on file extensions matching <pattern>
- Findings above severity <threshold> block the commit; lower findings warn

Rationale: Closes the QC.1 PW.5.1 gap not covered by existing pre-commit secret-scan.
Alternatives <X> and <Y> rejected because <reason>.

Drift trigger: Security advisory, or major release
Version pin: <X.Y.Z>
```

### Example template for a skill or configuration seed

```
### <seed-repo-name>

Stage 2 entry: Phase 4
Date evaluated: <YYYY-MM-DD>
Decision: <integrate | integrate-with-constraints | reject>

Windows-specific validation:
- Execution context: <choice>
- Path convention: <choice>
- PowerShell version: <choice>
- Execution policy: <choice>
- Line ending tolerance: <choice>

Nominal task: <what the seed claims to do, and whether it did it on Windows>
Edge case: <what happens when the seed encounters the failure mode>
No-op cost: <cache prefix impact, tool pool impact, instruction-following degradation>

Constraints (if applicable):
- <constraint>

Rationale: <what the seed gives that nothing else gave, and why the constraints are
sufficient>

Drift trigger: <trigger>
Version pin: <pin>
```

## Rejected after deep eval

Candidates that survive pre-filter but fail deep eval land here with a paragraph naming the specific failure mode. Windows-specific failure modes to watch for:

- POSIX-only system calls without acceptable Windows fallback
- Native modules that fail to build under MSVC or MinGW
- File-locking semantics that conflict with Windows-style locking
- Path-length limits hit during normal operation (260-character MAX_PATH on default Windows)
- Line-ending assumptions that break when CRLF or LF arrives unexpectedly
- WSL2 routing latency exceeding the PreToolUse budget

Phase 5 reviews this section against the rejected-at-pre-filter list to look for patterns.

## Notes on the methodology

The integration test is the evidence. README, star count, vendor pitch, rubric score: none of those count.

A candidate that performs well on the nominal task but fails the edge case is rejected or integrated with constraints. A candidate that performs well on both but carries a high no-op cost is integrated with a documented opportunity cost that gets revisited on the next QC.5 trigger.

The decision is binary at the integration level (integrate / integrate-with-constraints / reject) but the rationale captures the gradient. Phase 5's Reviewer subagent audits each decision against the rationale and the threat model.
