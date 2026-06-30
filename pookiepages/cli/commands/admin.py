from __future__ import annotations
import click


@click.command("create")
def adminCreateCommand():
    """Create an admin user account."""
    import os, sys, getpass
    sys.path.insert(0, os.getcwd())

    from pookiepages.app import create_app
    app = create_app(project_root=os.getcwd())

    emailAddr = input("Admin email: ").strip().lower()
    if not emailAddr:
        print("pookiepages: email cannot be empty.")
        return

    plainPassword = getpass.getpass("Admin password: ")
    if not plainPassword:
        print("pookiepages: password cannot be empty.")
        return

    with app.app_context():
        from pookiepages.database.tables import PpUser
        from pookiepages.auth.passwords import hashPassword

        try:
            existing = PpUser.objects.filter(email=emailAddr).first()
            if existing:
                existing.isAdmin = True
                existing.save()
                print(f"pookiepages: existing account updated to admin for {emailAddr}")
                return

            PpUser.objects.create(
                email=emailAddr,
                passwordHash=hashPassword(plainPassword),
                isAdmin=True,
            )
            print(f"pookiepages: admin account created for {emailAddr}")
        except Exception as createErr:
            print(f"pookiepages: failed to create admin account: {createErr}")
