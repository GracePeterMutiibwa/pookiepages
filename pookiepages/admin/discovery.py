from __future__ import annotations
import os
import importlib
import inspect
import pookiedb as pk

_excludedModels: set[type] = set()
_discoveredModels: list[type] = []


def excludeFromAdmin(model_class: type) -> type:
    _excludedModels.add(model_class)
    return model_class


def discoverModels(project_root: str = ".") -> list[type]:
    global _discoveredModels
    modelsDir = os.path.join(project_root, "models")

    if not os.path.isdir(modelsDir):
        _discoveredModels = []
        return _discoveredModels

    found = []
    for fileName in os.listdir(modelsDir):
        if not fileName.endswith(".py") or fileName.startswith("_"):
            continue
        moduleName = f"models.{fileName[:-3]}"
        try:
            module = importlib.import_module(moduleName)
            for attrName in dir(module):
                obj = getattr(module, attrName)
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, pk.Model)
                    and obj is not pk.Model
                    and obj not in _excludedModels
                ):
                    found.append(obj)
        except ImportError:
            pass

    _discoveredModels = found
    return _discoveredModels


def getDiscoveredModels() -> list[type]:
    return list(_discoveredModels)
