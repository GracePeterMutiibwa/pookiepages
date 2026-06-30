# config

## AppConfig

```python
from pookiepages.config import AppConfig

APP = AppConfig(
    secretKey="...",
    pagesDir="pages",
    staticDir="static",
    settingsFile="settings.py",
    routes=[],
    publicConfig={},
    bridge=True,
    loginPage="/auth/login",
)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `secretKey` | `str` | `""` | Flask session encryption key. Required. |
| `pagesDir` | `str` | `"pages"` | Directory containing HTML page files. |
| `staticDir` | `str` | `"static"` | Directory for static assets. |
| `settingsFile` | `str` | `"settings.py"` | File containing DATABASE config. |
| `routes` | `list[str]` | `[]` | Python module paths for dynamic routes and API handlers. |
| `publicConfig` | `dict` | `{}` | Config keys exposed via `window.pkbridge.config`. |
| `bridge` | `bool` | `True` | Enable the `window.pkbridge` JS bridge. |
| `loginPage` | `str` | `"/auth/login"` | Redirect target for unauthenticated requests. |

## BuildConfig

```python
from pookiepages.config import BuildConfig

BUILD = BuildConfig(outputDir="dist", minifyCss=True, minifyJs=True, minifyHtml=False)
```

| Parameter | Type | Default |
|---|---|---|
| `outputDir` | `str` | `"dist"` |
| `minifyCss` | `bool` | `True` |
| `minifyJs` | `bool` | `True` |
| `minifyHtml` | `bool` | `False` |

## DevConfig

```python
from pookiepages.config import DevConfig

DEV = DevConfig(port=8000, host="127.0.0.1", reload=True, apiDocs=True)
```

| Parameter | Type | Default |
|---|---|---|
| `port` | `int` | `8000` |
| `host` | `str` | `"127.0.0.1"` |
| `reload` | `bool` | `True` |
| `apiDocs` | `bool` | `False` |

## AdminConfig

```python
from pookiepages.config import AdminConfig

ADMIN = AdminConfig(path="/admin", title="Admin", enabled=True)
```

| Parameter | Type | Default |
|---|---|---|
| `path` | `str` | `"/admin"` |
| `title` | `str` | `"pookiepages Admin"` |
| `enabled` | `bool` | `True` |
