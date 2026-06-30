from __future__ import annotations
import secrets
from datetime import datetime, timezone, timedelta
from functools import wraps
from flask import session as flaskSession, redirect, request as flaskRequest
from pookiepages.response import JsonResponse

ADMIN_SESSION_HOURS = 8


def createAdminSession(user_id: int) -> str:
    from pookiepages.database.tables import PpAdminSession
    token = secrets.token_urlsafe(48)
    expiresAt = datetime.now(timezone.utc) + timedelta(hours=ADMIN_SESSION_HOURS)
    PpAdminSession.objects.create(token=token, userId=user_id, expiresAt=expiresAt)
    return token


def getAdminSession(token: str):
    from pookiepages.database.tables import PpAdminSession
    try:
        session = PpAdminSession.objects.get(token=token)
        if session.expiresAt and datetime.now(timezone.utc) > session.expiresAt.replace(tzinfo=timezone.utc):
            session.delete()
            return None
        return session
    except Exception:
        return None


def destroyAdminSession(token: str):
    from pookiepages.database.tables import PpAdminSession
    try:
        session = PpAdminSession.objects.get(token=token)
        session.delete()
    except Exception:
        pass


def requireAdminAuth(handler):
    @wraps(handler)
    def protectedView(*args, **kwargs):
        token = flaskSession.get("pp_admin_token")
        if not token or not getAdminSession(token):
            return redirect("/admin/login")
        return handler(*args, **kwargs)
    return protectedView
