# pookiepages

A Python web framework built on Flask and PookieDB. File-based routing, typed APIs, built-in auth, admin panel, AI providers, vector search, and transactional email out of the box.

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation Status](https://readthedocs.org/projects/pookiepages/badge/?version=latest)](https://pookiepages.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://img.shields.io/pypi/v/pookiepages.svg)](https://pypi.org/project/pookiepages/)

## Quick start

```bash
pip install pookiepages
pookiepages init
pookiepages run
```

## Features

- File-based routing: `pages/index.html` becomes `/`, `pages/about.html` becomes `/about`
- Typed API routes with automatic Pydantic v2 validation
- Built-in local auth and OAuth (Google, GitHub) via Authlib
- Auto-discovered admin panel with Bootstrap 5 (no CDN)
- AES-256-GCM database encryption, ChaCha20-Poly1305, or AES-256-CBC
- Transactional email via SMTP or REST providers (Brevo, Mailgun, Resend, Postmark, SendGrid)
- AI completions and embeddings via any OpenAI-compatible API
- Vector search via zvec
- Cloud file storage: S3, Cloudflare R2, or local disk
- CSS and JS minification pipeline
- Frontend bridge: `window.pkbridge` served as `/pkbridge.js`
- CLI: `pookiepages init`, `pookiepages run`, `pookiepages build`, and more

## Documentation

- [Getting started](https://pookiepages.readthedocs.io/en/latest/getting-started/installation/)
- [Configuration reference](https://pookiepages.readthedocs.io/en/latest/getting-started/configuration/)
- [Routing](https://pookiepages.readthedocs.io/en/latest/guides/routing/)
- [Database](https://pookiepages.readthedocs.io/en/latest/guides/database/)
- [Auth](https://pookiepages.readthedocs.io/en/latest/guides/auth/)
- [Email](https://pookiepages.readthedocs.io/en/latest/guides/email/)
- [AI and embeddings](https://pookiepages.readthedocs.io/en/latest/guides/ai/)
- [Vector search](https://pookiepages.readthedocs.io/en/latest/guides/vector-search/)
- [File uploads](https://pookiepages.readthedocs.io/en/latest/guides/file-uploads/)
- [Admin panel](https://pookiepages.readthedocs.io/en/latest/guides/admin/)
- [Asset pipeline](https://pookiepages.readthedocs.io/en/latest/guides/assets/)
- [API reference](https://pookiepages.readthedocs.io/en/latest/api-reference/config/)

## License

MIT. See [LICENSE](LICENSE) for details.
