# Patch: managed-store exemption in PreToolUse-external-write-gate (Jetson)

Post-Phase-3 refinement. Apply the same `is_claude_code_managed_store` exemption
to the Jetson copy of `PreToolUse-external-write-gate.py` that landed first on
Mac. Reference commit on Mac:
`hook: exempt Claude Code managed stores from external-write-gate`.

The Mac source `mac/harness/hooks/PreToolUse-external-write-gate.py` is the
canonical implementation. Jetson hook scripts are byte-identical to Mac unless a
platform-specific reason to diverge is documented (AP.3, parity not portability).
This prompt is a port runbook, not a redesign.

---

<role>
You are a senior harness engineer applying a post-Phase-3 refinement on Jetson.
The change is mechanical: take the current Mac source byte-for-byte and deploy
it. Then prove the exemption works on this host with the same verification
matrix the Mac change was landed with.

Match the writing rules.
</role>

<effort>medium</effort>
<mode>default</mode>
<thinking>standard</thinking>
<context_budget>One pass. No compaction expected.</context_budget>
<scope>Strict. One hook file in the repo, one deployed copy on disk, one commit.</scope>

<context>
The Mac change introduced a class abstraction in
`PreToolUse-external-write-gate.py`: Claude Code's own managed, regenerable
write stores are exempted from the external-write gate. The class today is two
paths:

1. Auto-memory: `~/.claude/projects/<encoded-cwd>/memory/...`
2. Plan files: `~/.claude/plans/...`

Everything else under `~/.claude/` stays gated (settings.json, mcp.json, hooks,
skills, agents, CLAUDE.md, audited-hashes.json, anything under
`~/.claude/projects/<p>/` that is not `memory/`).

The rationale is in the hook's module header (`Exemption:` block). Read it
before porting so you can verify the deployed Jetson copy matches intent, not
just bytes.

On Jetson the host home is typically `/home/<user>`, not `/Users/<user>`. The
hook uses `os.path.expanduser("~")` so it adapts automatically. No path edits
needed in the script itself.
</context>

<investigate_before_answering>
Read:

- `mac/harness/hooks/PreToolUse-external-write-gate.py` (canonical source,
  includes the exemption and the module-header rationale)
- `jetson/harness/hooks/PreToolUse-external-write-gate.py` if it exists
- `jetson/harness/hooks/README.md`
- `foundation/02-architectural-principles.md` AP.3 (parity), AP.5 (commit)
- `scripts/drift-check.sh` (check 5 enforces deployed == source via `cmp -s`)
</investigate_before_answering>

<instructions>

### 1. Port the hook source into the Jetson tree

If `jetson/harness/hooks/PreToolUse-external-write-gate.py` does not exist,
create it as a byte-for-byte copy of `mac/harness/hooks/PreToolUse-external-write-gate.py`.

If it exists and already includes `is_claude_code_managed_store`, confirm it is
byte-identical to the Mac source. If it diverges, replace it with the Mac
source unless the divergence has a documented Jetson-specific reason in
`jetson/ARCHITECTURE.md`.

```bash
cp mac/harness/hooks/PreToolUse-external-write-gate.py \
   jetson/harness/hooks/PreToolUse-external-write-gate.py
cmp -s mac/harness/hooks/PreToolUse-external-write-gate.py \
       jetson/harness/hooks/PreToolUse-external-write-gate.py && echo "byte-identical"
```

### 2. Deploy to the live host hooks directory

The deployed copy at `~/.claude/hooks/PreToolUse-external-write-gate.py` is what
Claude Code actually invokes per write. Mirror the tracked source byte-for-byte
so the drift check passes:

```bash
cp jetson/harness/hooks/PreToolUse-external-write-gate.py \
   ~/.claude/hooks/PreToolUse-external-write-gate.py
chmod +x ~/.claude/hooks/PreToolUse-external-write-gate.py
cmp -s jetson/harness/hooks/PreToolUse-external-write-gate.py \
       ~/.claude/hooks/PreToolUse-external-write-gate.py && echo "deployed == source"
```

### 3. Verification matrix

Run from the repo root. The Python driver below covers the same 20 cases the
Mac landing proved, adapted for the Jetson `$HOME`:

