---
name: mcp-server-pre-trust-audit
description: Use when about to register a new MCP server, add to mcpServers, or accept an MCP invocation from a cloned repo. Walks the pre-trust audit (license, source review, network egress, version pin, secret-handling) before the server reaches the tool pool. Closes the gap above ~/.claude/mcp.json that the SessionStart hook does not gate.
---

# MCP Server Pre-Trust Audit

## When this fires

The harness's SessionStart hook (`mac/harness/hooks/SessionStart-audit-claude-config.py`) audits in-repo `.claude/settings.json`, `.claude/settings.local.json`, and `.mcp.json` against a hash registry. It does NOT audit user-level `~/.claude/mcp.json` or new additions to `mac/harness/settings.json` `mcpServers`. Those entries are added by Rock at the keyboard, outside the SessionStart gate.

This skill activates when:

- A request mentions registering, adding, or installing a new MCP server.
- A request asks to enable a Claude Code plugin whose `.mcp.json` declares MCP servers.
- A cloned repo proposes installing an MCP server via its README or setup script.
- The conversation drifts toward "let's wire up X MCP".

## The audit (six checks)

Each check is binary: pass or fail. Any fail blocks adoption. Document each result in `phase-outputs/PHASE-4-NOTES.md` (during build phases) or in the commit message that registers the server (post-launch).

### 1. License

Read the server's LICENSE file. MIT, Apache-2.0, BSD, and similar permissive licenses pass without further review. GPL, AGPL, SSPL, BSL, and case-by-case licenses require explicit decision on whether the harness's intended use is compatible.

### 2. Source review

Read the server's entry point and any subprocess invocations. The fast version: clone the repo, `find . -name '*.py' -o -name '*.ts' -o -name '*.js' | xargs grep -nE '(exec|spawn|subprocess|os\.system|requests\.|http\.|fetch\(|urllib)'`. Anything that surprises you blocks adoption until the surprise is understood.

The slow version: read the server's tool implementations end-to-end. Required for any server that handles secrets, executes arbitrary code, or writes outside its working directory.

### 3. Network egress

List the external endpoints the server contacts at runtime. The discipline is the deny-by-default posture from Principle 2: the server gets one specific endpoint per declared purpose. A server that "reaches out as needed" without a documented endpoint list fails the check.

The harness has no OS-level egress monitor (Phase 2 Q7 elected skip). The MCP allowlist + the per-server endpoint review is the egress defense.

### 4. Version pin

The server's invocation in `mcpServers` pins to a specific version, not a floating tag. `npx -y @upstash/context7-mcp` is unpinned and fails this check; `npx -y @upstash/context7-mcp@2.1.3` passes. Plugin-defined `.mcp.json` that uses unpinned forms gets overridden by an explicit `mcpServers` entry in `mac/harness/settings.json` with the pin.

### 5. Secret handling

If the server takes credentials (API tokens, database URLs, key paths), the credentials live in environment variables resolved at server startup, not in plaintext in `~/.claude/mcp.json` or `mac/harness/settings.json`. macOS Keychain or 1Password CLI is the secret store; `mcpServers.<server>.env.X = "${env:X}"` is the indirection form.

Phase 1 surfaced a HIGH-severity finding here (plaintext Hetzner Cloud API token in `~/.claude/mcp.json`). The defense lives in this check.

### 6. Tool subset

The server's allowlisted tool set is the minimum the harness needs, not the wildcard surface. Inline the explicit tool list in the `mcpServers` entry where the server schema supports it. Where it does not, document in `PHASE-4-NOTES.md` which tools Rock expects to invoke and which stay unused.

## When the audit fails

A failed check blocks adoption. The audit produces one of three decisions:

- **Adopt**: all checks pass. Add to `mcpServers` with the pinned invocation, the env-var indirection, the tool subset.
- **Adopt-with-constraints**: most checks pass, specific risks are mitigated by hook rules or deny patterns added in the same commit. The constraints are explicit, not aspirational.
- **Reject**: one or more checks fail, no mitigation lands. The server stays out. Rejection is logged so the next audit does not re-evaluate without new information.

## Related artifacts

- Phase 3 hook: `mac/harness/hooks/SessionStart-audit-claude-config.py` (in-repo defense)
- Phase 3 hook: `mac/harness/hooks/PreToolUse-supply-chain-bash-checks.py` (catches unpinned Bash installs)
- Foundation: `foundation/01-threat-model.md` Threat actors #3 (CVE-2025-59536 class) and #6 (compromised or hostile MCP server)
- Foundation: `foundation/02-architectural-principles.md` Principle 2 (least privilege)
- Foundation: `foundation/03-seed-evaluation-methodology.md` (the broader seed framework)
- Owner: harness-engineering (Phase 4, 2026-05-11)
