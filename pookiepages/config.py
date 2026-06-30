from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from pookiepages.exceptions import PookiePagesError


@dataclass
class AppConfig:
    pagesDir: str = "pages"
    staticDir: str = "static"
    settingsFile: str = "settings.py"
    routes: list[str] = field(default_factory=list)
    publicConfig: dict[str, Any] = field(default_factory=dict)
    bridge: bool = True
    secretKey: str = ""
    loginPage: str = "/auth/login"


@dataclass
class BuildConfig:
    outputDir: str = "dist"
    minifyCss: bool = True
    minifyJs: bool = True
    minifyHtml: bool = False


@dataclass
class DevConfig:
    port: int = 8000
    host: str = "127.0.0.1"
    reload: bool = True
    apiDocs: bool = True


@dataclass
class AdminConfig:
    path: str = "/admin"
    title: str = "pookiepages Admin"
    enabled: bool = True


def _loadConfigModule(project_root: str) -> Any:
    import importlib.util, os, sys

    configPath = os.path.join(project_root, "pookiepages.config.py")
    if not os.path.exists(configPath):
        raise PookiePagesError(
            f"Config loading failed in {project_root}. "
            f"pookiepages.config.py not found. "
            f"Create pookiepages.config.py in your project root."
        )

    spec = importlib.util.spec_from_file_location("pookiepages_config", configPath)
    module = importlib.util.module_from_spec(spec)
    sys.modules["pookiepages_config"] = module
    spec.loader.exec_module(module)
    return module


def loadConfig(project_root: str = ".") -> tuple[AppConfig, BuildConfig, DevConfig, AdminConfig]:
    module = _loadConfigModule(project_root)

    def _require(attr: str) -> Any:
        if not hasattr(module, attr):
            raise PookiePagesError(
                f"Config loading failed in pookiepages.config.py. "
                f"Required section '{attr}' is missing. "
                f"Add APP = AppConfig(...) (or BUILD/DEV/ADMIN) to your config file."
            )
        return getattr(module, attr)

    appConfig = _require("APP")
    if not isinstance(appConfig, AppConfig):
        raise PookiePagesError(
            f"Config loading failed in pookiepages.config.py. "
            f"APP must be an AppConfig instance. "
            f"Check that APP = AppConfig(...) is set correctly."
        )

    buildConfig = getattr(module, "BUILD", BuildConfig())
    devConfig = getattr(module, "DEV", DevConfig())
    adminConfig = getattr(module, "ADMIN", AdminConfig())

    print(f"pookiepages: loaded config from pookiepages.config.py")
    return appConfig, buildConfig, devConfig, adminConfig
