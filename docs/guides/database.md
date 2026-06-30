# Database

pookiepages uses PookieDB for its ORM and database layer.

## Configure the database

In `settings.py`:

```python
from pookiepages.database import DatabaseConfig

DATABASE = DatabaseConfig(url="sqlite:///myapp.db")
```

For PostgreSQL:

```python
from pookiepages.database import PostgresConfig

DATABASE = PostgresConfig(
    host="localhost",
    port=5432,
    name="mydb",
    user="postgres",
    password="secret",
)
```

## Define models

Create files in `models/`:

```python
import pookiedb as pk


class Post(pk.Model):
    class Meta:
        db_table = "posts"

    title = pk.CharField(max_length=200)
    content = pk.TextField()
    published = pk.BooleanField(default=False)
    createdAt = pk.DateTimeField(auto_now_add=True)
```

## Migrations

```bash
pookiepages migrate --make   # generate migration files
pookiepages migrate          # apply pending migrations
pookiepages migrate --show   # list all migrations
pookiepages migrate --rollback --steps 1  # roll back last migration
```

## Encryption

Enable database encryption in `settings.py`:

```python
from pookiepages.database import DatabaseConfig
from pookiepages.database.encryption import EncryptionAlgorithm

DATABASE = DatabaseConfig(
    url="sqlite:///myapp.db",
    encryptionAlgorithm="AES_256_GCM",  # default
)
```

pookiepages auto-generates a key and stores it in `.pookiepages.key` (already gitignored). To use your own key, set `encryptionKey` in `DatabaseConfig`.

Available algorithms: `AES_256_GCM` (default), `CHACHA20_POLY1305`, `AES_256_CBC`.
