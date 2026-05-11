# bash-deny-git-push-force

## Pattern

```
Bash(git push --force:*)
Bash(git push -f:*)
Bash(git push --force-with-lease:*)
```

Three deny entries cover the canonical force-push forms. `--force-with-lease` is included because the lease check protects only against losing intermediate commits; an unauthorized push of new history still happens, and the asymmetry between local intent and remote outcome is the same.

## Threat addressed

`foundation/02-architectural-principles.md` Principle 3 (reversibility-weighted risk). A force-push overwrites remote history. Local branch protection rules can roll it back if reflog or backups exist, but the operation crosses a trust boundary into the shared GitHub remote, which the harness treats as out-of-band reversibility.

Also `foundation/01-threat-model.md` Assets #1 (source code integrity). The most common harness-fault scenario for source-code integrity is an automated push of stale or wrong history.

## Why deny, not ask

Force-push has narrow legitimate use (rebasing a feature branch before merge). The legitimate cases are infrequent and intentional; the dangerous cases are the silent ones triggered by a confused recovery flow. Deny + Rock-overrides-on-demand is the correct cost/benefit. Rock can override by approving the request manually after the deny fires, or by removing the deny temporarily for a single session.

## Test

Positive (deny fires):
```
echo '{"tool_name":"Bash","tool_input":{"command":"git push --force origin main"}}'
```
Claude Code's deny rule evaluation should match `Bash(git push --force:*)` and return a deny decision.

Negative (deny does not fire):
```
echo '{"tool_name":"Bash","tool_input":{"command":"git push origin main"}}'
```
Plain `git push` is not denied.

## Provenance

Phase 3, 2026-05-11. Foundation: Principle 3 (reversibility), Asset #1.
