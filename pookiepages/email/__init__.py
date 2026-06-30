from __future__ import annotations
from typing import Any
from pookiepages.exceptions import PookiePagesError

_activeBackend: Any = None


def configureEmail(backend: Any):
    global _activeBackend
    _activeBackend = backend


async def sendMail(
    to: str | list[str],
    subject: str,
    body: str,
    html: str | None = None,
    replyTo: str | None = None,
):
    if _activeBackend is None:
        raise PookiePagesError(
            "Email sending failed. No email backend is configured. "
            "Set EMAIL in your settings.py using SMTPEmailBackend or ProviderEmailBackend."
        )

    from pookiepages.email.backends import ProviderEmailBackend, SMTPEmailBackend

    if isinstance(_activeBackend, ProviderEmailBackend):
        await _activeBackend.send(to=to, subject=subject, body=body, html=html, replyTo=replyTo)
    elif isinstance(_activeBackend, SMTPEmailBackend):
        _activeBackend.send(to=to, subject=subject, body=body, html=html, replyTo=replyTo)
    else:
        await _activeBackend.send(to=to, subject=subject, body=body, html=html, replyTo=replyTo)
