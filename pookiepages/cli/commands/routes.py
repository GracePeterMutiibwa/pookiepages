from __future__ import annotations
import click


@click.command("routes")
def routesCommand():
    """List all registered routes."""
    import os, sys
    sys.path.insert(0, os.getcwd())

    from pookiepages.app import create_app
    app = create_app(project_root=os.getcwd())

    from pookiepages.router import listRoutes
    routes = listRoutes()

    if not routes:
        print("pookiepages: no routes registered.")
        return

    print(f"\n{'Endpoint':<40} {'Methods':<20} {'Source'}")
    print("-" * 90)
    for route in routes:
        methods = ", ".join(route["methods"])
        print(f"{route['endpoint']:<40} {methods:<20} {route['source']}")
    print()
