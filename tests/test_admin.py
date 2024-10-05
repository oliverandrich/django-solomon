import pytest
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory

from solomon.admin import SolomonTokenAdmin
from solomon.models import SolomonToken


@pytest.fixture
def admin_site():
    return AdminSite()


@pytest.fixture
def token_admin(admin_site):
    return SolomonTokenAdmin(SolomonToken, admin_site)


@pytest.fixture
def token():
    return SolomonToken.objects.create(
        email="test@example.com",
        ip_address="127.0.0.1",
        redirect_url="http://example.com",
    )


@pytest.fixture
def request_factory():
    return RequestFactory()


def test_list_display(token_admin):
    assert token_admin.list_display == (
        "email",
        "ip_address",
        "redirect_url",
        "created_at",
        "expiry_date",
        "is_consumed",
        "is_disabled",
    )


def test_search_fields(token_admin):
    assert token_admin.search_fields == ("email",)


@pytest.mark.django_db
def test_is_consumed(token_admin, token):
    assert not token_admin.is_consumed(token)
    token.consume()
    assert token_admin.is_consumed(token)


@pytest.mark.django_db
def test_is_disabled(token_admin, token):
    assert not token_admin.is_disabled(token)
    token.disable()
    assert token_admin.is_disabled(token)


def test_has_add_permission(token_admin, request_factory):
    request = request_factory.get("/")
    assert not token_admin.has_add_permission(request)


@pytest.mark.django_db
def test_has_change_permission(token_admin, request_factory, token):
    request = request_factory.get("/")
    assert not token_admin.has_change_permission(request)
    assert not token_admin.has_change_permission(request, token)


def test_is_consumed_boolean(token_admin):
    assert token_admin.is_consumed.boolean is True


def test_is_disabled_boolean(token_admin):
    assert token_admin.is_disabled.boolean is True
