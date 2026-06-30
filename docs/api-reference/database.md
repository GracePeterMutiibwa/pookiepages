# database

## DatabaseConfig

```python
from pookiepages.database import DatabaseConfig

DATABASE = DatabaseConfig(
    url="sqlite:///myapp.db",
    encryptionKey=None,      # optional: set your own key
    encryptionAlgorithm="AES_256_GCM",  # default
    alias="default",
)
```

## PostgresConfig

```python
from pookiepages.database import PostgresConfig

DATABASE = PostgresConfig(
    host="localhost",
    port=5432,
    name="mydb",
    user="postgres",
    password="secret",
    alias="default",
)
```

`PostgresConfig.toUrl()` returns `postgresql://user:password@host:port/name`.

## Encryption algorithms

| Value | Algorithm |
|---|---|
| `"AES_256_GCM"` | AES-256-GCM (default, authenticated) |
| `"CHACHA20_POLY1305"` | ChaCha20-Poly1305 (authenticated) |
| `"AES_256_CBC"` | AES-256-CBC with PKCS7 padding |

## Key management

Key resolution order:

1. `DatabaseConfig.encryptionKey` (if set, SHA-256 derived to 32 bytes)
2. `.pookiepages.key` file in project root (auto-loaded)
3. Auto-generate 32-byte key and write to `.pookiepages.key`

`.pookiepages.key` is always gitignored. Never commit it to version control.
