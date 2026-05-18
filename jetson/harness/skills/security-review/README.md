# Security Review Skill

This directory is the pre-generation guidance layer of the three-layer security stack. The skill loads lazily based on file type and surfaces high-frequency anti-patterns before they get written into code.

## Read order

`SKILL.md` is the manifest. Claude Code reads it to decide when to load the skill.

`patterns/` holds the deep-pattern content, one file per anti-pattern. Each file loads on demand based on the triggering file type.

## How to extend

To add a new pattern:

Create a new file in `patterns/` following the structure of the existing pattern files: CWE ID, severity, file-type relevance, BAD examples, GOOD examples, Semgrep rule cross-reference, primary source.

Add an entry in `SKILL.md` mapping the pattern to its triggering file types.

If the pattern needs new Semgrep rules to catch it, add the rule references to the file and verify they exist in the Semgrep registry. If they don't exist, document that the pattern is guidance-only (Layer 1) and not covered by Layer 2.

## How to verify

Run `./scripts/drift-check.sh` from the repo root. It confirms the skill's QC and threat references resolve and the hook scripts pass shellcheck. Then confirm every pattern listed in `SKILL.md` has a matching file in `patterns/`, and that each pattern file states a CWE ID, a Semgrep cross-reference, and a primary source.

If a pattern is documented in `SKILL.md` but has no corresponding `patterns/*.md` file, the drift check flags it.

The automated integration test `mac/scripts/integration-test.sh` is a Phase 5 deliverable specified in `mac/prompts/phase-5-wire-and-document.md`. It is not yet created. The drift check and the manifest-to-`patterns/` consistency check above are the verification until it lands.

## Source attribution

The taxonomy and pattern ranking are informed by the Arcanum-Sec sec-context project (CC BY 4.0). The lazy-load skill mechanism and the in-session feedback methodology are adapted from SecureForge (MIT). Full citations are in `SKILL.md`.
