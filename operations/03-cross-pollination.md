# Post-Mac 3 — Cross-pollinate Mac validation findings into Jetson and Windows scaffolds

<role>
You are propagating Mac-validated facts into the Jetson and Windows scaffolds so that when Rock executes those builds, the prompts carry the platform-relevant evidence the Mac build produced. The capabilities-identical-across-platforms locked decision (3) does not mean Mac evidence becomes Jetson or Windows fact. It means Mac evidence shifts the question from "is this true at all" to "is this true on this platform too." Markers narrow rather than disappear.

You are not lifting Mac decisions wholesale. You are taking each `<NEEDS-JETSON-PORT-VALIDATION>` and `<NEEDS-WINDOWS-PORT-VALIDATION>` marker and asking whether Mac evidence informs it, and if so, replacing it with tighter framing that preserves the verification requirement.
</role>

<effort>xhigh</effort>

<mode>default mode (writes). Plan-mode pass first to classify findings, then default-mode writes.</mode>

<thinking>adaptive</thinking>

<context_budget>Run /context at start and end. Phase reads the Mac-validated source artifacts, the Jetson scaffold artifacts, and the Windows scaffold artifacts. Cache load is substantial. Record state in `phase-outputs/POST-MAC-3-CONTEXT.md`.</context_budget>

<parallel_tool_calls>
Read Mac sources in parallel: `mac/README.md`, `mac/ARCHITECTURE.md`, `mac/harness/CLAUDE.md`, `mac/harness/settings.json`, `phase-outputs/PHASE-0-DECISIONS.md`, `phase-outputs/ANSWERS.md`, `phase-outputs/PHASE-3-NOTES.md`, `phase-outputs/PHASE-4-NOTES.md`, `phase-outputs/PHASE-5-AUDIT.md`.

Read Jetson and Windows scaffolds in parallel: `jetson/README.md`, `jetson/ARCHITECTURE.md`, `jetson/harness/CLAUDE.md`, every file in `jetson/prompts/`, `jetson/evaluations/pre-filter.md`, `windows/README.md`, `windows/ARCHITECTURE.md`, `windows/harness/CLAUDE.md`, every file in `windows/prompts/`, `windows/evaluations/pre-filter.md`.
</parallel_tool_calls>

<scope>
Apply only to:
- `jetson/ARCHITECTURE.md` (writes)
- `jetson/harness/CLAUDE.md` (writes, minor)
- `jetson/prompts/phase-3-deterministic-layer.md` (writes)
- `jetson/prompts/phase-4-extension-layer.md` (writes)
- `jetson/prompts/phase-5-wire-and-document.md` (writes)
- `jetson/evaluations/pre-filter.md` (writes)
- `windows/ARCHITECTURE.md` (writes)
- `windows/harness/CLAUDE.md` (writes, minor)
- `windows/prompts/phase-3-deterministic-layer.md` (writes)
- `windows/prompts/phase-4-extension-layer.md` (writes)
- `windows/prompts/phase-5-wire-and-document.md` (writes)
- `windows/evaluations/pre-filter.md` (writes)
- `phase-outputs/POST-MAC-3-CONTEXT.md` (writes)
- `phase-outputs/POST-MAC-3-NOTES.md` (writes: classification log and propagation decisions)

Do not modify `mac/` (the source). Do not modify `foundation/`, `research/`, or any other file outside the scope list.
</scope>

## What to do

### Stage 1: Classify Mac findings by portability class

Read every Mac-validated finding. Classify each into one of three buckets:

1. **Platform-agnostic**: the finding describes Claude Code v2.1.x behavior, the hook event schemas, the cached prefix discipline, the cache-economy semantics, the 50-subcommand bypass threshold, the auto-mode classifier false-positive rate, the seed evaluation pre-filter outcomes for tools whose architecture support is verified for the target platform. These findings translate cleanly to expectations on Jetson and Windows.

2. **Platform-informed-but-platform-specific**: the finding describes a specific Mac behavior (sandbox-exec primitive, Anaconda Python install path, Homebrew package paths, macOS session log path format) where the equivalent on Jetson or Windows is different but the Mac evidence informs the question. The marker on the other platforms gets tighter framing but does not disappear.

3. **Mac-only**: the finding is genuinely Mac-specific (macOS version pin, FileVault assumption, SIP integrity model, the absence of Little Snitch on Rock's specific machine, Anaconda's broken semgrep install). The Jetson or Windows marker stays as-is, possibly with a brief note explaining why Mac evidence does not apply.

