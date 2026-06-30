from __future__ import annotations
from flask import Flask
from pookiepages.response import JsonResponse


def _buildOpenApiSchema(app: Flask) -> dict:
    from pookiepages.api import getApiRegistry

    routes = getApiRegistry()
    paths: dict = {}

    for route in routes:
        path = route["path"]
        methods = route["methods"]
        operationId = f"{route['module']}_{route['handler']}"

        if path not in paths:
            paths[path] = {}

        for method in methods:
            paths[path][method.lower()] = {
                "operationId": operationId,
                "summary": f"{route['handler']} ({route['source']})",
                "responses": {
                    "200": {"description": "Success"},
                    "422": {"description": "Validation error"},
                },
            }

    return {
        "openapi": "3.0.0",
        "info": {
            "title": "pookiepages API",
            "version": "1.0.0",
            "description": "Auto-generated API documentation",
        },
        "paths": paths,
    }


_SWAGGER_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>API Docs</title>
<link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css">
</head>
<body>
<div id="swagger-ui"></div>
<script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>
<script>
SwaggerUIBundle({{
  url: "{schema_url}",
  dom_id: "#swagger-ui",
  presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
  layout: "StandaloneLayout"
}});
</script>
</html>"""


def registerApiDocs(app: Flask):
    @app.route("/api/docs")
    def apiDocs():
        devConfig = app.config.get("PP_DEV")
        if devConfig and not devConfig.apiDocs:
            from flask import abort
            abort(404)
        return _SWAGGER_HTML.format(schema_url="/api/docs/schema.json")

    @app.route("/api/docs/schema.json")
    def apiDocsSchema():
        devConfig = app.config.get("PP_DEV")
        if devConfig and not devConfig.apiDocs:
            from flask import abort
            abort(404)
        schema = _buildOpenApiSchema(app)
        return JsonResponse(schema)
