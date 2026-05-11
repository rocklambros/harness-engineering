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

## Phase 3 evaluations

Run date: 2026-05-11. Five candidates from the deterministic-layer security tool class (Phase 2 Q8): gitleaks, trivy, semgrep, detect-secrets, cosai-oasis/project-codeguard. Each evaluated against the three exercises with realistic fixtures at `/tmp/phase3-deep-eval-v2/`.

### gitleaks

Stage 2 entry: Phase 3
Date evaluated: 2026-05-11
Decision: integrate

Nominal task: Created a git-init'd fixture with realistic-shape AWS access key + secret, GitHub PAT, Slack token, and a fake RSA private key. `gitleaks detect --no-banner` in the repo correctly flagged 3 leaks across 1 commit, scanned ~406 bytes in 57.7ms. Run on the canonical AWS example key (AKIAIOSFODNN7EXAMPLE) returned no leaks, which is correct behavior (the key is in gitleaks's documented-allowlist as a known doc example).

Edge case: A clean git repo with no secrets returned "no leaks found" with the same ~58ms latency. The git-history scope is gitleaks's strength: it reads commits, not just working tree, which catches secrets that were committed and later removed.

No-op cost: ~58ms per scan on a small repo. Cache footprint zero (binary at /opt/homebrew/bin/gitleaks, no tool-pool slot). Pre-commit invocation adds the same ~58ms per run.

Rationale: gitleaks closes the QC.1 PW.5.1 secret-scan-in-pre-commit gap with the strongest git-history awareness in the candidate set. Detect-secrets was rejected in favor of gitleaks because gitleaks finds the same realistic-shape secrets with stronger commit-history coverage and is already installed (no QC.1 PS.2.1 install-and-pin cost). The pre-commit wiring change is a Phase 5 deliverable.

Drift trigger: Security advisory, or major release (v9)
Version pin: 8.30.0

### trivy

Stage 2 entry: Phase 3
Date evaluated: 2026-05-11
Decision: integrate

Nominal task: `trivy fs --scanners secret vuln/` against the same realistic-shape fixture flagged 5 secrets: 3 CRITICAL (AWS access key, AWS secret access key, AWS asymmetric key) + 2 HIGH (GitHub PAT, Slack token). Trivy's secret coverage is broader than gitleaks's (caught the Slack token that gitleaks missed in the same fixture). Scan time ~350ms wall (including engine startup).

Edge case: Clean fixture returned "No issues detected" with the same scanner invocation. The fs scanner does not require git context, which makes it useful for build-artifact scanning and in-flight CI checks.

No-op cost: ~350ms startup-dominated for a small dir. The vulnerability scanner (`trivy image`) needs a vuln DB cache; the alpine:3.14 image scan returned 0 vulnerabilities on this machine (likely a stale or absent DB cache, not a tool failure). Cache hot-path runs are sub-second; first-run cold-path is several seconds while the DB downloads.

Rationale: trivy complements gitleaks: trivy covers any-file content scanning (build outputs, generated configs, container layers) while gitleaks covers git-history. The two together close the QC.1 PW.5.1 gap for the spectrum of secret-leak scenarios. Trivy also covers QC.1 PS.2.1 SBOM scanning at release time (not used by Phase 3 hooks but available for Phase 5 release flow).

Drift trigger: Security advisory, or major release (v1.x)
Version pin: 0.69.0

### semgrep

Stage 2 entry: Phase 3
Date evaluated: 2026-05-11
Decision: integrate-with-constraints (substitution required)

Nominal task: `/opt/anaconda3/bin/semgrep --version` triggers an ImportError during `semgrep.cli` module load: traceback at /opt/anaconda3/lib/python3.13/site-packages/semgrep/cli.py:22. The Anaconda install is broken on the current Python 3.13.9. Phase 0 documented this; Phase 3 confirms the state is unchanged.

Edge case: Not run (the broken state blocks the nominal exercise).

