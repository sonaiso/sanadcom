"""Invalidate every live credential after a secret exposure.

Run on each live instance that was ever restored from, or shares a SECRET_KEY with, the
database dumps that were committed to the public repository (see
docs/SECURITY_REMEDIATION_2026-11-02.md):

    python manage.py invalidate_credentials --yes

What it does, in one transaction:
  1. deletes every Django session (all logged-in users are signed out);
  2. deletes every Knox API token (all API clients must re-authenticate);
  3. marks every user's password unusable so the next login goes through the
     password-reset flow (the e-mail/SSO identity is kept; nothing is deleted).
     Pass --keep-passwords to skip step 3.

It never prints or stores a credential. Rotating DJANGO_SECRET_KEY itself is a deployment
action (environment variable or secret store) and is only reminded here; this command
does not and cannot change it.
"""

from __future__ import annotations

from django.contrib.sessions.models import Session
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from iam.models import User

try:  # knox is installed in this project, but keep the command usable if the table is absent
    from knox.models import AuthToken
except Exception:  # pragma: no cover - defensive import
    AuthToken = None


class Command(BaseCommand):
    help = "Sign everyone out, revoke every API token and force password resets after a secret exposure."

    def add_arguments(self, parser):
        parser.add_argument("--yes", action="store_true", help="Actually perform the invalidation (otherwise a dry run).")
        parser.add_argument("--keep-passwords", action="store_true", help="Do not mark user passwords unusable.")

    def handle(self, *args, **options):
        sessions = Session.objects.count()
        tokens = AuthToken.objects.count() if AuthToken is not None else 0
        users = User.objects.count()
        self.stdout.write(f"sessions to delete: {sessions}")
        self.stdout.write(f"api tokens to delete: {tokens}")
        self.stdout.write("users whose password will be marked unusable: " + ("0 (--keep-passwords)" if options["keep_passwords"] else str(users)))

        if not options["yes"]:
            self.stdout.write(self.style.WARNING("dry run: nothing changed. Re-run with --yes to apply."))
            return

        with transaction.atomic():
            deleted_sessions, _ = Session.objects.all().delete()
            deleted_tokens = 0
            if AuthToken is not None:
                deleted_tokens, _ = AuthToken.objects.all().delete()
            reset_users = 0
            if not options["keep_passwords"]:
                for user in User.objects.all().iterator():
                    user.set_unusable_password()
                    user.save(update_fields=["password"])
                    reset_users += 1

        if Session.objects.exists() or (AuthToken is not None and AuthToken.objects.exists()):
            raise CommandError("invalidation incomplete: live sessions or tokens remain")

        self.stdout.write(self.style.SUCCESS(
            f"done: {deleted_sessions} sessions deleted, {deleted_tokens} api tokens deleted, {reset_users} passwords marked unusable"
        ))
        self.stdout.write(self.style.WARNING(
            "still required, outside Django: rotate DJANGO_SECRET_KEY and the database credentials in the deployment "
            "secret store, then restart the backend so the new key takes effect."
        ))
