# Hardcoded Secrets

A credential, API key, token, or private key written into source. The model produces a runnable example, and a runnable example needs a value, so it fills in a literal. The literal ships, lands in git history, and stays valid until someone rotates it. Deleting the line later does not help, because the value is in every clone of the history.

**CWE:** CWE-798 (Use of Hard-coded Credentials), CWE-259 (Use of Hard-coded Password)
**Severity:** High. Blast radius is whatever the credential unlocks. Git history makes deletion insufficient and rotation mandatory.
**Threats:** T.6 (credential and secret exposure in generated code).

## Where this applies

Every language and config format. The skill loads this file for Python, JavaScript, TypeScript, shell, and infrastructure code (`.tf`, `.tfvars`, `.hcl`, `.yaml`). It is the broadest pattern in the set.

The examples below use obvious placeholders, never realistic key material. A security reference that ships a string shaped like a live secret trips every cloner's scanner and risks being mistaken for a real credential. Teaching the anti-pattern does not require a realistic value.

## Why AI-generated code hits this

A working snippet is more satisfying than a placeholder, so a model prefers a literal key over an environment read. Placeholder discipline is learned behavior, not the default. The failure is invisible in review because the line looks like correct, complete code, and the value is often realistic enough to pass a skim.

## BAD

```python
# Credential literal in source. Lands in git history on the first commit.
STRIPE_KEY = "sk_live_PLACEHOLDER_not_a_real_key"
stripe.api_key = STRIPE_KEY
```

```javascript
// Password embedded in a connection string.
const db = new Client({
  connectionString: "postgres://admin:PLACEHOLDER_PW@db.internal:5432/prod",
});
```

```hcl
# Terraform default secret. It is in source, in the state file, and in plan output.
variable "db_password" {
  default = "PLACEHOLDER_REPLACE_AT_APPLY"
}
```

## GOOD

```python
# Read from the environment. Fail closed if it is absent.
import os
stripe.api_key = os.environ["STRIPE_KEY"]  # KeyError beats a silent default
```

```javascript
// No default. Missing config is a startup error, not a fallback.
const url = process.env.DATABASE_URL;
if (!url) throw new Error("DATABASE_URL is required");
const db = new Client({ connectionString: url });
```

```hcl
# No default. Value supplied at apply time from a secrets manager.
variable "db_password" {
  type      = string
  sensitive = true
}
```

When config containing a credential must exist in the repo, commit a template with placeholders and document the retrieval path in the same commit. That rule is in the harness CLAUDE.md, and this pattern is why it is there.

## Common wrong fix

Moving the secret into a committed `.env` file is not a fix. A committed `.env` is a hardcoded secret with extra steps. Base64 or hex encoding the value is not a fix either, because encoding is not encryption. The fix is that the secret never enters version control, in any form.

## Detection limits

Semgrep catches the structural shape (a key-like literal assigned to a credential-named field). gitleaks catches the value by entropy and known prefixes. Neither catches a secret that does not match a known shape, for example a custom internal token format. Layer 1 discipline, never write the literal, is the only control that covers the unknown-format case.

## Semgrep cross-reference (Layer 2)

In `p/default` and `p/security-audit`, run by the Phase 3 PostToolUse hook. gitleaks runs in the pre-commit stack at Layer 3 and blocks the commit on a matched value:

- `generic.secrets.security.detected-generic-api-key.detected-generic-api-key`
- `python.lang.security.audit.hardcoded-password-default-argument.hardcoded-password-default-argument`
- `javascript.lang.security.audit.hardcoded-jwt-secret.hardcoded-jwt-secret`

A secret that reaches commit is a Layer 3 block, not a warning. The skill exists so it is never written in the first place.

## Primary sources

CWE-798 and CWE-259, MITRE CWE database (`https://cwe.mitre.org/data/definitions/798.html`, `/259.html`). OWASP Secrets Management Cheat Sheet. Pattern rank-3 placement from the Arcanum-Sec sec-context taxonomy (R.2.2, CC BY 4.0, Jason Haddix, Arcanum Information Security). The harness secret-handling rule traces to QC.1. Content rewritten to repo voice.