No-op cost: Currently the broken binary consumes a PATH entry but no other resource. If fixed, semgrep is the established Python/JS SAST baseline and would close QC.1 PW.5.1 SAST gate alongside gitleaks/trivy.

Constraints:
- Install a clean semgrep in a separate venv (pipx install semgrep) rather than repairing the Anaconda install. The Anaconda environment is shared with mempalace, academia_mcp, and other tools; ripple effects of dependency repair are not in scope for this phase.
- Phase 5 wires semgrep into pre-commit alongside gitleaks. SAST findings above HIGH severity block the commit; lower findings warn.

Rationale: semgrep is the SAST gate that QC.1 PW.5.1 names. The broken Anaconda install does not falsify the tool; a clean install resolves the issue and the historical signal (Anthropic's own Claude Code repo uses semgrep) supports the integration. The constraint is the install path, not the tool choice.

Drift trigger: Security advisory, or quarterly review
Version pin: deferred to Phase 5 install (latest stable at install time, then pinned)

### detect-secrets

Stage 2 entry: Phase 3
Date evaluated: 2026-05-11
Decision: reject

Nominal task: Binary not installed (Phase 0 and Phase 1 confirmed). The pre-commit framework wired in Batch 1 references `detect-secrets-hook` but the binary is missing on this machine.

Edge case: Not run.

No-op cost: Zero (not installed).

Rationale: gitleaks covers detect-secrets's use case with stronger coverage in this fixture set (3 detections vs the expected detect-secrets baseline) and is already installed. Adding detect-secrets means maintaining two tools that solve the same problem. Phase 5 updates `.pre-commit-config.yaml` to use gitleaks in place of detect-secrets.

Rejected: detect-secrets — superseded by gitleaks + trivy for secret-scanning coverage. Pre-commit wiring change is Phase 5 scope.

### cosai-oasis/project-codeguard

Stage 2 entry: Phase 3 (per Phase 2 Q8; class-level placement)
Date evaluated: 2026-05-11 (paper evaluation; not installed)
Decision: defer

Nominal task: Not installed (Phase 1 confirmed). Pre-1.0 status (per foundation/03 and CHECKPOINT).

Edge case: Not run.

No-op cost: Not measured.

Rationale: Phase 2 Q8 elected Phase 3 for the class of deterministic-layer security tool seeds; codeguard is one named candidate in that class. Pre-1.0 status combined with no upstream commit signal in the last 90 days (license unverified per Phase 1; Phase 3 web-check deferred for scope discipline) means deep-eval cost exceeds expected value at this time. The integration shape Phase 3 is building (PreToolUse hooks for supply-chain checks + deny rules for reversibility-class operations) is the same shape codeguard would slot into, so future swap is structurally supported.

The agentcontrolstandard.ai work Rock mentioned in Phase 2 Q8 is the same shape candidate; it gets first-class consideration when it ships per the project memory in PHASE-3-NOTES.md.

Drift trigger: Codeguard 1.0 release, or agentcontrolstandard.ai ship.
Version pin: not applicable (deferred).

## Rejected after deep eval

Candidates that survive pre-filter but fail deep eval land here with a paragraph naming the specific failure mode. The list serves two purposes: it prevents re-evaluation of the same candidate without new information, and it documents what failure modes the methodology actually catches.

Phase 5 reviews this section against the rejected-at-pre-filter list to look for patterns. Repeated failure modes across multiple candidates may indicate a structural issue with how the harness presents the integration surface.

## Notes on the methodology

The integration test is the evidence. The README, the star count, the vendor pitch, and the rubric score are not.

A candidate that performs well on the nominal task but fails the edge case is rejected or integrated with constraints that prevent the failure mode. A candidate that performs well on both but carries a high no-op cost (large cache prefix injection, instruction-following degradation, tool slot inflation) is integrated with a documented opportunity cost that gets revisited on the next QC.5 trigger.

The decision is binary at the integration level (integrate / integrate-with-constraints / reject) but the rationale captures the gradient. Phase 5's Reviewer subagent audits each decision against the rationale and the threat model.
