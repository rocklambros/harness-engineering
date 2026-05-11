# Deep-evaluation worksheet (Mac)

Records the integration outcomes for pre-filter survivors. The methodology is in `foundation/03-seed-evaluation-methodology.md`. This file is the operational log for the Mac build.

Deep evaluation is integration, not scoring. Each survivor gets wired into a sandboxed harness session and exercised against three workloads. The output of the deep eval is a paragraph per candidate, not a rubric.

## The three exercises per candidate

1. **Nominal task**: A task the candidate is supposed to do well. Measures expected-case quality.
2. **Edge case**: A task that exercises the failure mode the threat model worries about. Measures resilience.
3. **No-op interaction**: The cost of having the candidate installed and idle. Measures cache footprint, startup latency, tool pool inflation, and mental complexity.

## Format per candidate

```
### <candidate>

Stage 2 entry: Phase <3 or 4>
Date evaluated: <YYYY-MM-DD>
Decision: integrate / integrate-with-constraints / reject

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

Phase 3 and Phase 4 populate this file with real evaluations. Each evaluation follows the format above. Templates below give the shape Phase 3 and Phase 4 fill against.

### Example template for a security tool

```
### <security-tool-name>

Stage 2 entry: Phase 3
Date evaluated: <YYYY-MM-DD>
Decision: integrate-with-constraints

Nominal task: Ran <tool> against a known-vulnerable test fixture (intentional SAST trigger).
The tool flagged the expected finding and produced output in <format> that the
PostToolUse hook can route into the pre-commit pipeline.

Edge case: Ran <tool> against a file that previous versions falsely flagged.
The current version handles the case correctly.

No-op cost: Startup adds ~<X>ms to PreToolUse latency on Bash invocations.
Cache footprint negligible. No additional tool slot consumed because the tool
runs inside the hook, not as a SkillTool.

Constraints:
- Hook script PreToolUse-<tool>-scan.sh enforces a 30-second timeout
- Tool runs only on file extensions matching <pattern>
- Findings above severity <threshold> block the commit; lower findings warn

Rationale: <Tool> closes the QC.1 PW.5.1 gap that the existing pre-commit
secret-scan does not cover. Alternatives <X> and <Y> were rejected because
<reason>.

Drift trigger: Security advisory, or major release
Version pin: <X.Y.Z>
```

### Example template for a skill or configuration seed

```
### <seed-repo-name>

Stage 2 entry: Phase 4
Date evaluated: <YYYY-MM-DD>
Decision: <integrate | integrate-with-constraints | reject>

Nominal task: <what the seed claims to do, and whether it did it>
Edge case: <what happens when the seed encounters the failure mode the
threat model worries about>
No-op cost: <cache prefix impact, tool pool impact, instruction-following
degradation per HumanLayer's analysis if applicable>

Constraints (if applicable):
- <constraint>

Rationale: <what the seed gives that nothing else gave, and why the
constraints are sufficient>

Drift trigger: <trigger>
Version pin: <pin>
```

## Rejected after deep eval

Candidates that survive pre-filter but fail deep eval land here with a paragraph naming the specific failure mode. The list serves two purposes: it prevents re-evaluation of the same candidate without new information, and it documents what failure modes the methodology actually catches.

Phase 5 reviews this section against the rejected-at-pre-filter list to look for patterns. Repeated failure modes across multiple candidates may indicate a structural issue with how the harness presents the integration surface.

## Notes on the methodology

The integration test is the evidence. The README, the star count, the vendor pitch, and the rubric score are not.

A candidate that performs well on the nominal task but fails the edge case is rejected or integrated with constraints that prevent the failure mode. A candidate that performs well on both but carries a high no-op cost (large cache prefix injection, instruction-following degradation, tool slot inflation) is integrated with a documented opportunity cost that gets revisited on the next QC.5 trigger.

The decision is binary at the integration level (integrate / integrate-with-constraints / reject) but the rationale captures the gradient. Phase 5's Reviewer subagent audits each decision against the rationale and the threat model.
