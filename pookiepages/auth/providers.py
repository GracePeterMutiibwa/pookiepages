from __future__ import annotations
from functools import wraps
from typing import Any, Callable
from flask import Flask, redirect, request as flaskRequest, session as flaskSession
from pookiepages.auth.config import AuthConfig, GoogleAuthConfig, GithubAuthConfig
from pookiepages.auth.passwords import hashPassword, verifyPassword
from pookiepages.auth.sessions import createSession, getSession, destroySession
from pookiepages.auth.signals import _dispatch
from pookiepages.response import JsonResponse
from pookiepages.exceptions import PookiePagesError


class DefaultAuthProvider:
    def __init__(self, app: Flask, auth_config: AuthConfig | None = None):
        self.app = app
        self.authConfig = auth_config or AuthConfig()
        self._registerRoutes()

    def _registerRoutes(self):
        app = self.app
        authConfig = self.authConfig

        @app.route("/auth/register", methods=["POST"])
        def authRegister():
            from pookiepages.database.tables import PpUser
            import orjson
            data = orjson.loads(flaskRequest.get_data() or b"{}")
            emailAddr = data.get("email", "").strip().lower()
            plainPassword = data.get("password", "")
            username = data.get("username", "")

            if not emailAddr or not plainPassword:
                return JsonResponse({"error": "email and password are required"}, status=400)

            if PpUser.objects.filter(email=emailAddr).exists():
                return JsonResponse({"error": "an account with this email already exists"}, status=409)

            user = PpUser.objects.create(
                email=emailAddr,
                username=username,
                passwordHash=hashPassword(plainPassword),
            )
            _dispatch("signup", user=user)
            token = createSession(user.id)
            flaskSession["pp_user_id"] = user.id
            flaskSession["pp_session_token"] = token
            return JsonResponse({"message": "account created", "userId": user.id}, status=201)

        @app.route("/auth/login", methods=["POST"])
        def authLogin():
            from pookiepages.database.tables import PpUser
            import orjson
            data = orjson.loads(flaskRequest.get_data() or b"{}")
            emailAddr = data.get("email", "").strip().lower()
            plainPassword = data.get("password", "")

            if not emailAddr or not plainPassword:
                return JsonResponse({"error": "email and password are required"}, status=400)

            try:
                user = PpUser.objects.get(email=emailAddr)
            except Exception:
                return JsonResponse({"error": "invalid email or password"}, status=401)

            if not user.passwordHash or not verifyPassword(plainPassword, user.passwordHash):
                return JsonResponse({"error": "invalid email or password"}, status=401)

            if not user.isActive:
                return JsonResponse({"error": "this account has been deactivated"}, status=403)

            token = createSession(user.id)
            flaskSession["pp_user_id"] = user.id
            flaskSession["pp_session_token"] = token
            _dispatch("login", user=user)
            return JsonResponse({"message": "logged in", "userId": user.id})

        @app.route("/auth/logout", methods=["POST"])
        def authLogout():
            token = flaskSession.pop("pp_session_token", None)
            flaskSession.pop("pp_user_id", None)
            if token:
                destroySession(token)
            _dispatch("logout")
            return JsonResponse({"message": "logged out"})

        @app.route("/auth/change-password", methods=["POST"])
        def authChangePassword():
            from pookiepages.database.tables import PpUser
            import orjson
            userId = flaskSession.get("pp_user_id")
            if not userId:
                return JsonResponse({"error": "authentication required"}, status=401)

            data = orjson.loads(flaskRequest.get_data() or b"{}")
            currentPassword = data.get("currentPassword", "")
            newPassword = data.get("newPassword", "")

            try:
                user = PpUser.objects.get(id=userId)
            except Exception:
                return JsonResponse({"error": "user not found"}, status=404)

            if not verifyPassword(currentPassword, user.passwordHash):
                return JsonResponse({"error": "current password is incorrect"}, status=401)

            user.passwordHash = hashPassword(newPassword)
            user.save()
            _dispatch("passwordChange", user=user)
            return JsonResponse({"message": "password changed successfully"})

        @app.route("/auth/reset", methods=["POST"])
        def authReset():
            import orjson
            data = orjson.loads(flaskRequest.get_data() or b"{}")
            emailAddr = data.get("email", "").strip().lower()
            # Always respond OK so as not to leak whether email exists
            return JsonResponse({"message": "if that email exists, a reset link has been sent"})


def requireAuth(handler: Callable) -> Callable:
    @wraps(handler)
    def protectedHandler(*args, **kwargs):
        userId = flaskSession.get("pp_user_id")
        if not userId:
            if flaskRequest.content_type and "application/json" in flaskRequest.content_type:
                return JsonResponse({"error": "authentication required"}, status=401)
            from flask import current_app
            loginPage = current_app.config.get("PP_APP").loginPage
            return redirect(loginPage)
        return handler(*args, **kwargs)
    return protectedHandler


