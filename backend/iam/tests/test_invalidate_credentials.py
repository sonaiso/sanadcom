"""The post-exposure invalidation command: dry run changes nothing; --yes signs everyone out, revokes every
API token and forces password resets; --keep-passwords leaves passwords alone. Expectations are counts
fixed by hand, not read back from the command."""

from io import StringIO

import pytest
from django.contrib.sessions.backends.db import SessionStore
from django.core.management import call_command
from knox.models import AuthToken

from iam.models import User


@pytest.fixture
def exposed_state(db):
    users = [User.objects.create_user(email=f"u{i}@example.com", password="Strong-Pass-123!") for i in range(3)]
    for _ in range(2):
        store = SessionStore()
        store["k"] = "v"
        store.save()
    for user in users[:2]:
        AuthToken.objects.create(user=user)
    return users


def test_dry_run_changes_nothing(exposed_state):
    from django.contrib.sessions.models import Session

    out = StringIO()
    call_command("invalidate_credentials", stdout=out)
    assert "dry run" in out.getvalue()
    assert Session.objects.count() == 2
    assert AuthToken.objects.count() == 2
    assert all(u.has_usable_password() for u in User.objects.all())


def test_yes_invalidates_everything(exposed_state):
    from django.contrib.sessions.models import Session

    out = StringIO()
    call_command("invalidate_credentials", "--yes", stdout=out)
    assert Session.objects.count() == 0
    assert AuthToken.objects.count() == 0
    assert not any(u.has_usable_password() for u in User.objects.all())
    assert User.objects.count() == 3  # nobody is deleted
    assert "2 sessions deleted, 2 api tokens deleted, 3 passwords marked unusable" in out.getvalue()


def test_keep_passwords_only_revokes_sessions_and_tokens(exposed_state):
    from django.contrib.sessions.models import Session

    call_command("invalidate_credentials", "--yes", "--keep-passwords", stdout=StringIO())
    assert Session.objects.count() == 0 and AuthToken.objects.count() == 0
    assert all(u.has_usable_password() for u in User.objects.all())


def test_planted_fault_is_caught(exposed_state, monkeypatch):
    # blocked example: if deletion silently skipped sessions, the command must refuse to report success
    from django.contrib.sessions.models import Session
    from django.core.management.base import CommandError

    class NoDeleteQS(list):
        def delete(self):
            return 0, {}

    monkeypatch.setattr(Session.objects, "all", lambda: NoDeleteQS())
    with pytest.raises(CommandError):
        call_command("invalidate_credentials", "--yes", stdout=StringIO())
