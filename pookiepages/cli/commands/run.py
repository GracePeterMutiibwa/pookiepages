from __future__ import annotations
import click


@click.command("run")
@click.option("--port", default=8000, help="Port to listen on")
@click.option("--host", default="127.0.0.1", help="Host to bind to")
@click.option("--no-reload", is_flag=True, default=False, help="Disable auto-reload")
def runCommand(port: int, host: str, no_reload: bool):
    """Start the development server."""
    import os, sys
    sys.path.insert(0, os.getcwd())

    from pookiepages.app import create_app
    app = create_app(project_root=os.getcwd())

    print(f"pookiepages: dev server running at http://{host}:{port}")
    app.run(host=host, port=port, debug=True, use_reloader=not no_reload)
