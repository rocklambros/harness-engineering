# Archive

Operations superseded during the build sequence. Preserved as historical record of how the operations sequence evolved.

## Contents

### 02-journey-update.md (superseded 2026-05-11)

Original Operation 02 was a focused "complete the six placeholder cells" JOURNEY update at the depth the Phase prompts originally implied. Superseded by Operation 09 (`operations/09-journey-rewrite.md`), which authored JOURNEY as an extended educational narrative with story arc. The original Op 02 never ran; its scope was always covered by the deeper rewrite.

### 06-mac-build-closeout.md (superseded 2026-05-11)

Original Operation 06 was a single consolidated prompt that bundled four deliverables (CHECKPOINT refresh, README rewrite, HARNESS_GUIDE authoring, JOURNEY deep rewrite) into one execution. The bundle had no functional advantage over per-deliverable prompts and added context-switching overhead between three distinct voices. Superseded by four focused prompts (then later expanded to five after the USER_GUIDE addition):

- `operations/06-readme-rewrite.md`
- `operations/07-user-guide.md`
- `operations/08-harness-guide.md`
- `operations/09-journey-rewrite.md`
- `operations/10-build-closeout.md`

Each new prompt is a fresh Claude Code session with focused scope. The original consolidated prompt never ran.

### 07-harness-guide.md (first version, superseded 2026-05-11)

The first split version of Operation 07 conflated two distinct jobs: architectural reference (how is the harness designed, why does each piece exist, what threat does each mitigate) and pragmatic day-to-day (when does each hook fire, what message do you see, what workflow benefits from this harness). The conflation produced a document that explained design but didn't actually tell a reader how to use the harness. Rock surfaced this gap: "I still have no freaking clue what this harness is doing." Superseded by two documents with separate prompts: `operations/07-user-guide.md` (pragmatic) and `operations/08-harness-guide.md` (architectural, tightened scope).

### 08-journey-rewrite.md (first version, superseded 2026-05-11)

The first split version of Operation 08 authored JOURNEY as a `.ipynb` Jupyter notebook with 42-58 cells. The .ipynb rationale was "code cells are runnable; verification against the live repo grows over time." Superseded once Rock surfaced the format-consistency concern: two documentation formats (.md and .ipynb) split the navigation/maintenance story for marginal verification benefit. Superseded by `operations/09-journey-rewrite.md`, which produces JOURNEY.md instead.

### 09-build-closeout.md (first version, superseded 2026-05-11)

The first split version of Operation 09 was the build closeout (CHECKPOINT refresh, cross-document consistency check, behavioral verification protocol). Superseded only by renumbering, not by content change, when the USER_GUIDE addition pushed each subsequent operation up by one. Content carries forward in `operations/10-build-closeout.md` with minor updates for the new document set.

## Why preserve them

Two reasons. First, the supersession is itself a documented decision; the archived files are evidence of how the operations sequence iterated. Second, filesystem-with-morph has no delete tool, so move-to-archive is the cleanest available signal.
