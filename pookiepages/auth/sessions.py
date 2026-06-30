from __future__ import annotations
import secrets
from datetime import datetime, timezone, timedelta
from typing import Any
from pookiepages.exceptions import PookiePagesError


SESSION_EXPIRY_HOURS = 24 * 7


def createSession(user_id: int) -> str:
    from pookiepages.database.tables import PpSession
    token = secrets.token_urlsafe(48)
    expiresAt = datetime.now(timezone.utc) + timedelta(hours=SESSION_EXPIRY_HOURS)
    PpSession.objects.create(
        token=token,
        userId=user_id,
        expiresAt=expiresAt,
    )
    return token


def getSession(token: str) -> Any | None:
    from pookiepages.database.tables import PpSession
    try:
        session = PpSession.objects.get(token=token)
        if session.expiresAt and datetime.now(timezone.utc) > session.expiresAt.replace(tzinfo=timezone.utc):
            session.delete()
            return None
        return session
    except Exception:
        return None


def destroySession(token: str):
    from pookiepages.database.tables import PpSession
    try:
        session = PpSession.objects.get(token=token)
        session.delete()
    except Exception:
        pass
