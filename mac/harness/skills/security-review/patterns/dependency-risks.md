# Dependency Risks: Slopsquatting and Dependency Confusion

The highest-ranked anti-pattern in the source taxonomy, and the one most specific to AI-generated code. A model under a benign prompt invents a plausible package name that does not exist. An attacker registers that name. The next developer who accepts the suggestion installs attacker-controlled code that runs at install time, before any application logic. Dependency confusion is the sibling failure: an internal package name resolves against a public registry where an attacker has published a higher version, and the resolver prefers it.

**CWE:** CWE-1357 (Reliance on Insufficiently Trustworthy Component), CWE-829 (Inclusion of Functionality from Untrusted Control Sphere)
**Severity:** High. Remote code execution at install time with the developer's or CI runner's privileges.
**Threats:** T.1 (benign-prompt vulnerability generation). Slopsquatting is the cleanest example of T.1 because no malicious prompt is involved, only a confident hallucination.

## Where this applies

Any file that declares or installs dependencies: `requirements.txt`, `pyproject.toml`, `package.json`, `go.mod`, `Gemfile`, Terraform provider blocks, and any `.sh` or `.py` that shells out to `pip`, `npm`, `uv`, `go get`, or `terraform init`. The skill loads this file for Python, JavaScript, TypeScript, and shell.

## Why AI-generated code hits this

Package hallucination is measured, not hypothetical. A model trained on a corpus where `requests`, `numpy`, and `lodash` co-occur will produce a name that fits the distribution but was never published. The name reads correctly because it sits next to real packages in name-space. Plausibility is exactly the attack surface. The failure is invisible in review because the line looks like finished, correct code, and it only fails closed if something checks the registry before the install runs.

## BAD

```python
# Hallucinated package. No such project on PyPI at generation time.
# Whoever registers "requests-oauth-helper" owns this process.
import subprocess
subprocess.run(["pip", "install", "requests-oauth-helper"])
```

The name is plausible because a real adjacent package exists (`requests-oauthlib`). The model interpolated a name from the neighborhood.

```json
{
  "dependencies": {
    "internal-auth-sdk": "*"
  }
}
```

An unscoped internal name with a floating version. If `internal-auth-sdk` is absent from the public registry today, it can appear tomorrow at a higher version, and the resolver takes the attacker's.

```bash
# Unpinned, unverified, executed immediately. Install scripts run as you.
npm install left-pad-utils && node -e "require('left-pad-utils')"
```

## GOOD

```python
# Real, checked project. Exact version. Hash recorded in the lockfile.
# requirements.txt
requests-oauthlib==2.0.0  # verified on PyPI, project URL confirmed
```

Install with `pip install --require-hashes -r requirements.txt`. A substituted artifact fails the hash check and the install aborts.

```json
{
  "dependencies": {
    "@your-org/internal-auth-sdk": "1.4.2"
  }
}
```

The scoped name (`@your-org/`) cannot be claimed on the public registry by an outsider. Dependency confusion is structurally prevented, not detected after the fact.

```bash
# Lockfile-exact install, no implicit code execution.
npm ci --ignore-scripts
```

## Common wrong fix

Pinning the version but not verifying the name still installs a hallucinated package, just a specific version of it. The order matters: confirm the package exists and is the project you mean, then pin, then hash-lock. A blocklist of "known bad" names is useless here because the attacker picks the name after seeing what models hallucinate.

## Detection limits

A hallucinated name is not a syntactic pattern, so Semgrep is weak against this. The deterministic control is the Phase 3 supply-chain pre-tool hook, which blocks unpinned and unverified install invocations (`npx -y`, `uvx --from git+`, `@latest`, unconstrained `pip install`). This pattern is therefore mostly Layer 1 guidance plus the Phase 3 hook, with the lockfile-hash gate as the catch at Layer 3. Treat any model-suggested package as unverified until its registry page and repository have been checked.

## Semgrep cross-reference (Layer 2)

Manifest hygiene rules that do apply, shipped in `p/default` and `p/security-audit`:

- `yaml.github-actions.security.run-shell-injection.run-shell-injection` for install commands built from untrusted CI input
- `generic.ci.security.use-frozen-lockfile.use-frozen-lockfile` for non-frozen installs in CI

## Primary sources

CWE-1357 and CWE-829, MITRE CWE database (`https://cwe.mitre.org/data/definitions/1357.html`, `/829.html`). Slopsquatting as a named, measured failure mode is documented in the SecureForge methodology (R.2.1, arXiv:2605.08382v1, MIT). Pattern selection and the rank-1 placement come from the Arcanum-Sec sec-context taxonomy (R.2.2, CC BY 4.0, Jason Haddix, Arcanum Information Security). Content here is rewritten to repo voice. The taxonomy and ranking are the attributed contribution.
