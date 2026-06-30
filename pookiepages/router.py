from __future__ import annotations
import os
import importlib
from flask import Flask, send_file, current_app
from pookiepages.config import AppConfig
from pookiepages.exceptions import PookiePagesError

# Registry: maps endpoint name -> (source description, http methods)
_routeRegistry: dict[str, tuple[str, list[str]]] = {}

# Deferred route registrations from @router decorators (before app exists)
_pendingRoutes: list[tuple[str, list[str], callable, str]] = []

# Reference to the active Flask app for decorator-time registration
_activeApp: Flask | None = None


class _Router:
    """Decorator-based dynamic route registrar. Use @router.get, @router.post, etc."""

    def _register(self, path: str, methods: list[str], handler: callable, source: str):
        if _activeApp is not None:
            endpointName = f"dynamic_{handler.__module__}_{handler.__name__}"
            _activeApp.add_url_rule(path, endpoint=endpointName, view_func=handler, methods=methods)
            _routeRegistry[endpointName] = (source, methods)
        else:
            _pendingRoutes.append((path, methods, handler, source))

    def get(self, path: str):
        def decorator(handler: callable):
            self._register(path, ["GET"], handler, f"{handler.__module__}.{handler.__name__}")
            return handler
        return decorator

    def post(self, path: str):
        def decorator(handler: callable):
            self._register(path, ["POST"], handler, f"{handler.__module__}.{handler.__name__}")
            return handler
        return decorator

    def put(self, path: str):
        def decorator(handler: callable):
            self._register(path, ["PUT"], handler, f"{handler.__module__}.{handler.__name__}")
            return handler
        return decorator

    def patch(self, path: str):
        def decorator(handler: callable):
            self._register(path, ["PATCH"], handler, f"{handler.__module__}.{handler.__name__}")
            return handler
        return decorator

    def delete(self, path: str):
        def decorator(handler: callable):
            self._register(path, ["DELETE"], handler, f"{handler.__module__}.{handler.__name__}")
            return handler
        return decorator


router = _Router()


def _deriveUrlPath(pagesDir: str, filePath: str) -> str:
    relative = os.path.relpath(filePath, pagesDir)
    parts = relative.replace("\\", "/").split("/")

    if parts[-1] == "index.html":
        parts = parts[:-1]
        if not parts:
            return "/"
        return "/" + "/".join(parts)

    if parts[-1].endswith(".html"):
        parts[-1] = parts[-1][:-5]

    return "/" + "/".join(parts)


def registerFileRoutes(app: Flask, project_root: str, appConfig: AppConfig):
    pagesDir = os.path.join(project_root, appConfig.pagesDir)
    if not os.path.isdir(pagesDir):
        print(f"pookiepages: pages directory '{appConfig.pagesDir}' not found, skipping file-based routing")
        return

    routeCount = 0
    for dirPath, _, fileNames in os.walk(pagesDir):
        for fileName in fileNames:
            if not fileName.endswith(".html"):
                continue
            fullPath = os.path.join(dirPath, fileName)
            urlPath = _deriveUrlPath(pagesDir, fullPath)

            # Capture for closure
            capturedPath = fullPath
            capturedUrlPath = urlPath

            def makeHandler(filePath: str, routePath: str):
                def fileRouteHandler():
                    from pookiepages.bridge import injectBridge
                    return injectBridge(filePath, current_app._get_current_object())
                fileRouteHandler.__name__ = f"file_route_{routePath.replace('/', '_') or 'index'}"
                return fileRouteHandler

            endpointName = f"file_{urlPath.replace('/', '_') or 'index'}"
            app.add_url_rule(urlPath, endpoint=endpointName, view_func=makeHandler(capturedPath, capturedUrlPath))
            _routeRegistry[endpointName] = (fullPath, ["GET"])
            routeCount += 1

    print(f"pookiepages: registered {routeCount} file-based routes from {appConfig.pagesDir}/")


def registerDynamicRoutes(app: Flask, appConfig: AppConfig):
    global _activeApp
    _activeApp = app

    # Flush pending routes registered before app was ready
    for path, methods, handler, source in _pendingRoutes:
        endpointName = f"dynamic_{handler.__module__}_{handler.__name__}"
        app.add_url_rule(path, endpoint=endpointName, view_func=handler, methods=methods)
        _routeRegistry[endpointName] = (source, methods)
    _pendingRoutes.clear()

    # Now import each route module so their decorators fire
    loadedCount = 0
    for moduleName in appConfig.routes:
        try:
            importlib.import_module(moduleName)
            loadedCount += 1
        except ImportError as importErr:
            raise PookiePagesError(
                f"Dynamic route registration failed for module '{moduleName}'. "
                f"Import error: {importErr}. "
                f"Check that '{moduleName}' is importable and listed correctly in APP.routes."
            )

    if loadedCount:
        routeCount = sum(1 for name in _routeRegistry if name.startswith("dynamic_"))
        print(f"pookiepages: registered {routeCount} API routes from {', '.join(appConfig.routes)}")


def listRoutes() -> list[dict]:
    results = []
    for endpointName, (source, methods) in _routeRegistry.items():
        results.append({"endpoint": endpointName, "source": source, "methods": methods})
    return results
