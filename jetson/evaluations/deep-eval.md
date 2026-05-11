# Deep-evaluation worksheet (Jetson)

Records the integration outcomes for pre-filter survivors on Jetson AGX Orin. The methodology is in `foundation/03-seed-evaluation-methodology.md`. This file is the operational log for the Jetson build.

Deep evaluation is integration, not scoring. Each survivor gets wired into a sandboxed harness session on Jetson and exercised against three workloads. The output is a paragraph per candidate, not a rubric.

## The three exercises per candidate

1. **Nominal task**: A task the candidate is supposed to do well. Measures expected-case quality on ARM64 Linux.
2. **Edge case**: A task that exercises the failure mode the threat model worries about. Measures resilience.
3. **No-op interaction**: The cost of having the candidate installed and idle. Cache footprint, startup latency, tool pool inflation, mental complexity.

## Jetson-specific check per candidate

In addition to the three exercises, every deep-eval on Jetson records:

- **ARM64 Linux validation**: confirm the candidate's behavior on ARM64 Linux matches the documented or Mac-validated behavior. Specific to check: byte-order assumptions in any binary serialization, NUMA topology assumptions, GPU library version assumptions, glibc vs musl assumptions.

## Format per candidate

```
### <candidate>

Stage 2 entry: Phase <3 or 4>
Date evaluated: <YYYY-MM-DD>
Decision: integrate / integrate-with-constraints / reject

ARM64 Linux validation: <one paragraph confirming behavior matches expectations; or
documenting the delta from Mac if behavior differs>

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

ARM64 Linux validation: Installed via <method: apt | direct download | pip>. Version
<X.Y.Z>. Behavior on test fixtures matches Mac at version <X.Y.Z>. No glibc
incompatibility observed.

Nominal task: Ran <tool> against a known-vulnerable test fixture (intentional SAST
trigger). Flagged the expected finding. Output format matches Mac.

Edge case: Ran <tool> against the file class Mac Phase 3 falsely flagged. Current
version handles the case correctly.

No-op cost: Startup adds ~<X>ms to PreToolUse latency on Bash invocations. Cache
footprint negligible. No additional tool slot consumed.

Constraints:
- Hook script PreToolUse-<tool>-scan.sh enforces a 30-second timeout
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

ARM64 Linux validation: <whether the seed's executable bodies run on ARM64 Linux,
whether dependencies have ARM64 builds, whether any shell scripts use BSD-specific
flags that need adaptation>

Nominal task: <what the seed claims to do, and whether it did it on Jetson>
Edge case: <what happens when the seed encounters the failure mode the threat model
worries about>
No-op cost: <cache prefix impact, tool pool impact, instruction-following degradation
per HumanLayer's analysis if applicable>

Constraints (if applicable):
- <constraint>

Rationale: <what the seed gives that nothing else gave, and why the constraints are
sufficient>

Drift trigger: <trigger>
Version pin: <pin>
```

## Rejected after deep eval

Candidates that survive pre-filter but fail deep eval land here with a paragraph naming the specific failure mode. Jetson-specific failure modes to watch for:

- GNU vs BSD coreutils incompatibility in shipped shell scripts
- ARM64 Linux build present but with reduced feature set vs x86
- Network egress assumptions baked into the candidate that conflict with `opensnitch` or similar
- CUDA version assumptions that conflict with the installed JetPack base

Phase 5 reviews this section against the rejected-at-pre-filter list to look for patterns.

## Notes on the methodology

The integration test is the evidence. README, star count, vendor pitch, rubric score: none of those count.

A candidate that performs well on the nominal task but fails the edge case is rejected or integrated with constraints. A candidate that performs well on both but carries a high no-op cost is integrated with a documented opportunity cost that gets revisited on the next QC.5 trigger.

The decision is binary at the integration level (integrate / integrate-with-constraints / reject) but the rationale captures the gradient. Phase 5's Reviewer subagent audits each decision against the rationale and the threat model.
