# Authentication and Access-Control Failures

The code authenticates weakly, stores credentials poorly, or skips the authorization check. The model produces a route that works for the happy path and never adds the check that was not in the prompt.

**CWE:** CWE-287 (Improper Authentication), CWE-306 (Missing Authentication for Critical Function), CWE-384 (Session Fixation)
**Severity:** High. Account takeover, privilege escalation, unauthenticated access to protected functions.
**Threats:** T.1 (benign-prompt vulnerability generation), T.6 (credential exposure when secrets back the auth).

## Where this applies

JavaScript and TypeScript (`.js`, `.jsx`, `.ts`, `.tsx`), SQL (`.sql`), and infrastructure code (`.tf`, `.tfvars`, `.hcl`, `.yaml`). The skill loads this file for JavaScript, TypeScript, SQL, and infrastructure.

## Why AI-generated code hits this

The prompt describes the feature, not its guard. "Add an endpoint that deletes a user" produces a delete endpoint. The authorization check is implied by the domain, not stated, so it is omitted. Plaintext credential handling wins over a slow salted hash because it is one line shorter.

## BAD

```javascript
// Missing authorization. Any logged-in user deletes any account.
app.delete("/users/:id", requireLogin, (req, res) => {
  db.deleteUser(req.params.id);
  res.sendStatus(204);
});
```

`requireLogin` proves who you are. Nothing proves you may delete this id.

```javascript
// Plaintext credential comparison.
if (user.password === req.body.password) grantSession(user);
```

```javascript
// Session fixation. The pre-login session id survives authentication.
req.session.user = user;
```

## GOOD

```javascript
// Authorize the action, not just the identity.
app.delete("/users/:id", requireLogin, (req, res) => {
  if (req.user.id !== req.params.id && !req.user.isAdmin)
    return res.sendStatus(403);
  db.deleteUser(req.params.id);
  res.sendStatus(204);
});
```

```javascript
// Slow salted hash, constant-time verify.
const ok = await argon2.verify(user.passwordHash, req.body.password);
```

```javascript
// Rotate the session id on privilege change.
req.session.regenerate(() => { req.session.user = user; });
```

## Common wrong fix

Hiding the endpoint or relying on an unguessable URL is not access control. Checking authentication and calling that authorization is the most common error: identity is not permission. The fix is an explicit authorization decision on every protected path, evaluated server side against the acting principal and the target object.

## Detection limits

Missing authorization is usually not statically detectable, because the absent check has no syntax. Semgrep catches weak hashing, missing CSRF middleware, and some plaintext comparisons. This pattern is therefore primarily Layer 1 guidance: every protected path states who may act on which object, and that decision is in the code, not in the prompt's assumptions.

## Semgrep cross-reference (Layer 2)

In `p/default` and `p/security-audit`, run by the Phase 3 PostToolUse hook:

- `javascript.express.security.audit.express-check-csurf-middleware-usage.express-check-csurf-middleware-usage`
- `generic.secrets.security.detected-generic-api-key.detected-generic-api-key`
- `python.django.security.audit.unvalidated-password.unvalidated-password`

A hit here is a Layer 2 finding.

## Primary sources

CWE-287, CWE-306, CWE-384, MITRE CWE database (`https://cwe.mitre.org/data/definitions/287.html`). OWASP Authentication and Session Management Cheat Sheets. Pattern selection from the Arcanum-Sec sec-context taxonomy (R.2.2, CC BY 4.0, Jason Haddix, Arcanum Information Security). Methodology from SecureForge (R.2.1, MIT). Content rewritten to repo voice.
