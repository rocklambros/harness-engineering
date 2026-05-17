# Design: standalone docs and Superpowers credit

Date: May 17, 2026
Status: approved, executing in-session

## Problem

Two documentation defects.

First, "TRACT" appears as "TRACT-pattern" or "TRACT pattern" in seven Markdown files. It is the repo author's own coinage from `github.com/rocklambros/TRACT` and is defined only inside one research-reference entry. A reader who hits `README.md:53` has no way to know what it means. The repo's stated value is that it stands on its own except for the outside repos it explicitly cites, so an undefined private term in the front-door docs breaks that promise.

Second, the brainstorm to plan to implement to review loop that produced every artifact in this repo comes from Superpowers (Jesse Vincent, GitHub `obra`, MIT, `https://github.com/obra/superpowers`). Superpowers is not part of the shipped harness, but it is the development discipline that built it. The docs never disclose this. That is a factual omission and an unpaid attribution.

## Decisions

Two decisions were made with the user before this spec was written.

Decision 1: drop the "TRACT" label. The seven section names are already enumerated at every occurrence, so the label carries no information the line does not already give. Replace it with a self-contained descriptor. Retain the `rocklambros/TRACT` credit in exactly one place, `foundation/04-research-references.md` R.4.2, because that file is the canonical references list and the user chose to keep the credit there.

Decision 2: credit Superpowers in three non-repetitive touches. One explanatory section plus one attribution bullet in `README.md`, and one narrative pointer in `JOURNEY.md`. No section in `HARNESS_GUIDE.md` or `USER_GUIDE.md`, because Superpowers is not part of the harness and those guides are scoped to the harness itself. Three touches, three different audiences, no re-explanation.

## Scope

In scope: the seven files that contain "TRACT", plus `README.md` and `JOURNEY.md` for the Superpowers credit.

Out of scope: `research/` is read-only source per the project CLAUDE.md, and its Superpowers mentions are correct citations. `phase-outputs/` and `operations/` are historical records and contain no "TRACT". "All .md files" is read as "every file that needs the change," not a paste into every file in the tree.

## Part 1: drop the TRACT label

| File | From | To |
|---|---|---|
| `README.md` | `under 200 lines, TRACT-pattern (Role, ...)` | `under 200 lines, organized into seven sections (Role, ...)` |
| `HARNESS_GUIDE.md` | `Under 200 lines. TRACT pattern: Role, ...` | `Under 200 lines. Seven sections: Role, ...` |
| `mac/ARCHITECTURE.md` | `It applies the TRACT pattern (Role, ...)` | `It follows a seven-section pattern (Role, ...)` |
| `mac/prompts/phase-3-deterministic-layer.md` | `TRACT pattern (Role, ...). Under 200 lines hard cap` | `Seven-section pattern (Role, ...). Under 200 lines hard cap` |
| `jetson/prompts/phase-3-deterministic-layer.md` | `TRACT pattern. Capability-equivalent to mac...` | `Seven-section pattern (Role, ...). Capability-equivalent to mac...` |
| `windows/prompts/phase-3-deterministic-layer.md` | `TRACT pattern. Same as Mac...` | `Seven-section pattern (Role, ...). Same as Mac...` |
| `foundation/04-research-references.md` | `Used for: CLAUDE.md TRACT pattern (...). The TRACT acronym is borrowed...` | `Used for: the seven-section CLAUDE.md pattern (...). The section structure is borrowed from this repo's TRACT acronym...` |

The Jetson and Windows prompts gain the explicit seven-name parenthetical, because they previously leaned on the reader knowing the now-removed label. The R.4.2 heading and its `github.com/rocklambros/TRACT` URL are unchanged. After this change, the string "TRACT" survives in the repo only in `foundation/04-research-references.md`.

## Part 2: Superpowers credit

`README.md` gains a `## How this repo was built` section between "How to read this repo" and "What ships in the harness". It states the development loop, that Superpowers is the development discipline and not part of the shipped harness, why the loop suits a reasoning-first repo, and the author and license.

`README.md` Attribution list gains one bullet after the CISA entry, pointing at the new section.

`JOURNEY.md` gains one sentence after the intro paragraph naming the loop and its source and pointing back to the README section. No re-explanation.

## Verification

After edits: `grep -rn TRACT --include="*.md" .` returns matches only in `foundation/04-research-references.md`. `README.md` and `JOURNEY.md` contain the Superpowers credit. The new README section and the JOURNEY sentence conform to the project writing rules (no em dashes, no semicolons, no banned sentence openers, no filler, no corporate slop). Semgrep PostToolUse hook clean on every edited file.

## Process deviation

The brainstorming skill's default terminal step is to hand a written spec to the writing-plans skill for a separate execution session. For an eight-file, fully-specified documentation edit that is disproportionate, and the user instruction is to make the changes now. This spec records the reasoning. Execution happens in-session. The deviation was surfaced to the user and approved.
