# Routing

pookiepages supports two kinds of routes: file-based (for HTML pages) and dynamic (for APIs).

## File-based routes

Put HTML files in your `pages/` directory. pookiepages walks it on startup and registers a GET route for each file.

| File | Route |
|---|---|
| `pages/index.html` | `/` |
| `pages/about.html` | `/about` |
| `pages/blog/index.html` | `/blog` |
| `pages/blog/first-post.html` | `/blog/first-post` |

## Dynamic routes

Use `@router.get`, `@router.post`, etc. for routes that run Python code:

```python
from pookiepages.router import router
from pookiepages.request import Request
from pookiepages.response import JsonResponse


@router.get("/health")
def healthCheck(req: Request):
    return JsonResponse({"status": "ok"})
```

List the module in `pookiepages.config.py`:

```python
APP = AppConfig(
    secretKey="...",
    routes=["routes.api"],
)
```

## API routes with Pydantic validation

Use `@api.*` decorators for typed API endpoints. Declare a Pydantic model as a parameter and pookiepages parses and validates the request body automatically.

```python
from pydantic import BaseModel
from pookiepages.api import api
from pookiepages.request import Request
from pookiepages.response import JsonResponse


class CreateUserBody(BaseModel):
    email: str
    name: str


@api.post("/api/users")
def createUser(req: Request, body: CreateUserBody):
    return JsonResponse({"email": body.email, "name": body.name}, status=201)
```

Invalid bodies get a `422` response automatically:

```json
{
  "error": "validation_failed",
  "detail": [{"loc": ["email"], "msg": "field required", "type": "missing"}]
}
```
