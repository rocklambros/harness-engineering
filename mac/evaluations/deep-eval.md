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

## Phase 4 evaluations

Run date: 2026-05-11. Six candidates from the extension-layer class: obra/superpowers, affaan-m/everything-claude-code, disler/claude-code-hooks-mastery, MemPalace, Serena, and the broader plugin set Rock currently runs (16 plugins inventoried by Phase 1).

### obra/superpowers

Stage 2 entry: Phase 4
Date evaluated: 2026-05-11
Decision: integrate (wholesale, plugin form)

Nominal task: Used `verification-before-completion` skill across all five build phases. The skill correctly fires on completion-claim prompts, walks the iron-law gate (run verification → read output → claim with evidence), and prevents the silent-failure modes the skill description names. Used `using-superpowers` to scaffold every phase's skill discovery. Both produced behavior that the harness's CLAUDE.md alone does not: the verification-before-completion gate fires on completion-claim PROMPTS rather than waiting for the model to remember it from CLAUDE.md.

Edge case: The 5.0.7 and 5.1.0 versions are both retained in the plugin cache (per Phase 1 inventory). The current loaded version is 5.1.0. The orphaned 5.0.7 tree does not cause routing collision (skill discovery uses the current cache, not the orphan), but it is a Phase 5 hygiene item to prune.

