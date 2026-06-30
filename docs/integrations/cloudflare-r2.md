# Cloudflare R2

```python
from pookiepages.storage import R2Storage

storage = R2Storage(
    accountId="your-account-id",
    bucket="my-uploads",
    accessKey="your-access-key-id",
    secretKey="your-secret-access-key",
    publicUrl="https://cdn.yourapp.com",
)
```

`R2Storage` automatically sets the endpoint to `https://{accountId}.r2.cloudflarestorage.com`. All other behavior is identical to `S3Storage`.

## Serving uploads

Set `publicUrl` to your R2 custom domain or the public bucket URL. The `SavedFile.url` returned from `storage.save()` will use this URL.
