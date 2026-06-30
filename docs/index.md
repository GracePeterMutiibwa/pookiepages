# pookiepages

**pookiepages** is a Python web framework built on Flask and PookieDB. It gives you file-based routing, typed APIs, built-in auth, admin panel, AI providers, vector search, and transactional email out of the box.

## Features

- File-based routing: `pages/index.html` becomes `/`, `pages/about.html` becomes `/about`
- Typed API routes with automatic Pydantic validation
- Built-in local auth and OAuth (Google, GitHub)
- Auto-discovered admin panel with Bootstrap 5
- AES-256-GCM database encryption (default), ChaCha20-Poly1305, AES-256-CBC
- Transactional email via SMTP or REST providers (Brevo, Mailgun, Resend, Postmark, SendGrid)
- AI completion and embedding via any OpenAI-compatible API
- Vector search via zvec
- Cloud file storage (S3, Cloudflare R2, local)
- Asset minification pipeline for CSS and JS
- Frontend bridge: `window.pkbridge` served as `/pkbridge.js`
- CLI: `pookiepages init`, `pookiepages run`, `pookiepages build`, and more

## Quick start

```bash
pip install pookiepages
pookiepages init
cd my-project
pookiepages run
```

Visit `http://localhost:8000` to see your project.
