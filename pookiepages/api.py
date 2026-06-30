from __future__ import annotations
import inspect
from typing import Any, get_type_hints
from functools import wraps
import orjson
from flask import Flask, request as flaskRequest
from pydantic import BaseModel, ValidationError
from pookiepages.response import JsonResponse
from pookiepages.exceptions import PookiePagesError

# Registry for OpenAPI doc generation
_apiRegistry: list[dict] = []

_activeApp: Flask | None = None
_pendingApiRoutes: list[tuple] = []


class _Api:
    """Decorator-based API route registrar with automatic Pydantic validation."""

    def _register(self, path: str, methods: list[str], handler: callable):
        wrappedHandler = self._wrapHandler(handler, methods)
        source = f"{handler.__module__}.{handler.__name__}"

        _apiRegistry.append({
            "path": path,
            "methods": methods,
            "handler": handler.__name__,
            "module": handler.__module__,
            "source": source,
        })

        if _activeApp is not None:
            endpointName = f"api_{handler.__module__}_{handler.__name__}"
            _activeApp.add_url_rule(path, endpoint=endpointName, view_func=wrappedHandler, methods=methods)
            from pookiepages.router import _routeRegistry
            _routeRegistry[endpointName] = (source, methods)
        else:
            _pendingApiRoutes.append((path, methods, wrappedHandler, handler.__name__, handler.__module__))

    def _wrapHandler(self, handler: callable, methods: list[str]) -> callable:
        sig = inspect.signature(handler)
        hints = {}
        try:
            hints = get_type_hints(handler)
        except Exception:
            pass

        pydanticParam = None
        pydanticParamName = None
        for paramName, param in sig.parameters.items():
            annotation = hints.get(paramName)
            if annotation and inspect.isclass(annotation) and issubclass(annotation, BaseModel):
                pydanticParam = annotation
                pydanticParamName = paramName
                break

        returnAnnotation = hints.get("return")
        returnsModel = (
            returnAnnotation is not None
            and inspect.isclass(returnAnnotation)
            and issubclass(returnAnnotation, BaseModel)
        )

        @wraps(handler)
        def wrappedView(*args, **kwargs):
            from pookiepages.request import Request
            req = Request()

            if pydanticParam and pydanticParamName:
                rawBody = flaskRequest.get_data()
                contentType = flaskRequest.content_type or ""
                if "application/json" in contentType and rawBody:
                    try:
                        bodyDict = orjson.loads(rawBody)
                    except Exception as parseErr:
                        return JsonResponse({"error": "invalid_json", "detail": str(parseErr)}, status=400)
                elif contentType and "form" in contentType:
                    bodyDict = flaskRequest.form.to_dict()
                else:
                    bodyDict = {}

                try:
                    parsedModel = pydanticParam.model_validate(bodyDict)
                    kwargs[pydanticParamName] = parsedModel
                except ValidationError as validationErr:
                    errors = validationErr.errors()
                    return JsonResponse({"error": "validation_failed", "detail": errors}, status=422)

            result = handler(req, **kwargs)

            if returnsModel and isinstance(result, BaseModel):
                return JsonResponse(result.model_dump(), status=200)

            return result

        wrappedView.__name__ = handler.__name__
        return wrappedView

    def get(self, path: str):
        def decorator(handler: callable):
            self._register(path, ["GET"], handler)
            return handler
        return decorator

    def post(self, path: str):
        def decorator(handler: callable):
            self._register(path, ["POST"], handler)
            return handler
        return decorator

    def put(self, path: str):
        def decorator(handler: callable):
            self._register(path, ["PUT"], handler)
            return handler
        return decorator

    def patch(self, path: str):
        def decorator(handler: callable):
            self._register(path, ["PATCH"], handler)
            return handler
        return decorator

    def delete(self, path: str):
        def decorator(handler: callable):
            self._register(path, ["DELETE"], handler)
            return handler
        return decorator


api = _Api()


def flushPendingApiRoutes(app: Flask):
    global _activeApp
    _activeApp = app
    for path, methods, wrappedHandler, handlerName, moduleName in _pendingApiRoutes:
        endpointName = f"api_{moduleName}_{handlerName}"
        app.add_url_rule(path, endpoint=endpointName, view_func=wrappedHandler, methods=methods)
        from pookiepages.router import _routeRegistry
        _routeRegistry[endpointName] = (f"{moduleName}.{handlerName}", methods)
    _pendingApiRoutes.clear()


def getApiRegistry() -> list[dict]:
    return list(_apiRegistry)