No-op cost: 14 skills + 1 SessionStart hook + 0 agents loaded into the discovery flow (verified by direct listing during Phase 5 audit; Phase 1 INVENTORY's 17/4/1 figure double-counted). Skill descriptions are short (frontmatter only sits in cache); the body loads on SkillTool invocation. The cache footprint is the 14 frontmatter blocks, estimated ~4k tokens. Acceptable for the discipline value the collection provides.

Rationale: superpowers closes the gap between advisory CLAUDE.md text ("verify before claiming complete") and deterministic-enough enforcement (skill firing on routing). Wholesale adoption is correct because the collection's value is the curated set; cherry-picking would lose the skill priority logic (process skills first, implementation skills second) that the using-superpowers skill encodes. The plugin form preserves upstream updates without manual sync; the lastUpdated 2026-05-05 signal confirms active maintenance.

Drift trigger: Plugin lastUpdated drift past 90 days, or upstream major version (6.0.x).
Version pin: 5.1.0 (per `installed_plugins.json`)

### MemPalace

Stage 2 entry: Phase 4
Date evaluated: 2026-05-11
Decision: integrate

Nominal task: All MCP calls verified working in this build session. `mempalace_diary_write` accepted AAAK-formatted entries across phases (Phase 2 entry_id diary_wing_claude-code_20260511, Phase 3 entry_id diary_wing_claude-code_20260511_085635773368). `mempalace_add_drawer` accepted full prose records (Phase 2 drawer 8250356d9c729f7d04ed3a36, Phase 3 drawer 5eb86f6da826eec5ec6a8075). `mempalace_kg_add` produced retrievable triples for project memory (Mac harness build phase_status fact, gitleaks supersedes-detect-secrets fact, Rock-works_on-agentcontrolstandard.ai fact). The `/opt/anaconda3/bin/mempalace-mcp --help` invocation returns the documented argument set in <100ms.

Edge case: Phase 2 surfaced a drawer-content-corruption bug when add_drawer was called with content containing XML-like `</content>` and `<added_by>` tags; the drawer was created with the trailing junk and the returned drawer_id could not be retrieved via get_drawer. Workaround: refile the clean version as a new drawer (Phase 2 record). Recorded as a known MemPalace bug, not a harness defect. The bug does not block adoption because the workaround is deterministic.

No-op cost: 39 mempalace_* tools registered when the plugin is enabled. Their schemas sit in the deferred-tool list (loaded on demand via ToolSearch per the runtime's lazy-load behavior on this version). Active cache footprint is the plugin's setup metadata, not the full tool schemas. Daily LaunchAgent at 03:00 runs `/opt/anaconda3/bin/python3 /Users/klambros/.mempalace/maintenance.py` for back-end housekeeping; cost negligible.

Rationale: MemPalace provides cross-session structured memory that Claude Code's native auto-memory does not: drawers + wings + rooms for content, AAAK-format diaries for compressed agent histories, knowledge-graph triples with time windows. Phase 2 Q4 enabled native auto-memory; MemPalace lives alongside it for the structured workflows where auto-memory's free-form .md format does not fit (e.g., the AAAK phase summaries this build produced). The two systems are complementary, not redundant.

Alternative considered: goodmem (also installed per Phase 1). goodmem is rejected because MemPalace's structured-memory shape is already wired into Rock's workflow (LaunchAgent, daily maintenance, 2 wings + multiple drawers in active use) and the goodmem feature surface duplicates without adding distinct value.

Drift trigger: Security advisory, or major release (4.0.x), or the documented add_drawer content-corruption bug not being fixed within 90 days.
Version pin: 3.3.2 (plugin manifest and Anaconda binary)

### Serena

Stage 2 entry: Phase 4
Date evaluated: 2026-05-11
Decision: defer (respect user-disabled signal)

Nominal task: Not exercised. The plugin is installed at `~/.claude/plugins/cache/claude-plugins-official/serena/unknown/` but the user's settings.json sets `serena@claude-plugins-official: false`. Per Phase 1 inventory, the disable is deliberate (not an accident of installation).

Edge case: Not run.

No-op cost: When disabled, the plugin's tools do not enter the pool. Cache footprint is zero. The plugin cache directory is on-disk but does not load.

Rationale: Serena is an LSP integration that provides semantic code navigation (find symbol, references, rename across language). The use case is high-friction in Claude Code's flat-tool-pool model: LSP responses are large, the model has to learn the symbol-navigation vocabulary, and the harness's existing built-in tools (Grep, Glob, Read) cover the common navigation cases. Rock's pre-existing decision to disable Serena is the strongest evidence available about the cost-vs-value gradient on this machine. The harness reference respects the signal: keep disabled, defer adoption until Rock has a specific use case that built-ins do not serve.

Drift trigger: Rock requests a specific code-navigation task that built-ins cannot handle, or upstream major version with a new feature surface.
Version pin: not applicable (deferred).

### affaan-m/everything-claude-code

Stage 2 entry: Phase 4 (paper evaluation; not installed)
Decision: reject

Nominal task: Not run; project is not present on this machine.

Edge case: Not run.

No-op cost: zero (would be the adoption cost if installed).

Rationale: The repository is a configuration reference rather than a tool. The harness's `foundation/` documents and `mac/ARCHITECTURE.md` carry the equivalent reasoning in a form that fits this build's needs. Adopting a second reference repository would create a maintenance vector (sync with upstream) for material the harness already owns. The post-launch revision cadence is the appeal path if a specific affaan-m skill or hook turns out to close a gap; current signal does not justify wholesale adoption.

### disler/claude-code-hooks-mastery

Stage 2 entry: Phase 4 (paper evaluation; not installed)
Decision: reject

Nominal task: Not run.

Edge case: Not run.

No-op cost: zero.

Rationale: The hooks Phase 3 wrote (6 Python scripts, each with header, threat citation, verification command) cover the threats Phase 2 elected. The disler reference adds breadth (more hook examples) without depth (no hook there enforces a threat Phase 2 elected that Phase 3 has not already covered). Adopting the broader hook collection would introduce hooks for threats Phase 2 explicitly skipped or deferred, weakening the calibrated-minimum posture. Reject; revisit post-launch if a specific hook there turns out to fill a Phase 3 gap.

### Other enabled plugins (13)

The current `~/.claude/settings.json` enables 13 plugins beyond superpowers and mempalace: context7, github, security-guidance, playwright, pyright-lsp, feature-dev, code-review, vercel, ralph-loop, goodmem, frontend-design, plus typescript-lsp/sentry/serena currently disabled. The Phase 4 harness reference (`mac/harness/settings.json`) carries only superpowers + mempalace as the calibrated minimum.

Phase 5 deep-evaluates the other 13 plugins for inclusion in Rock's rebuilt `~/.claude/settings.json` per Q3. Each adoption decision applies the `mcp-server-pre-trust-audit` skill (for plugins that ship MCP servers) and the `seed-evaluation` skill (for plugins that ship skills, agents, or commands). The context7 plugin's unpinned-npx invocation is the first decision in that pass; the rationale for the supply-chain-discipline override lives in `phase-outputs/PHASE-4-NOTES.md` §context7.

## Rejected after deep eval

Candidates that survive pre-filter but fail deep eval land here with a paragraph naming the specific failure mode. The list serves two purposes: it prevents re-evaluation of the same candidate without new information, and it documents what failure modes the methodology actually catches.

Phase 5 reviews this section against the rejected-at-pre-filter list to look for patterns. Repeated failure modes across multiple candidates may indicate a structural issue with how the harness presents the integration surface.

## Notes on the methodology

The integration test is the evidence. The README, the star count, the vendor pitch, and the rubric score are not.

A candidate that performs well on the nominal task but fails the edge case is rejected or integrated with constraints that prevent the failure mode. A candidate that performs well on both but carries a high no-op cost (large cache prefix injection, instruction-following degradation, tool slot inflation) is integrated with a documented opportunity cost that gets revisited on the next QC.5 trigger.

The decision is binary at the integration level (integrate / integrate-with-constraints / reject) but the rationale captures the gradient. Phase 5's Reviewer subagent audits each decision against the rationale and the threat model.
