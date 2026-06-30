# request

## Request

The `Request` object is passed as the first argument to every route handler.

```python
from pookiepages.request import Request

def myView(req: Request):
    ...
```

### Properties

| Property | Type | Description |
|---|---|---|
| `req.method` | `str` | HTTP method in uppercase. |
| `req.path` | `str` | URL path of the request. |
| `req.headers` | `dict` | Request headers. |
| `req.user` | `PpUser or None` | Authenticated user from session, or None. |
| `req.query` | `_QueryParams` | URL query parameter accessor. |
| `req.body` | `dict` | Parsed request body (JSON or form data). |
| `req.files` | `dict` | Uploaded files from multipart form. |

### req.query.get

```python
page = req.query.get("page", default=1, cast=int)
name = req.query.get("name", default="")
```

- `cast` must be a callable. Pass `int`, `float`, or a custom function.
- Returns `default` if the key is missing or cast fails.

### req.render

```python
return req.render("blog/post.html", {"post": post, "author": author})
```

Renders a Jinja2 template from `APP.pagesDir`. The current user is injected automatically as `user`.
