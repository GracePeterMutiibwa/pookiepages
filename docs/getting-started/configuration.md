# Configuration

pookiepages is configured via `pookiepages.config.py` in your project root.

## Minimal config

```python
from pookiepages.config import AppConfig

APP = AppConfig(secretKey="your-long-random-secret")
```

## Full AppConfig reference

| Field | Type | Default | Description |
|---|---|---|---|
| `secretKey` | `str` | `""` | Flask session secret. Required. |
| `pagesDir` | `str` | `"pages"` | Directory for HTML page files. |
| `staticDir` | `str` | `"static"` | Directory for static assets. |
| `settingsFile` | `str` | `"settings.py"` | File containing DATABASE config. |
| `routes` | `list[str]` | `[]` | Python module paths for dynamic routes. |
| `publicConfig` | `dict` | `{}` | Keys exposed to the frontend via `window.pkbridge.config`. |
| `bridge` | `bool` | `True` | Enable the `window.pkbridge` frontend bridge. |
| `loginPage` | `str` | `"/auth/login"` | Redirect destination for unauthenticated users. |

## BuildConfig

```python
from pookiepages.config import BuildConfig

BUILD = BuildConfig(
    outputDir="dist",
    minifyCss=True,
    minifyJs=True,
    minifyHtml=False,
)
```

## DevConfig

```python
from pookiepages.config import DevConfig

DEV = DevConfig(
    port=8000,
    host="127.0.0.1",
    reload=True,
    apiDocs=True,
)
```

## AdminConfig

```python
from pookiepages.config import AdminConfig

ADMIN = AdminConfig(
    path="/admin",
    title="My App Admin",
    enabled=True,
)
```
