from __future__ import annotations
import inspect
from typing import Any
from flask import Flask, request as flaskRequest, session as flaskSession, redirect
import pookiedb as pk
from pookiepages.admin.auth import requireAdminAuth, createAdminSession, destroyAdminSession
from pookiepages.admin.discovery import getDiscoveredModels
from pookiepages.auth.passwords import verifyPassword
from pookiepages.config import AdminConfig

_BS5_CDN = ""  # Bootstrap 5 served from package static dir

_PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | Admin</title>
<link rel="stylesheet" href="/admin/static/bootstrap.min.css">
</head>
<body>
<nav class="navbar navbar-dark bg-dark px-3">
  <span class="navbar-brand">{site_title}</span>
  <a class="btn btn-sm btn-outline-light" href="/admin/logout">Logout</a>
</nav>
<div class="container mt-4">
{content}
</div>
<script src="/admin/static/bootstrap.bundle.min.js"></script>
</body>
</html>"""


def _renderPage(title: str, content: str, site_title: str = "pookiepages Admin") -> str:
    return _PAGE_TEMPLATE.format(title=title, content=content, site_title=site_title)


def _modelFields(model_class: type) -> list[Any]:
    return [f for f in model_class._meta.fields if f.name != "id"]


def _listView(model_class: type, admin_config: AdminConfig) -> str:
    tableName = model_class.__name__
    objects = list(model_class.objects.all())
    fields = _modelFields(model_class)

    headers = "".join(f"<th>{f.name}</th>" for f in fields)
    rows = ""
    for obj in objects:
        cells = "".join(f"<td>{getattr(obj, f.name, '')}</td>" for f in fields)
        pkVal = getattr(obj, "id", "")
        rows += (
            f"<tr>{cells}"
            f"<td>"
            f"<a class='btn btn-sm btn-primary me-1' href='{admin_config.path}/{tableName}/{pkVal}/edit'>Edit</a>"
            f"<form method='POST' action='{admin_config.path}/{tableName}/{pkVal}/delete' style='display:inline'>"
            f"<button type='submit' class='btn btn-sm btn-danger'>Delete</button>"
            f"</form>"
            f"</td></tr>"
        )

    content = f"""
<div class="d-flex justify-content-between align-items-center mb-3">
  <h4>{tableName}</h4>
  <a class="btn btn-success" href="{admin_config.path}/{tableName}/create">Add new</a>
</div>
<table class="table table-bordered table-striped">
  <thead><tr>{headers}<th>Actions</th></tr></thead>
  <tbody>{rows}</tbody>
</table>"""

    return _renderPage(tableName, content)


def _createView(model_class: type, admin_config: AdminConfig) -> str:
    tableName = model_class.__name__
    fields = _modelFields(model_class)

    if flaskRequest.method == "POST":
        data = flaskRequest.form.to_dict()
        try:
            model_class.objects.create(**data)
            return redirect(f"{admin_config.path}/{tableName}")
        except Exception as createErr:
            error = str(createErr)
            formHtml = _buildForm(fields, {}, tableName, admin_config, error)
            return _renderPage(f"Create {tableName}", formHtml)

    formHtml = _buildForm(fields, {}, tableName, admin_config)
    return _renderPage(f"Create {tableName}", formHtml)


def _editView(model_class: type, pk_value: int, admin_config: AdminConfig) -> str:
    tableName = model_class.__name__
    fields = _modelFields(model_class)

    try:
        obj = model_class.objects.get(id=pk_value)
    except Exception:
        return _renderPage("Not Found", "<p>Record not found.</p>")

    if flaskRequest.method == "POST":
        data = flaskRequest.form.to_dict()
        for fieldObj in fields:
            if fieldObj.name in data:
                setattr(obj, fieldObj.name, data[fieldObj.name])
        try:
            obj.save()
            return redirect(f"{admin_config.path}/{tableName}")
        except Exception as saveErr:
            currentValues = {f.name: getattr(obj, f.name, "") for f in fields}
            formHtml = _buildForm(fields, currentValues, tableName, admin_config, str(saveErr), pk_value)
            return _renderPage(f"Edit {tableName}", formHtml)

    currentValues = {f.name: getattr(obj, f.name, "") for f in fields}
    formHtml = _buildForm(fields, currentValues, tableName, admin_config, pk_id=pk_value)
    return _renderPage(f"Edit {tableName}", formHtml)


def _buildForm(fields, values: dict, table_name: str, admin_config: AdminConfig, error: str = "", pk_id: int | None = None) -> str:
    action = f"{admin_config.path}/{table_name}/create" if pk_id is None else f"{admin_config.path}/{table_name}/{pk_id}/edit"
    inputsHtml = ""
    for fieldObj in fields:
        val = values.get(fieldObj.name, "")
        inputsHtml += (
            f"<div class='mb-3'>"
            f"<label class='form-label'>{fieldObj.name}</label>"
            f"<input class='form-control' name='{fieldObj.name}' value='{val}'>"
            f"</div>"
        )
    errorHtml = f"<div class='alert alert-danger'>{error}</div>" if error else ""
    return f"""
{errorHtml}
<form method="POST" action="{action}">
{inputsHtml}
<button type="submit" class="btn btn-primary">Save</button>
<a href="{admin_config.path}/{table_name}" class="btn btn-secondary ms-2">Cancel</a>
</form>"""


def registerAdminRoutes(app: Flask, admin_config: AdminConfig):
    import os
    packageStaticDir = os.path.join(os.path.dirname(__file__), "static")

    @app.route(f"{admin_config.path}/static/<path:filename>")
    def adminStatic(filename):
        from flask import send_from_directory
        return send_from_directory(packageStaticDir, filename)

    @app.route(f"{admin_config.path}/login", methods=["GET", "POST"])
    def adminLogin():
        from pookiepages.database.tables import PpUser
        if flaskRequest.method == "GET":
            return _renderPage("Admin Login", """
