from __future__ import annotations
import json
from typing import Any
from flask import Flask, session as flaskSession, Response


_BRIDGE_JS = """\
(function() {
  'use strict';
  var _data = window.__pkbridgeData || {};
  var _user = _data.user || null;
  var _csrf = _data.csrf || '';
  var _config = _data.config || {};

  function pkFetch(url, options) {
    options = options || {};
    var method = (options.method || 'GET').toUpperCase();
    var mutating = ['POST', 'PUT', 'PATCH', 'DELETE'];
    if (mutating.indexOf(method) !== -1) {
      options.headers = options.headers || {};
      options.headers['X-CSRF-Token'] = _csrf;
      if (!options.headers['Content-Type'] && !(options.body instanceof FormData)) {
        options.headers['Content-Type'] = 'application/json';
      }
    }
    return fetch(url, options);
  }

  window.pkbridge = {
    user: _user,
    csrf: _csrf,
    config: _config,
    fetch: pkFetch
  };
})();
"""


def _generateCsrfToken() -> str:
    import secrets
    token = flaskSession.get("pp_csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        flaskSession["pp_csrf_token"] = token
    return token


def _buildDataScript(app: Flask, user: Any | None) -> str:
    appConfig = app.config.get("PP_APP")

    if user is not None:
        userData = {
            "id": getattr(user, "id", None),
            "email": getattr(user, "email", None),
            "username": getattr(user, "username", None),
        }
    else:
        userData = None

    try:
        csrfToken = _generateCsrfToken()
    except RuntimeError:
        csrfToken = ""

    publicConfig = {}
    if appConfig and appConfig.publicConfig:
        publicConfig = dict(appConfig.publicConfig)

    dataPayload = json.dumps({"user": userData, "csrf": csrfToken, "config": publicConfig})
    return f"<script>window.__pkbridgeData = {dataPayload};</script>"


def registerBridgeRoute(app: Flask):
    @app.route("/pkbridge.js")
    def pkbridgeJs():
        return Response(_BRIDGE_JS, mimetype="application/javascript")


def injectBridgeIntoHtml(html: str, app: Flask, user: Any | None = None) -> str:
    appConfig = app.config.get("PP_APP")
    if appConfig and not appConfig.bridge:
        return html

    dataScript = _buildDataScript(app, user)
    loaderScript = '<script src="/pkbridge.js"></script>'
    injection = dataScript + "\n" + loaderScript + "\n"

    bodyClose = html.lower().rfind("</body>")
    if bodyClose != -1:
        return html[:bodyClose] + injection + html[bodyClose:]

    return html + injection


def injectBridge(file_path: str, app: Flask) -> str:
    with open(file_path, "r", encoding="utf-8") as htmlFile:
        html = htmlFile.read()

    user = None
    try:
        userId = flaskSession.get("pp_user_id")
        if userId:
            from pookiepages.database.tables import PpUser
            user = PpUser.objects.get(id=userId)
    except Exception:
        pass

    return injectBridgeIntoHtml(html, app, user)
