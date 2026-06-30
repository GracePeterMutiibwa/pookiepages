from __future__ import annotations
import os
from flask import Flask
from pookiepages.config import AppConfig, BuildConfig, DevConfig, AdminConfig, loadConfig
from pookiepages.exceptions import PookiePagesError


def create_app(project_root: str = ".") -> Flask:
    appConfig, buildConfig, devConfig, adminConfig = loadConfig(project_root)

    flaskApp = Flask(
        __name__,
        template_folder=os.path.join(project_root, appConfig.pagesDir),
        static_folder=os.path.join(project_root, appConfig.staticDir),
    )

    if not appConfig.secretKey:
        raise PookiePagesError(
            "App startup failed. APP.secretKey is empty. "
            "Set APP.secretKey to a long random string in pookiepages.config.py."
        )
    flaskApp.secret_key = appConfig.secretKey

    flaskApp.config["PP_APP"] = appConfig
    flaskApp.config["PP_BUILD"] = buildConfig
    flaskApp.config["PP_DEV"] = devConfig
    flaskApp.config["PP_ADMIN"] = adminConfig
    flaskApp.config["PP_PROJECT_ROOT"] = project_root

    from pookiepages.database.connection import initDatabase
    initDatabase(flaskApp, project_root)

    from pookiepages.database.tables import createInternalTables
    createInternalTables(flaskApp)

    if appConfig.bridge:
        from pookiepages.bridge import registerBridgeRoute
        registerBridgeRoute(flaskApp)

    from pookiepages.router import registerFileRoutes
    registerFileRoutes(flaskApp, project_root, appConfig)

    from pookiepages.router import registerDynamicRoutes
    registerDynamicRoutes(flaskApp, appConfig)

    if adminConfig.enabled:
        from pookiepages.admin import registerAdminRoutes
        registerAdminRoutes(flaskApp, adminConfig)
        print(f"pookiepages: admin panel enabled at {adminConfig.path}")

    if devConfig.apiDocs:
        from pookiepages.docs_gen import registerApiDocs
        registerApiDocs(flaskApp)

    return flaskApp
