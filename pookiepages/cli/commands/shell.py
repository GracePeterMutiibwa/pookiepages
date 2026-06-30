from __future__ import annotations
import click


@click.command("shell")
def shellCommand():
    """Launch interactive Python shell with app context."""
    import os, sys, code
    sys.path.insert(0, os.getcwd())

    from pookiepages.app import create_app
    app = create_app(project_root=os.getcwd())

    localVars = {"app": app}
    modelsDir = os.path.join(os.getcwd(), "models")
    if os.path.isdir(modelsDir):
        import importlib
        for fileName in os.listdir(modelsDir):
            if fileName.endswith(".py") and not fileName.startswith("_"):
                try:
                    module = importlib.import_module(f"models.{fileName[:-3]}")
                    localVars[fileName[:-3]] = module
                except ImportError:
                    pass

    print("pookiepages: interactive shell. App context is active. 'app' is available.")
    with app.app_context():
        code.interact(local=localVars)
