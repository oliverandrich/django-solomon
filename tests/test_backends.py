import pytest

from solomon.backends import SolomonBackend


@pytest.mark.django_db
def test_get_user_with_active_user(token, active_user):
    backend = SolomonBackend()
    assert backend.get_user(active_user.pk) == active_user


@pytest.mark.django_db
def test_get_user_with_non_existent_user(faker):
    backend = SolomonBackend()
    assert backend.get_user(2) is None
