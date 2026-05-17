# SQL Injection

Untrusted input becomes part of a SQL statement instead of staying data. The model concatenates a value into a query string because that is the shortest way to make the example run. The query executes with the application's database privileges.

**CWE:** CWE-89 (Improper Neutralization of Special Elements used in an SQL Command)
**Severity:** High. Full read and often write access to the database, authentication bypass, data exfiltration.
**Threats:** T.1 (benign-prompt vulnerability generation).

## Where this applies

Python (`.py`, `.pyi`) and SQL files (`.sql`). Any code that builds a query from a string. The skill loads this file for Python and SQL.

## Why AI-generated code hits this

String formatting is the most common way queries appear in training data. f-strings, percent formatting, `.format()`, and template literals all read as natural code. Parameterization requires knowing the driver's placeholder style, which the model skips when the prompt does not mention security.

## BAD

```python
# f-string injection. id is request input.
def get_user(conn, id):
    return conn.execute(f"SELECT * FROM users WHERE id = {id}").fetchall()
```

A value of `0 OR 1=1` returns every row. A stacked statement can drop the table.

```python
# ORM escape hatch with raw concatenation. The ORM does not help here.
User.objects.raw("SELECT * FROM users WHERE name = '" + name + "'")
```

```sql
-- Dynamic SQL in a stored procedure built from an unvalidated argument.
EXEC('SELECT * FROM orders WHERE customer = ''' + @customer + '''');
```

## GOOD

```python
# Parameterized. The driver sends data separately from the statement.
def get_user(conn, id):
    return conn.execute("SELECT * FROM users WHERE id = ?", (id,)).fetchall()
```

```python
# ORM used as intended. The ORM parameterizes.
User.objects.filter(name=name)
```

```sql
-- Parameterized procedure. No string building.
CREATE PROCEDURE get_orders @customer INT AS
SELECT * FROM orders WHERE customer = @customer;
```

## Common wrong fix

Escaping quotes by hand is not a fix. Numeric contexts need no quotes, second-order data arrives already stored, and character-set tricks defeat naive escaping. Parameterization is the fix because it removes the value from the statement entirely. An identifier that genuinely cannot be a parameter (a table or column name) is constrained with an allowlist, never escaped.

## Detection limits

Semgrep flags formatted query strings and known raw-execution sinks well. It misses injection that crosses a function boundary or is assembled in steps, and it cannot judge whether an allowlisted identifier path is actually exhaustive. Layer 1 rule: data goes through parameters, identifiers go through an allowlist, and there is no third option.

## Semgrep cross-reference (Layer 2)

In `p/default` and `p/security-audit`, run by the Phase 3 PostToolUse hook:

- `python.sqlalchemy.security.sqlalchemy-execute-raw-query.sqlalchemy-execute-raw-query`
- `python.django.security.injection.sql.sql-injection-using-extra-where.sql-injection-using-extra-where`
- `python.lang.security.audit.formatted-sql-query.formatted-sql-query`

A hit here is a Layer 2 finding. Fix before the commit reaches Layer 3.

## Primary sources

CWE-89, MITRE CWE database (`https://cwe.mitre.org/data/definitions/89.html`). OWASP SQL Injection Prevention Cheat Sheet for the parameterization rule. Pattern rank-4 placement from the Arcanum-Sec sec-context taxonomy (R.2.2, CC BY 4.0, Jason Haddix, Arcanum Information Security). Methodology from SecureForge (R.2.1, MIT). Content rewritten to repo voice.
