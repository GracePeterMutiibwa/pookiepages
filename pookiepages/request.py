from __future__ import annotations
from typing import Any, TypeVar, Callable, Type
import flask
import orjson
from pookiepages.exceptions import PookiePagesError

CastType = TypeVar("CastType")


class _QueryParams:
    def __init__(self, params: Any):
        self._params = params

    def get(self, key: str, default: Any = None, cast: Callable[[str], CastType] | None = None) -> Any:
        rawValue = self._params.get(key, None)
        if rawValue is None:
            return default
        if cast is None:
            return rawValue
        try:
            return cast(rawValue)
        except (ValueError, TypeError):
            return default


class Request:
    """Wraps Flask's request proxy. One instance per handler invocation."""

    def __init__(self):
        self._flaskRequest = flask.request
        self._user = None
        self._userLoaded = False

    @property
    def query(self) -> _QueryParams:
        return _QueryParams(self._flaskRequest.args)

    @property
    def body(self) -> Any:
        contentType = self._flaskRequest.content_type or ""
        rawData = self._flaskRequest.get_data()
        if not rawData:
            return {}
        if "application/json" in contentType:
            try:
                return orjson.loads(rawData)
            except Exception as parseErr:
                raise PookiePagesError(
                    f"Request body parsing failed. JSON is malformed: {parseErr}. "
                    f"Check that the request body is valid JSON."
                )
        if "application/x-www-form-urlencoded" in contentType or "multipart/form-data" in contentType:
            return self._flaskRequest.form.to_dict()
        return rawData

    @property
    def files(self) -> Any:
        return self._flaskRequest.files

    @property
    def headers(self) -> Any:
        return self._flaskRequest.headers

    @property
    def method(self) -> str:
        return self._flaskRequest.method

    @property
    def path(self) -> str:
        return self._flaskRequest.path

    @property
    def user(self) -> Any | None:
        if not self._userLoaded:
            self._user = self._loadUser()
            self._userLoaded = True
        return self._user

    def _loadUser(self) -> Any | None:
        from flask import session as flaskSession
        userId = flaskSession.get("pp_user_id")
        if not userId:
            return None
        try:
            from pookiepages.database.tables import PpUser
            return PpUser.objects.get(id=userId)
        except Exception:
            return None

    def render(self, template_path: str, context: dict | None = None) -> str:
        from flask import current_app, render_template
        from pookiepages.bridge import injectBridgeIntoHtml

        ctx = dict(context or {})
        if self.user is not None:
            ctx.setdefault("user", self.user)

        rendered = render_template(template_path, **ctx)
        appConfig = current_app.config.get("PP_APP")

        if appConfig and appConfig.bridge:
            rendered = injectBridgeIntoHtml(rendered, current_app._get_current_object(), self.user)

        return rendered