<div class="row justify-content-center">
  <div class="col-md-4">
    <h4 class="mb-3">Admin Login</h4>
    <form method="POST" action="/admin/login">
      <div class="mb-3"><label class="form-label">Email</label><input type="email" class="form-control" name="email"></div>
      <div class="mb-3"><label class="form-label">Password</label><input type="password" class="form-control" name="password"></div>
      <button type="submit" class="btn btn-primary w-100">Login</button>
    </form>
  </div>
</div>""")

        emailAddr = flaskRequest.form.get("email", "").lower()
        plainPassword = flaskRequest.form.get("password", "")
        try:
            user = PpUser.objects.get(email=emailAddr)
        except Exception:
            return _renderPage("Admin Login", "<div class='alert alert-danger'>Invalid credentials.</div>")

        if not user.isAdmin or not verifyPassword(plainPassword, user.passwordHash or ""):
            return _renderPage("Admin Login", "<div class='alert alert-danger'>Invalid credentials or insufficient permissions.</div>")

        token = createAdminSession(user.id)
        flaskSession["pp_admin_token"] = token
        return redirect(admin_config.path)

    @app.route(f"{admin_config.path}/logout")
    def adminLogout():
        token = flaskSession.pop("pp_admin_token", None)
        if token:
            destroyAdminSession(token)
        return redirect(f"{admin_config.path}/login")

    @app.route(admin_config.path)
    @requireAdminAuth
    def adminIndex():
        models = getDiscoveredModels()
        links = "".join(
            f"<a class='list-group-item list-group-item-action' href='{admin_config.path}/{m.__name__}'>{m.__name__}</a>"
            for m in models
        )
        content = f"<h4>Models</h4><div class='list-group'>{links}</div>"
        return _renderPage("Dashboard", content, admin_config.title)

    @app.route(f"{admin_config.path}/<string:model_name>")
    @requireAdminAuth
    def adminList(model_name: str):
        models = {m.__name__: m for m in getDiscoveredModels()}
        if model_name not in models:
            return _renderPage("Not Found", "<p>Model not found.</p>")
        return _listView(models[model_name], admin_config)

    @app.route(f"{admin_config.path}/<string:model_name>/create", methods=["GET", "POST"])
    @requireAdminAuth
    def adminCreate(model_name: str):
        models = {m.__name__: m for m in getDiscoveredModels()}
        if model_name not in models:
            return _renderPage("Not Found", "<p>Model not found.</p>")
        return _createView(models[model_name], admin_config)

    @app.route(f"{admin_config.path}/<string:model_name>/<int:pk_value>/edit", methods=["GET", "POST"])
    @requireAdminAuth
    def adminEdit(model_name: str, pk_value: int):
        models = {m.__name__: m for m in getDiscoveredModels()}
        if model_name not in models:
            return _renderPage("Not Found", "<p>Model not found.</p>")
        return _editView(models[model_name], pk_value, admin_config)

    @app.route(f"{admin_config.path}/<string:model_name>/<int:pk_value>/delete", methods=["POST"])
    @requireAdminAuth
    def adminDelete(model_name: str, pk_value: int):
        models = {m.__name__: m for m in getDiscoveredModels()}
        if model_name not in models:
            return _renderPage("Not Found", "<p>Model not found.</p>")
        try:
            obj = models[model_name].objects.get(id=pk_value)
            obj.delete()
        except Exception:
            pass
        return redirect(f"{admin_config.path}/{model_name}")
