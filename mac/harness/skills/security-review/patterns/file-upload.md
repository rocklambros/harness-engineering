# Unsafe File Upload Handling

The code accepts an uploaded file and trusts something about it: the name, the extension, the declared content type, or the path it asks to be stored at. Each of those is attacker controlled.

**CWE:** CWE-434 (Unrestricted Upload of File with Dangerous Type), CWE-22 (Improper Limitation of a Pathname to a Restricted Directory)
**Severity:** High to Critical. A web-executable upload is remote code execution. A traversal path is arbitrary file write.
**Threats:** T.1 (benign-prompt vulnerability generation).

## Where this applies

Matched by content heuristic: upload handlers, multipart parsers, anything that writes a caller-supplied file. The skill loads this file when upload code is touched.

## Why AI-generated code hits this

Checking the extension and saving under the original filename is the obvious implementation and it demos correctly. The trust in caller-supplied metadata and the path-traversal in the filename are invisible until someone sends a crafted name.

## BAD

```python
# Trusts the client extension and the client filename.
f = request.files["upload"]
f.save(f"/var/www/uploads/{f.filename}")   # filename = ../../app/routes.py
```

```javascript
// Trusts the declared content type.
if (req.file.mimetype === "image/png") store(req.file);  // header is attacker set
```

## GOOD

```python
# Ignore client metadata. Generate the name. Confine the path. Verify content.
import os, uuid, imghdr
base = "/var/www/uploads"
ext = {"jpeg": ".jpg", "png": ".png"}.get(imghdr.what(request.files["upload"]))
if ext is None:
    raise ValueError("unsupported type")          # content, not extension
dest = os.path.join(base, f"{uuid.uuid4()}{ext}")  # generated name, no traversal
request.files["upload"].save(dest)
```

```javascript
// Store outside the web root, served through a handler that sets the type.
const name = crypto.randomUUID();
await fs.writeFile(`/srv/blobs/${name}`, req.file.buffer);
```

## Common wrong fix

Blocklisting `.php` or `.exe` is not a fix. Execution depends on server config, double extensions and case and null bytes evade the list, and the next dangerous type is not on it. The fix is an allowlist of content-verified types, a generated storage name, a confined path, and storage outside any web-executable directory.

## Detection limits

Semgrep can flag a save built from a client filename and some path-join sinks. It cannot verify that type checking is content based rather than extension based, which is the core of the defense. This pattern is primarily Layer 1: never trust caller-supplied name, extension, or content type, and never store inside a web-executable path.

## Semgrep cross-reference (Layer 2)

In `p/default` and `p/security-audit`, run by the Phase 3 PostToolUse hook:

- `python.lang.security.audit.path-traversal.path-traversal-join`
- `javascript.lang.security.audit.path-traversal.path-join-resolve-traversal`

A hit here is a Layer 2 finding. A clean scan does not prove content-based type checking exists.

## Primary sources

CWE-434, CWE-22, MITRE CWE database (`https://cwe.mitre.org/data/definitions/434.html`, `/22.html`). OWASP File Upload Cheat Sheet. Pattern selection from the Arcanum-Sec sec-context taxonomy (R.2.2, CC BY 4.0, Jason Haddix, Arcanum Information Security). Methodology from SecureForge (R.2.1, MIT). Content rewritten to repo voice.
