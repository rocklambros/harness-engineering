# Data Exposure Through Errors, Debug, and Over-Fetching

Sensitive data leaves the system through a channel that was never meant to carry it: a verbose error, a debug endpoint left on in production, or a response that returns more fields than the caller should see.

**CWE:** CWE-200 (Exposure of Sensitive Information to an Unauthorized Actor), CWE-209 (Generation of Error Message Containing Sensitive Information)
**Severity:** Medium to High. Stack traces and over-fetched fields hand an attacker the internal map and sometimes the credentials.
**Threats:** T.6 (credential and secret exposure), T.1 (benign-prompt vulnerability generation).

## Where this applies

Infrastructure code (`.tf`, `.tfvars`, `.hcl`, `.yaml`) and, by content heuristic, error handlers, serializers, and API responses. The skill loads this file for infrastructure and alongside endpoint code.

## Why AI-generated code hits this

Returning the exception text is the fastest way to make an endpoint debuggable, and serializing the whole model object is one line shorter than picking fields. Both read as helpful. Both leak.

## BAD

```python
# The client receives the stack trace and the SQL.
@app.errorhandler(Exception)
def on_error(e):
    return str(e), 500   # leaks query text, paths, internals

# Debug server in production.
app.run(debug=True)
```

```javascript
// Over-fetch. The whole user row, including hash and reset token, ships.
res.json(await db.users.findById(id));
```

```hcl
# Storage bucket world-readable.
resource "aws_s3_bucket_acl" "a" { acl = "public-read" }
```

## GOOD

```python
# Generic message to the client, full detail to the server log.
@app.errorhandler(Exception)
def on_error(e):
    log.exception("request failed")
    return {"error": "internal error"}, 500

app.run(debug=False)
```

```javascript
// Explicit field projection. Only what the caller may see.
const u = await db.users.findById(id);
res.json({ id: u.id, name: u.name, email: u.email });
```

```hcl
resource "aws_s3_bucket_acl" "a" { acl = "private" }
```

## Common wrong fix

Hiding the error text behind a feature flag that defaults on, or trimming fields only on the one endpoint someone noticed, is not a fix. Exposure is the default failure mode, so the control has to be the default behavior: generic external errors everywhere, explicit field allowlists on every serializer, debug off in any non-local environment.

## Detection limits

Semgrep catches debug-on, public ACLs, and returning raw exception objects in known frameworks. It cannot tell that a serialized object contains a sensitive field, because that depends on the data model. Over-fetching is therefore primarily Layer 1: responses are built from an explicit field list, never from a whole record.

## Semgrep cross-reference (Layer 2)

In `p/default` and `p/security-audit`, run by the Phase 3 PostToolUse hook:

- `python.flask.security.audit.debug-enabled.debug-enabled`
- `python.django.security.audit.django-debug-true.django-debug-true`
- `terraform.aws.security.aws-s3-bucket-public-read.aws-s3-bucket-public-read`

A hit here is a Layer 2 finding.

## Primary sources

CWE-200, CWE-209, MITRE CWE database (`https://cwe.mitre.org/data/definitions/200.html`, `/209.html`). OWASP Error Handling Cheat Sheet. Pattern selection from the Arcanum-Sec sec-context taxonomy (R.2.2, CC BY 4.0, Jason Haddix, Arcanum Information Security). Methodology from SecureForge (R.2.1, MIT). Content rewritten to repo voice.
