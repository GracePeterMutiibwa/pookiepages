from __future__ import annotations
import importlib.util
import os
import sys
from flask import Flask
import pookiedb
from pookiepages.exceptions import PookiePagesError


_activeConnections: dict[str, Any] = {}


def _loadSettingsModule(project_root: str, settings_file: str) -> Any:
    settingsPath = os.path.join(project_root, settings_file)
    if not os.path.exists(settingsPath):
        return None

    spec = importlib.util.spec_from_file_location("pp_settings", settingsPath)
    module = importlib.util.module_from_spec(spec)
    sys.modules["pp_settings"] = module
    spec.loader.exec_module(module)
    return module


def initDatabase(app: Flask, project_root: str):
    appConfig = app.config["PP_APP"]
    settingsModule = _loadSettingsModule(project_root, appConfig.settingsFile)

    if settingsModule is None:
        print(f"pookiepages: no settings.py found, skipping database connection")
        return

    if not hasattr(settingsModule, "DATABASE"):
        print(f"pookiepages: DATABASE not defined in {appConfig.settingsFile}, skipping database connection")
        return

    dbConfig = settingsModule.DATABASE

    from pookiepages.database import DatabaseConfig, PostgresConfig

    if isinstance(dbConfig, PostgresConfig):
        connectionUrl = dbConfig.toUrl()
        alias = dbConfig.alias
    elif isinstance(dbConfig, DatabaseConfig):
        connectionUrl = dbConfig.url
        alias = dbConfig.alias
    elif isinstance(dbConfig, str):
        connectionUrl = dbConfig
        alias = "default"
    else:
        raise PookiePagesError(
            f"Database connection failed. DATABASE in {appConfig.settingsFile} must be "
            f"a DatabaseConfig, PostgresConfig, or connection string. "
            f"Check your settings.py DATABASE assignment."
        )

    try:
        connection = pookiedb.connect(connectionUrl, alias=alias)
        _activeConnections[alias] = connection
        app.config["PP_DB_CONNECTION"] = connection
        app.config["PP_DB_ALIAS"] = alias

        dbLabel = connectionUrl.split("///")[-1] if ":///" in connectionUrl else connectionUrl
        print(f"pookiepages: connected to database at {dbLabel}")
    except Exception as connErr:
        raise PookiePagesError(
            f"Database connection failed for '{connectionUrl}'. "
            f"Error: {connErr}. "
            f"Check your DATABASE connection string in {appConfig.settingsFile}."
        )


def getConnection(alias: str = "default"):
    return _activeConnections.get(alias)
