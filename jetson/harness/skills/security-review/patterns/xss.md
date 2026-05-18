# Cross-Site Scripting (XSS)

Untrusted data reaches a browser as executable markup or script. The model produces a template or DOM write that interpolates a value without context-correct encoding. The value looks like a string. In a browser it becomes code.

**CWE:** CWE-79 (Improper Neutralization of Input During Web Page Generation)
**Severity:** High. Session theft, credential capture, request forgery in the victim's authenticated context.
**Threats:** T.1 (benign-prompt vulnerability generation).

## Where this applies

JavaScript and TypeScript (`.js`, `.jsx`, `.ts`, `.tsx`), server templates rendered from those stacks, and any HTML-producing Python or Go view. The skill loads this file for JavaScript and TypeScript.

## The three variants

Reflected: input echoed straight back in the response. Stored: input persisted, then served to other users. DOM-based: a client-side script writes attacker data into a sink with no server round trip. Encoding has to match the sink. HTML-body encoding does not protect a JavaScript or URL context, so the question is always "encoded for which context."

## Why AI-generated code hits this

The unsafe HTML-injection sinks are the shortest path to a working UI, so they are overrepresented in training data. The model reaches for them. React's raw-HTML prop and Vue's `v-html` carry the danger in their names, yet they appear whenever the prompt asks to render server-supplied HTML and says nothing about trust.

## BAD

```javascript
// DOM-based XSS. Anything in ?msg= is parsed as markup and executes.
const msg = new URLSearchParams(location.search).get("msg");
document.getElementById("out").innerHTML = msg;
```

A `msg` value carrying an `onerror` image payload runs script in the page origin.

```jsx
// Stored XSS. comment.body came from another user. React escaping is opted out.
function Comment({ comment }) {
  return <div dangerouslySetInnerHTML={{ __html: comment.body }} />;
}
```

```python
# Reflected XSS. Flask response built by string concatenation, no autoescape.
@app.route("/hello")
def hello():
    return "<h1>Hello " + request.args.get("name", "") + "</h1>"
```

## GOOD

```javascript
// textContent never parses markup. The string stays a string.
const msg = new URLSearchParams(location.search).get("msg");
document.getElementById("out").textContent = msg;
```

```jsx
// Default JSX interpolation is context-aware and escapes.
function Comment({ comment }) {
  return <div>{comment.body}</div>;
}
```

```python
# Jinja2 autoescaping on. The template encodes for HTML context.
@app.route("/hello")
def hello():
    return render_template("hello.html", name=request.args.get("name", ""))
```

If rich text is a genuine requirement, sanitize with a maintained library such as DOMPurify and render the sanitized output, never the raw input.

## Common wrong fix

Blocklisting `<script>` is not a fix. XSS has hundreds of vectors: event handlers, `javascript:` URLs, SVG, CSS expressions, mutation XSS. Stripping one tag leaves the rest. Encoding for HTML body and then placing the value in an attribute or a URL is also wrong, because the context did not match. The fix is context-correct output encoding by default, plus a sanitizer for the rare rich-text case.

## Detection limits

Semgrep reliably flags the named dangerous sinks and autoescape-off. It does not track a tainted value across files into a hand-rolled DOM write, so a sink fed indirectly can pass static analysis. Layer 1 guidance covers the indirect case: treat any value that originated outside the program as unencoded until it has been encoded for its exact sink.

## Semgrep cross-reference (Layer 2)

In `p/default` and `p/security-audit`, run by the Phase 3 PostToolUse hook:

- `javascript.browser.security.insecure-document-method.insecure-document-method`
- `typescript.react.security.audit.react-dangerouslysetinnerhtml.react-dangerouslysetinnerhtml`
- `python.flask.security.xss.audit.template-autoescape-off.template-autoescape-off`

A hit on any of these in a touched file is a Layer 2 finding. Fix in the same session.

## Primary sources

CWE-79, MITRE CWE database (`https://cwe.mitre.org/data/definitions/79.html`). OWASP Cross-Site Scripting Prevention Cheat Sheet for the context-encoding rule. Pattern rank-2 placement from the Arcanum-Sec sec-context taxonomy (R.2.2, CC BY 4.0, Jason Haddix, Arcanum Information Security). The in-session static-analysis feedback method is from SecureForge (R.2.1, MIT). Content rewritten to repo voice.
