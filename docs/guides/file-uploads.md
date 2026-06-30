# File uploads

## Configure allowed types

```python
from pookiepages.files import FileConfig

fileConfig = FileConfig(
    allowedTypes=["image/jpeg", "image/png", "image/webp"],
    maxSizeMb=5.0,
)
```

## Handle upload in a route

```python
from pookiepages.router import router
from pookiepages.files import UploadedFile, FileConfig
from pookiepages.response import JsonResponse
from pookiepages.request import Request

config = FileConfig(allowedTypes=["image/jpeg", "image/png"], maxSizeMb=5.0)


@router.post("/upload")
async def uploadFile(req: Request):
    fileStorage = req.files.get("file")
    if not fileStorage:
        return JsonResponse({"error": "no file provided"}, status=400)

    uploaded = UploadedFile(fileStorage, config)
    uploaded.validate()

    saved = await uploaded.save(resize=(800, 600), thumbnail=(128, 128))
    return JsonResponse({"url": saved.url, "thumbnailUrl": saved.thumbnailUrl})
```

## Storage backends

```python
# Local storage (default)
from pookiepages.storage import LocalStorage

# S3 compatible
from pookiepages.storage import S3Storage

storage = S3Storage(
    bucket="my-bucket",
    accessKey="key",
    secretKey="secret",
    region="us-east-1",
)

# Cloudflare R2
from pookiepages.storage import R2Storage

storage = R2Storage(
    accountId="your-account-id",
    bucket="my-bucket",
    accessKey="key",
    secretKey="secret",
    publicUrl="https://cdn.yourapp.com",
)
```
