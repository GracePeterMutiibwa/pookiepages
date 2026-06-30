# bridge

The bridge injects `window.pkbridge` into every rendered HTML page via a two-part mechanism:

1. A data script sets `window.__pkbridgeData = {...}` inline.
2. `<script src="/pkbridge.js"></script>` loads the bridge logic.

## What the bridge exposes

```javascript
window.pkbridge = {
  user: { id, email, username } | null,
  csrf: "token-string",
  config: { /* only APP.publicConfig keys */ },
  fetch: pkFetch,
}
```

`pkbridge.fetch` is a drop-in replacement for `window.fetch` that automatically adds `X-CSRF-Token` and `Content-Type: application/json` headers on mutating requests (POST/PUT/PATCH/DELETE).

## What the bridge never exposes

- Password hashes
- Session tokens
- Encryption keys
- Database connection strings
- Any key not listed in `APP.publicConfig`

## Disable the bridge

```python
APP = AppConfig(secretKey="...", bridge=False)
```

## Direct API

```python
from pookiepages.bridge import injectBridgeIntoHtml

html = injectBridgeIntoHtml(rawHtml, app, user=currentUser)
```
