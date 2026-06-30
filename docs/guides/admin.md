# Admin panel

pookiepages auto-discovers all PookieDB models in your `models/` directory and provides a full CRUD admin interface.

## Create an admin user

```bash
pookiepages admin create
```

Enter the email and password when prompted.

## Access the panel

Visit `/admin` (or your configured `ADMIN.path`). Log in with the admin account you created.

## Exclude a model

```python
from pookiepages.admin import admin
import pookiedb as pk


@admin.exclude
class InternalLog(pk.Model):
    class Meta:
        db_table = "internal_logs"
    message = pk.TextField()
```

`InternalLog` will not appear in the admin panel.

## Configure the admin path

```python
from pookiepages.config import AdminConfig

ADMIN = AdminConfig(
    path="/manage",
    title="My App Admin",
    enabled=True,
)
```