```bash
python3 - <<'PY'
import json, os, subprocess, sys
HOOK = os.path.expanduser("~/.claude/hooks/PreToolUse-external-write-gate.py")
HOME = os.path.expanduser("~")
CWD  = os.getcwd()
ALT  = "/tmp/altproj"

EXEMPT = [
    (CWD, f"{HOME}/.claude/projects/x/memory/MEMORY.md"),
    (CWD, f"{HOME}/.claude/projects/some-other/memory/user-pref.md"),
    (CWD, f"{HOME}/.claude/plans/foo.md"),
    (CWD, f"{HOME}/.claude/plans/nested/dir/plan.md"),
    (ALT, f"{ALT}/src/x.py"),
    (ALT, f"{HOME}/.claude/projects/p/memory/MEMORY.md"),
    (ALT, f"{HOME}/.claude/plans/altproj-plan.md"),
    (CWD, "./local.txt"),
]
GATED = [
    "/tmp/external.txt",
    f"{HOME}/.claude/settings.json",
    f"{HOME}/.claude/mcp.json",
    f"{HOME}/.claude/CLAUDE.md",
    f"{HOME}/.claude/hooks/evil.sh",
    f"{HOME}/.claude/skills/foo/SKILL.md",
    f"{HOME}/.claude/agents/foo.md",
    f"{HOME}/.claude/audited-hashes.json",
    f"{HOME}/.claude/projects/p/notes.txt",
    "/some/other/repo/src/main.py",
]

def run(cwd, path):
    payload = json.dumps({"tool_name":"Write","tool_input":{"file_path":path},"cwd":cwd})
    r = subprocess.run(["python3", HOOK], input=payload, capture_output=True, text=True)
    return r.returncode, r.stdout

p = f = 0
for cwd, path in EXEMPT:
    code, out = run(cwd, path)
    ok = (code == 0 and out == "")
    print(("OK   " if ok else "FAIL ") + f"exempt [{cwd}] {path}" + ("" if ok else f"  out={out!r}"))
    p += ok; f += not ok
for path in GATED:
    code, out = run(CWD, path)
    ok = '"permissionDecision": "ask"' in out
    print(("OK   " if ok else "FAIL ") + f"gated  {path}" + ("" if ok else f"  out={out!r}"))
    p += ok; f += not ok
print(f"\npass={p} fail={f}")
sys.exit(0 if f == 0 else 1)
PY
```

All 18 cases must pass. Document outcome in `phase-outputs/PHASE_3_VALIDATION.md`
under a Jetson post-Phase-3 refinement section.

### 4. Drift and SAST

```bash
bash scripts/drift-check.sh
# Required: "deployed hooks match tracked source"

semgrep --error --quiet --config p/python --config p/security-audit \
  jetson/harness/hooks/PreToolUse-external-write-gate.py
```

Both must exit 0.

### 5. Commit

AP.5 template. Single decision. Example:

```
hook(jetson): exempt Claude Code managed stores from external-write-gate

Context: Auto-memory and plan-file writes outside cwd produced a constant
permission prompt on Jetson even under bypass mode. Hooks run after the
permission engine by design, so no allow rule could suppress it. Mac landed
the class-aware exemption first.

Decision: Port the Mac source byte-for-byte into jetson/harness/hooks/. The
hook now exempts ~/.claude/projects/*/memory/ (auto-memory) and ~/.claude/plans/
(plan files), while keeping the rest of ~/.claude/ gated. No platform-specific
divergence.

Why: AP.3 (parity), AP.5 (single decision per commit), Principle 3 (the gate's
signal-to-noise improves when high-frequency expected writes stop training
reflexive approval). Reference: Mac commit <SHA>.

Tradeoff: Custom plansDirectory or autoMemoryDirectory overrides outside the
default paths are not auto-detected. Documented in the hook header for future
maintainers.
```

</instructions>

<deliverable>
The tracked Jetson copy of `PreToolUse-external-write-gate.py` is byte-identical
to Mac. The deployed copy at `~/.claude/hooks/` is byte-identical to source.
Verification matrix passes 18/18. Drift check green. Semgrep clean. One commit
on a feature branch. Short summary report.
</deliverable>

<verification>
Drift check passes (`scripts/drift-check.sh` exit 0 with "deployed hooks match
tracked source").

Semgrep exits 0 on the Jetson hook copy.

The 18-case verification matrix passes with `fail=0`.

`PHASE_3_VALIDATION.md` records the run and outcome.
</verification>