class GoogleAuthProvider:
    def __init__(self, app: Flask, config: GoogleAuthConfig):
        self.app = app
        self.config = config
        self._registerRoutes()

    def _registerRoutes(self):
        from authlib.integrations.requests_client import OAuth2Session
        config = self.config
        app = self.app

        @app.route("/auth/google/login")
        def googleLogin():
            oauthClient = OAuth2Session(
                client_id=config.clientId,
                redirect_uri=flaskRequest.host_url.rstrip("/") + "/auth/google/callback",
                scope="openid email profile",
            )
            authorizationUrl, state = oauthClient.create_authorization_url(
                "https://accounts.google.com/o/oauth2/v2/auth"
            )
            flaskSession["pp_oauth_state"] = state
            return redirect(authorizationUrl)

        @app.route("/auth/google/callback")
        def googleCallback():
            from pookiepages.database.tables import PpUser
            state = flaskSession.pop("pp_oauth_state", "")
            oauthClient = OAuth2Session(
                client_id=config.clientId,
                client_secret=config.clientSecret,
                state=state,
                redirect_uri=flaskRequest.host_url.rstrip("/") + "/auth/google/callback",
            )
            try:
                oauthClient.fetch_token(
                    "https://oauth2.googleapis.com/token",
                    authorization_response=flaskRequest.url,
                )
                userInfo = oauthClient.get("https://www.googleapis.com/oauth2/v3/userinfo").json()
            except Exception as oauthErr:
                return JsonResponse({"error": f"Google OAuth failed: {oauthErr}"}, status=400)

            email = userInfo.get("email", "").lower()
            if config.allowedDomains:
                domain = email.split("@")[-1]
                if domain not in config.allowedDomains:
                    return JsonResponse({"error": f"email domain '{domain}' is not allowed"}, status=403)

            try:
                user = PpUser.objects.get(email=email)
            except Exception:
                user = PpUser.objects.create(
                    email=email,
                    username=userInfo.get("name", ""),
                    oauthProvider="google",
                    oauthId=userInfo.get("sub", ""),
                )
                _dispatch("signup", user=user)

            token = createSession(user.id)
            flaskSession["pp_user_id"] = user.id
            flaskSession["pp_session_token"] = token
            _dispatch("login", user=user)

            from flask import current_app
            redirectTo = current_app.config.get("PP_APP").loginPage.replace("/auth/login", "/")
            return redirect("/")


class GithubAuthProvider:
    def __init__(self, app: Flask, config: GithubAuthConfig):
        self.app = app
        self.config = config
        self._registerRoutes()

    def _registerRoutes(self):
        from authlib.integrations.requests_client import OAuth2Session
        config = self.config
        app = self.app

        @app.route("/auth/github/login")
        def githubLogin():
            oauthClient = OAuth2Session(
                client_id=config.clientId,
                redirect_uri=flaskRequest.host_url.rstrip("/") + "/auth/github/callback",
                scope="user:email",
            )
            authorizationUrl, state = oauthClient.create_authorization_url(
                "https://github.com/login/oauth/authorize"
            )
            flaskSession["pp_oauth_state"] = state
            return redirect(authorizationUrl)

        @app.route("/auth/github/callback")
        def githubCallback():
            from pookiepages.database.tables import PpUser
            state = flaskSession.pop("pp_oauth_state", "")
            oauthClient = OAuth2Session(
                client_id=config.clientId,
                client_secret=config.clientSecret,
                state=state,
                redirect_uri=flaskRequest.host_url.rstrip("/") + "/auth/github/callback",
            )
            try:
                oauthClient.fetch_token(
                    "https://github.com/login/oauth/access_token",
                    authorization_response=flaskRequest.url,
                )
                userInfo = oauthClient.get("https://api.github.com/user").json()
                emails = oauthClient.get("https://api.github.com/user/emails").json()
            except Exception as oauthErr:
                return JsonResponse({"error": f"GitHub OAuth failed: {oauthErr}"}, status=400)

            primaryEmail = next(
                (item["email"] for item in emails if item.get("primary")),
                userInfo.get("email", ""),
            )
            email = primaryEmail.lower()

            if config.allowedDomains:
                domain = email.split("@")[-1]
                if domain not in config.allowedDomains:
                    return JsonResponse({"error": f"email domain '{domain}' is not allowed"}, status=403)

            try:
                user = PpUser.objects.get(email=email)
            except Exception:
                user = PpUser.objects.create(
                    email=email,
                    username=userInfo.get("login", ""),
                    oauthProvider="github",
                    oauthId=str(userInfo.get("id", "")),
                )
                _dispatch("signup", user=user)

            token = createSession(user.id)
            flaskSession["pp_user_id"] = user.id
            flaskSession["pp_session_token"] = token
            _dispatch("login", user=user)
            return redirect("/")
