from __future__ import annotations
import click


@click.command("migrate")
@click.option("--make", is_flag=True, default=False, help="Generate migration files")
@click.option("--show", is_flag=True, default=False, help="Show migration status")
@click.option("--rollback", is_flag=True, default=False, help="Roll back last migration")
@click.option("--steps", default=1, help="Number of steps to roll back")
def migrateCommand(make: bool, show: bool, rollback: bool, steps: int):
    """Manage database migrations."""
    import os, sys
    sys.path.insert(0, os.getcwd())

    migrationsDir = os.path.join(os.getcwd(), "migrations")

    if show:
        if not os.path.isdir(migrationsDir):
            print("pookiepages: no migrations directory found. Run with --make first.")
            return
        files = sorted(f for f in os.listdir(migrationsDir) if f.endswith(".py") and not f.startswith("_"))
        if not files:
            print("pookiepages: no migrations found.")
        for f in files:
            print(f"  {f}")
        return

    if rollback:
        from pookiedb.migrations.executor import rollback as doRollback
        rolledBack = doRollback(migrationsDir, steps=steps)
        if rolledBack:
            print(f"pookiepages: rolled back {len(rolledBack)} migration(s): {', '.join(rolledBack)}")
        else:
            print("pookiepages: nothing to roll back.")
        return

    from pookiedb.migrations.executor import migrate as doMigrate
    applied = doMigrate(migrationsDir)
    if applied:
        print(f"pookiepages: applied {len(applied)} migration(s). Database is up to date.")
    else:
        print("pookiepages: no pending migrations. Database is already up to date.")
