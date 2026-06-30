from __future__ import annotations
import click


@click.command("version")
def versionCommand():
    """Show pookiepages version."""
    from pookiepages import __version__
    print(f"pookiepages {__version__}")
