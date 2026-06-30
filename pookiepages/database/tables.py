from __future__ import annotations
from flask import Flask
import pookiedb as pk
from pookiedb.db.connection import execute


# PookieDB model definitions for internal framework tables.
# These are used for ORM queries throughout the framework.

class PpUser(pk.Model):
    class Meta:
        db_table = "pp_users"

    email = pk.EmailField(unique=True)
    username = pk.CharField(max_length=150, null=True, blank=True)
    passwordHash = pk.TextField(null=True, blank=True)
    isAdmin = pk.BooleanField(default=False)
    isActive = pk.BooleanField(default=True)
    oauthProvider = pk.CharField(max_length=50, null=True, blank=True)
    oauthId = pk.CharField(max_length=255, null=True, blank=True)
    createdAt = pk.DateTimeField(auto_now_add=True)
    updatedAt = pk.DateTimeField(auto_now=True)


class PpSession(pk.Model):
    class Meta:
        db_table = "pp_sessions"

    token = pk.CharField(max_length=255, unique=True)
    userId = pk.IntegerField()
    createdAt = pk.DateTimeField(auto_now_add=True)
    expiresAt = pk.DateTimeField(null=True)


class PpPasswordResetToken(pk.Model):
    class Meta:
        db_table = "pp_password_reset_tokens"

    token = pk.CharField(max_length=255, unique=True)
    userId = pk.IntegerField()
    createdAt = pk.DateTimeField(auto_now_add=True)
    expiresAt = pk.DateTimeField(null=True)
    usedAt = pk.DateTimeField(null=True)


class PpConversation(pk.Model):
    class Meta:
        db_table = "pp_conversations"

    conversationId = pk.CharField(max_length=255)
    role = pk.CharField(max_length=20)
    content = pk.TextField()
    model = pk.CharField(max_length=100, null=True, blank=True)
    createdAt = pk.DateTimeField(auto_now_add=True)


class PpAdminSession(pk.Model):
    class Meta:
        db_table = "pp_admin_sessions"

    token = pk.CharField(max_length=255, unique=True)
    userId = pk.IntegerField()
    createdAt = pk.DateTimeField(auto_now_add=True)
    expiresAt = pk.DateTimeField(null=True)


_CREATE_STATEMENTS_SQLITE = [
    """CREATE TABLE IF NOT EXISTS "pp_users" (
        "id" INTEGER PRIMARY KEY AUTOINCREMENT,
        "email" VARCHAR(254) NOT NULL UNIQUE,
        "username" VARCHAR(150),
        "passwordHash" TEXT,
        "isAdmin" INTEGER NOT NULL DEFAULT 0,
        "isActive" INTEGER NOT NULL DEFAULT 1,
        "oauthProvider" VARCHAR(50),
        "oauthId" VARCHAR(255),
        "createdAt" DATETIME,
        "updatedAt" DATETIME
    )""",
    """CREATE TABLE IF NOT EXISTS "pp_sessions" (
        "id" INTEGER PRIMARY KEY AUTOINCREMENT,
        "token" VARCHAR(255) NOT NULL UNIQUE,
        "userId" INTEGER NOT NULL,
        "createdAt" DATETIME,
        "expiresAt" DATETIME
    )""",
    """CREATE TABLE IF NOT EXISTS "pp_password_reset_tokens" (
        "id" INTEGER PRIMARY KEY AUTOINCREMENT,
        "token" VARCHAR(255) NOT NULL UNIQUE,
        "userId" INTEGER NOT NULL,
        "createdAt" DATETIME,
        "expiresAt" DATETIME,
        "usedAt" DATETIME
    )""",
    """CREATE TABLE IF NOT EXISTS "pp_conversations" (
        "id" INTEGER PRIMARY KEY AUTOINCREMENT,
        "conversationId" VARCHAR(255) NOT NULL,
        "role" VARCHAR(20) NOT NULL,
        "content" TEXT NOT NULL,
        "model" VARCHAR(100),
        "createdAt" DATETIME
    )""",
    """CREATE TABLE IF NOT EXISTS "pp_admin_sessions" (
        "id" INTEGER PRIMARY KEY AUTOINCREMENT,
        "token" VARCHAR(255) NOT NULL UNIQUE,
        "userId" INTEGER NOT NULL,
        "createdAt" DATETIME,
        "expiresAt" DATETIME
    )""",
]

_CREATE_STATEMENTS_POSTGRES = [
    """CREATE TABLE IF NOT EXISTS "pp_users" (
        "id" SERIAL PRIMARY KEY,
        "email" VARCHAR(254) NOT NULL UNIQUE,
        "username" VARCHAR(150),
        "passwordHash" TEXT,
        "isAdmin" BOOLEAN NOT NULL DEFAULT FALSE,
        "isActive" BOOLEAN NOT NULL DEFAULT TRUE,
        "oauthProvider" VARCHAR(50),
        "oauthId" VARCHAR(255),
        "createdAt" TIMESTAMP,
        "updatedAt" TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS "pp_sessions" (
        "id" SERIAL PRIMARY KEY,
        "token" VARCHAR(255) NOT NULL UNIQUE,
        "userId" INTEGER NOT NULL,
        "createdAt" TIMESTAMP,
        "expiresAt" TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS "pp_password_reset_tokens" (
        "id" SERIAL PRIMARY KEY,
        "token" VARCHAR(255) NOT NULL UNIQUE,
        "userId" INTEGER NOT NULL,
        "createdAt" TIMESTAMP,
        "expiresAt" TIMESTAMP,
        "usedAt" TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS "pp_conversations" (
        "id" SERIAL PRIMARY KEY,
        "conversationId" VARCHAR(255) NOT NULL,
        "role" VARCHAR(20) NOT NULL,
        "content" TEXT NOT NULL,
        "model" VARCHAR(100),
        "createdAt" TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS "pp_admin_sessions" (
        "id" SERIAL PRIMARY KEY,
        "token" VARCHAR(255) NOT NULL UNIQUE,
        "userId" INTEGER NOT NULL,
        "createdAt" TIMESTAMP,
        "expiresAt" TIMESTAMP
    )""",
]


def createInternalTables(app: Flask):
    alias = app.config.get("PP_DB_ALIAS", "default")
    if alias not in _getActiveAliases():
        return

    from pookiedb.db.connection import get_connection
    pool = get_connection(alias)
    engine = pool.config.engine

    statements = _CREATE_STATEMENTS_POSTGRES if engine == "postgresql" else _CREATE_STATEMENTS_SQLITE

    for sql in statements:
        execute(sql, alias=alias)

    print("pookiepages: internal tables ready (pp_users, pp_sessions, pp_conversations, pp_admin_sessions)")


def _getActiveAliases() -> set[str]:
    from pookiedb.db.connection import _connections
    return set(_connections.keys())