Document every classification decision in `phase-outputs/POST-MAC-3-NOTES.md` with a one-paragraph rationale per finding. The classification is the load-bearing work; the write stage executes it mechanically.

### Stage 2: Propagate per finding

For each `<NEEDS-JETSON-PORT-VALIDATION>` marker in the Jetson scaffold and each `<NEEDS-WINDOWS-PORT-VALIDATION>` marker in the Windows scaffold:

- **Platform-agnostic finding**: replace the marker with the Mac-validated fact, followed by "verify behaviorally on this platform before adoption." Cite the Mac source (`phase-outputs/<file>` or `mac/<file>` line reference).
- **Platform-informed finding**: tighten the marker to name the Mac observation and what the Jetson or Windows equivalent question is. Example: `<NEEDS-JETSON-PORT-VALIDATION: Mac session log path format is ~/.claude/projects/<encoded-cwd>/<session-uuid>.jsonl with / replaced by - in the encoded directory name. Verify Linux Claude Code uses the same scheme or an XDG-style alternative>`.
- **Mac-only finding**: leave the marker unchanged. Optionally add a one-line note explaining the non-portability.

### Stage 3: Update evaluation worksheets

For Mac-evaluated seeds where Phase 1 architecture support resolved positively for Jetson (ARM64 Linux) or Windows (x86_64), update the corresponding row in `jetson/evaluations/pre-filter.md` and `windows/evaluations/pre-filter.md`. Do not lift Mac's Phase 3/4 adoption decisions onto the other platforms. The pre-filter table records architecture support and maintainership; the deep-eval decision is per platform.

For seeds Mac rejected at pre-filter, update the corresponding row on Jetson and Windows only if the rejection reason was platform-agnostic (license, maintainership). Architecture-rejection on Mac does not necessarily apply to Jetson or Windows; leave those as their own pre-filter.

<investigate_before_answering>
Before classifying a Mac finding as platform-agnostic, verify the finding is not Mac-specific by reading the source's full context. The Mac session log path uses macOS-specific path conventions even though session logging itself is platform-agnostic.

Before replacing a marker, verify the Mac fact you are citing actually appears in the source file at the line you cite. The classification log depends on accurate citations.

Before lifting a seed's pre-filter outcome from Mac to another platform, verify the architecture-support column on the other platform's worksheet. Mac's evaluation does not resolve another platform's architecture question.
</investigate_before_answering>

## Deliverables

- Updated Jetson section (4 prompt files, ARCHITECTURE.md, harness/CLAUDE.md, evaluations/pre-filter.md): every platform-agnostic marker resolved, every platform-informed marker tightened, every Mac-only marker preserved
- Updated Windows section: same
- `phase-outputs/POST-MAC-3-NOTES.md`: classification log naming every finding, its bucket, the Jetson treatment, the Windows treatment, and the citation back to Mac evidence
- `phase-outputs/POST-MAC-3-CONTEXT.md`: context-budget record

## Verification

Before reporting complete:

- `grep -c '<NEEDS-JETSON-PORT-VALIDATION>' jetson/` should be lower than before this phase ran (count before vs after recorded in the notes file).
- `grep -c '<NEEDS-WINDOWS-PORT-VALIDATION>' windows/` should be lower than before this phase ran.
- Every resolved marker on Jetson has a citation back to a Mac source. Same for Windows.
- Every tightened marker on Jetson reads more specifically than its pre-pollination version. Same for Windows.
- `bash scripts/drift-check.sh` returns 0. The CLAUDE.md hierarchy did not grow.

Report the marker count delta for both platforms and the line count delta of each modified file.

## Anti-overengineering

Do not invent Jetson- or Windows-specific facts. If unsure, retain the marker. The propagation discipline is to narrow questions, not to answer them.

Do not lift Mac decisions wholesale onto other platforms. Each platform's Phase 2 interview will produce its own answers. Cross-pollination is evidence-propagation, not decision-propagation.

Do not modify Mac artifacts. They are the source. Bidirectional propagation is out of scope.

Do not extend the Jetson or Windows scope to include new artifacts (skills, hooks, deny rules). Those land in the platform's own Phase 3 and Phase 4. Cross-pollination updates documentation and pre-validation framing only.

If during classification you find a Mac finding that should have been in the original Mac architecture document but isn't, do not back-port it here. Flag the gap in the notes file as a Mac-section revision candidate for the next revision cycle.
