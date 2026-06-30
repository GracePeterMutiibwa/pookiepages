from __future__ import annotations
from typing import Callable, Any

_signalHandlers: dict[str, list[Callable]] = {
    "signup": [],
    "login": [],
    "logout": [],
    "reset": [],
    "passwordChange": [],
}


def _on(event: str):
    def decorator(handler: Callable):
        if event in _signalHandlers:
            _signalHandlers[event].append(handler)
        return handler
    return decorator


def _dispatch(event: str, **kwargs):
    for handler in _signalHandlers.get(event, []):
        try:
            handler(**kwargs)
        except Exception:
            pass


onSignup = _on("signup")
onLogin = _on("login")
onLogout = _on("logout")
onReset = _on("reset")
onPasswordChange = _on("passwordChange")
