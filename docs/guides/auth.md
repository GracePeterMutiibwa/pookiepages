# Auth

## Local auth

Wire up local username/password auth:

```python
# in your app factory or route file
from pookiepages.auth import DefaultAuthProvider, AuthConfig

DefaultAuthProvider(app, AuthConfig(
    loginPage="/auth/login",
    redirectAfterLogin="/dashboard",
))
```

This registers:

| Route | Method | Description |
|---|---|---|
| `/auth/register` | POST | Create account |
| `/auth/login` | POST | Log in |
| `/auth/logout` | POST | Log out |
| `/auth/change-password` | POST | Change password |
| `/auth/reset` | POST | Request password reset |

## Protect a route

```python
from pookiepages.auth import requireAuth
from pookiepages.router import router
from pookiepages.request import Request


@router.get("/dashboard")
@requireAuth
def dashboard(req: Request):
    return req.render("dashboard.html", {"user": req.user})
```

Unauthenticated page requests are redirected to `APP.loginPage`. API requests get `401`.

## Auth signals

```python
from pookiepages.auth import onSignup, onLogin

@onSignup
def handleSignup(user):
    print(f"New user: {user.email}")

@onLogin
def handleLogin(user):
    print(f"Login: {user.email}")
```

Available signals: `onSignup`, `onLogin`, `onLogout`, `onReset`, `onPasswordChange`.

## Google OAuth

```python
from pookiepages.auth import GoogleAuthProvider, GoogleAuthConfig

GoogleAuthProvider(app, GoogleAuthConfig(
    clientId="your-client-id",
    clientSecret="your-client-secret",
    allowedDomains=["yourcompany.com"],
))
```

This registers `/auth/google/login` and `/auth/google/callback`.

## GitHub OAuth

```python
from pookiepages.auth import GithubAuthProvider, GithubAuthConfig

GithubAuthProvider(app, GithubAuthConfig(
    clientId="your-client-id",
    clientSecret="your-client-secret",
))
```
