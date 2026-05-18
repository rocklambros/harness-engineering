# Command Injection

Untrusted input reaches a shell or process invocation. The model builds a command string and runs it through a shell because that is the path of least resistance for "call this tool from code."

**CWE:** CWE-77 (Command Injection), CWE-78 (OS Command Injection), CWE-94 (Code Injection)
**Severity:** Critical. Arbitrary command execution with the process's privileges.
**Threats:** T.1 (benign-prompt vulnerability generation).

## Where this applies

Python (`.py`, `.pyi`) and shell scripts (`.sh`, `.bash`). Any code that shells out. The skill loads this file for Python and shell.

## Why AI-generated code hits this

Shell-true invocation, the system call, backticks, and the interpreter-eval builtin are compact and demo well. The model uses them when a prompt says "run ffmpeg" or "ping the host." The injection appears the moment any part of that command comes from input.

## BAD

```python
# Shell invocation with an interpolated argument. host is request input.
import subprocess
subprocess.run(f"ping -c 1 {host}", shell=True)
```

A host value of `8.8.8.8; rm -rf /` runs the second command.

```python
# Dynamic code execution from input is remote code execution by definition.
result = __builtins__.eval(request.args.get("expr"))
```

```bash
# Unquoted expansion of an external variable into a command.
curl "$URL" | bash
```

## GOOD

```python
# Argument list, no shell. Arguments stay arguments.
import subprocess
subprocess.run(["ping", "-c", "1", host], shell=False)
```

```python
# Parse instead of interpret. A literal-only evaluator.
import ast
result = ast.literal_eval(expr)  # raises on anything that is not a literal
```

```bash
# Allowlist before use, quote every expansion.
case "$URL" in
  https://releases.example.com/*) curl -fsSL -- "$URL" -o /tmp/pkg ;;
  *) echo "refused: URL not on allowlist" >&2; exit 1 ;;
esac
```

## Common wrong fix

Escaping shell metacharacters by hand is not a fix. The metacharacter set differs per shell, and one missed character is full execution. Quoting the interpolated variable still leaves command substitution and argument injection. The fix is to remove the shell: pass an argument vector to the process directly, so the input can never be parsed as syntax.

## Detection limits

Semgrep flags shell-true, the system call, and the eval builtin reliably. It does not always resolve a command string assembled across functions, and it cannot judge whether a shell is truly unavoidable. Layer 1 rule: argument vector with no shell is the default, a shell requires an allowlist and an explicit decision.

## Semgrep cross-reference (Layer 2)

In `p/default` and `p/security-audit`, run by the Phase 3 PostToolUse hook:

- `python.lang.security.audit.subprocess-shell-true.subprocess-shell-true`
- `python.lang.security.audit.eval-detected.eval-detected`
- `bash.lang.security.ifs-tampering.ifs-tampering`

A hit here is a Layer 2 finding. Fix in the same session.

## Primary sources

CWE-77, CWE-78, CWE-94, MITRE CWE database (`https://cwe.mitre.org/data/definitions/78.html`). OWASP OS Command Injection Defense Cheat Sheet for the argument-vector rule. Pattern selection from the Arcanum-Sec sec-context taxonomy (R.2.2, CC BY 4.0, Jason Haddix, Arcanum Information Security). Methodology from SecureForge (R.2.1, MIT). Content rewritten to repo voice.
