# auth

## requireAuth

```python
from pookiepages.auth import requireAuth

@router.get("/dashboard")
@requireAuth
def dashboard(req: Request):
    return req.render("dashboard.html", {"user": req.user})
```

For page requests: redirects to `APP.loginPage`.
For API requests (`Accept: application/json` or `/api/` path): returns `{"error": "unauthenticated"}` with status 401.

## hashPassword / verifyPassword

```python
from pookiepages.auth.passwords import hashPassword, verifyPassword

hashed = hashPassword("my_password")
ok = verifyPassword("my_password", hashed)
```

## createSession / getSession / destroySession

```python
from pookiepages.auth.sessions import createSession, getSession, destroySession

token = createSession(user_id=123)
session = getSession(token)   # returns PpSession or None
destroySession(token)
```

Sessions expire after 7 days.

## Signals

```python
from pookiepages.auth.signals import onSignup, onLogin, onLogout, onReset, onPasswordChange

@onSignup
def welcomeUser(user):
    print(f"New signup: {user.email}")
```
