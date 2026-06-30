from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DatabaseConfig:
    url: str = "sqlite:///pookiepages.db"
    encryptionKey: str = ""
    encryptionAlgorithm: str = "AES_256_GCM"
    alias: str = "default"


@dataclass
class PostgresConfig:
    host: str = "localhost"
    port: int = 5432
    name: str = ""
    user: str = ""
    password: str = ""
    alias: str = "default"

    def toUrl(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
