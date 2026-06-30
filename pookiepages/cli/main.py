from __future__ import annotations
import click
from pookiepages.cli.commands.run import runCommand
from pookiepages.cli.commands.build import buildCommand
from pookiepages.cli.commands.migrate import migrateCommand
from pookiepages.cli.commands.shell import shellCommand
from pookiepages.cli.commands.routes import routesCommand
from pookiepages.cli.commands.version import versionCommand
from pookiepages.cli.commands.admin import adminCreateCommand


@click.group()
def cli():
    """pookiepages - Python web framework CLI."""
    pass


@cli.command("init")
def initCommand():
    """Scaffold a new pookiepages project."""
    from pookiepages.cli.init_wizard import runInitWizard
    runInitWizard()


@cli.group("admin")
def adminGroup():
    """Admin management commands."""
    pass


adminGroup.add_command(adminCreateCommand, name="create")

cli.add_command(runCommand, name="run")
cli.add_command(buildCommand, name="build")
cli.add_command(migrateCommand, name="migrate")
cli.add_command(shellCommand, name="shell")
cli.add_command(routesCommand, name="routes")
cli.add_command(versionCommand, name="version")
