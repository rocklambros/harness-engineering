# Input Validation

Input is trusted by structure or range without a check. The model writes the function for the input it expected, not the input an attacker sends.

**CWE:** CWE-20 (Improper Input Validation), CWE-1284 (Improper Validation of Specified Quantity in Input)
**Severity:** Medium to High. The downstream effect ranges from a crash to injection, depending on where the unvalidated value lands.
**Threats:** T.1 (benign-prompt vulnerability generation).

## Where this applies

Python (`.py`, `.pyi`), JavaScript and TypeScript (`.js`, `.jsx`, `.ts`, `.tsx`). Any boundary where external data enters. The skill loads this file for Python, JavaScript, and TypeScript.

## Why AI-generated code hits this

Validation is friction the prompt rarely asks for. The model parses the integer, indexes the array, and reads the field without asking what happens when the value is negative, huge, missing, or the wrong type.

## BAD

```python
# Unbounded quantity drives an allocation. CWE-1284.
def make_buffer(req):
    n = int(req.args["count"])      # negative, zero, or 10_000_000 all accepted
    return bytearray(n)
```

```javascript
// Type confusion. body.ids may be a string, an object, or absent.
const ids = req.body.ids;
ids.forEach(id => remove(id));
```

```python
# Path traversal through an unvalidated name.
open(f"/data/{req.args['file']}")   # file=../../etc/passwd
```

## GOOD

```python
# Validate type and range at the boundary. Fail closed.
def make_buffer(req):
    n = int(req.args.get("count", 0))
    if not 1 <= n <= 4096:
        raise ValueError("count out of range")
    return bytearray(n)
```

```javascript
// Validate shape with a schema before use.
const schema = z.object({ ids: z.array(z.string().uuid()).max(100) });
const { ids } = schema.parse(req.body);
```

```python
# Resolve and confine the path.
import os
base = "/data"
p = os.path.realpath(os.path.join(base, req.args["file"]))
if not p.startswith(base + os.sep):
    raise ValueError("path escapes base")
```

## Common wrong fix

Sanitizing by stripping "bad" characters is not validation. It mutates the input into something that passes while still being wrong, and the stripped form often reconstructs the attack downstream. Validation accepts or rejects against an explicit specification, it does not edit the input into shape.

## Detection limits

Semgrep flags some sinks fed by unvalidated input, notably path traversal and prototype pollution. It cannot know the valid range or shape for a given field, which is domain knowledge. Most validation gaps are therefore Layer 1: define the accepted type, range, and shape at every trust boundary, and reject by default.

## Semgrep cross-reference (Layer 2)

In `p/default` and `p/security-audit`, run by the Phase 3 PostToolUse hook:

- `python.lang.security.audit.path-traversal.path-traversal-open`
- `javascript.lang.security.audit.prototype-pollution.prototype-pollution-assignment`
- `python.flask.security.audit.debug-enabled.debug-enabled`

A hit here is a Layer 2 finding.

## Primary sources

CWE-20, CWE-1284, MITRE CWE database (`https://cwe.mitre.org/data/definitions/20.html`). OWASP Input Validation Cheat Sheet. Pattern selection from the Arcanum-Sec sec-context taxonomy (R.2.2, CC BY 4.0, Jason Haddix, Arcanum Information Security). Methodology from SecureForge (R.2.1, MIT). Content rewritten to repo voice.
