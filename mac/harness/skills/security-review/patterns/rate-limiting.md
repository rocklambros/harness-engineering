# Missing Rate Limiting

A resource-intensive or security-sensitive endpoint accepts unlimited requests. The model implements the operation and not the budget around it, because the prompt asked for the feature, not the abuse case.

**CWE:** CWE-770 (Allocation of Resources Without Limits or Throttling), CWE-307 (Improper Restriction of Excessive Authentication Attempts)
**Severity:** Medium to High. Credential stuffing and brute force against auth, denial of service and cost amplification against expensive endpoints.
**Threats:** T.1 (benign-prompt vulnerability generation).

## Where this applies

Matched by content heuristic, not extension: request handlers, API endpoints, login and token routes, password reset, anything that calls a paid downstream or does heavy work. The skill loads this file alongside file-upload and data-exposure when endpoint code is touched.

## Why AI-generated code hits this

A login handler that checks the password is a complete answer to "add login." The lockout, the per-IP budget, and the per-account budget are abuse controls the prompt did not mention, so they are absent. The endpoint works perfectly for one caller and fails the moment someone scripts it.

## BAD

```javascript
// Unlimited login attempts. Credential stuffing has no cost.
app.post("/login", async (req, res) => {
  const ok = await verify(req.body.user, req.body.pass);
  res.sendStatus(ok ? 200 : 401);
});
```

```python
# Expensive endpoint with no budget. Each call fans out to a paid API.
@app.post("/summarize")
def summarize():
    return llm.summarize(request.json["text"])  # unbounded calls, unbounded cost
```

## GOOD

```javascript
// Per-IP and per-account budget on the auth path.
const limiter = rateLimit({ windowMs: 60_000, max: 5,
  keyGenerator: req => req.ip + ":" + req.body.user });
app.post("/login", limiter, async (req, res) => { /* ... */ });
```

```python
# Token-bucket budget on the expensive path, keyed to the principal.
@app.post("/summarize")
@limit("20/minute", key=current_principal)
def summarize():
    return llm.summarize(request.json["text"])
```

## Common wrong fix

A client-side throttle or a UI disable is not rate limiting, because the attacker does not use the UI. A single global counter is also wrong: it lets one caller starve everyone and lets a distributed caller slip under the global ceiling. The limit is enforced server side and keyed to the right principal, IP plus account for auth, the billing principal for cost.

## Detection limits

The absent limiter has no syntax, so Semgrep cannot see it. Some rulesets flag a login route with no recognized limiter middleware, but coverage is partial and framework specific. This pattern is primarily Layer 1: every authentication path and every expensive or paid path declares an explicit budget and the key it is enforced on.

## Semgrep cross-reference (Layer 2)

In `p/security-audit`, run by the Phase 3 PostToolUse hook, where applicable:

- `javascript.express.security.audit.express-rate-limit.missing-rate-limit`
- `python.flask.security.audit.flask-missing-rate-limit.flask-missing-rate-limit`

Coverage is partial. Treat a clean scan as insufficient evidence that the budget exists.

## Primary sources

CWE-770, CWE-307, MITRE CWE database (`https://cwe.mitre.org/data/definitions/770.html`, `/307.html`). OWASP Denial of Service and Credential Stuffing Prevention Cheat Sheets. Pattern selection from the Arcanum-Sec sec-context taxonomy (R.2.2, CC BY 4.0, Jason Haddix, Arcanum Information Security). Methodology from SecureForge (R.2.1, MIT). Content rewritten to repo voice.
