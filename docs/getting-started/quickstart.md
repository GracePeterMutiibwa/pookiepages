# Quick start

## Start the dev server

```bash
pookiepages run
```

Output:
```
pookiepages: loaded config from pookiepages.config.py
pookiepages: connected to SQLite at app.db
pookiepages: registered 1 file-based routes from pages/
pookiepages: internal tables ready
pookiepages: dev server running at http://127.0.0.1:8000
```

## Add a page

Create `pages/about.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>About</title></head>
<body>
<h1>About page</h1>
</body>
</html>
```

Visit `http://localhost:8000/about`. No restart needed when `DEV.reload=True`.

## Add an API route

In `routes/api.py`:

```python
from pydantic import BaseModel
from pookiepages.api import api
from pookiepages.request import Request
from pookiepages.response import JsonResponse


class CreatePostBody(BaseModel):
    title: str
    content: str


@api.post("/api/posts")
def createPost(req: Request, body: CreatePostBody) -> JsonResponse:
    return JsonResponse({"title": body.title, "content": body.content}, status=201)
```

Register it in `pookiepages.config.py`:

```python
APP = AppConfig(
    secretKey="your-long-random-secret",
    routes=["routes.api"],
)
```
