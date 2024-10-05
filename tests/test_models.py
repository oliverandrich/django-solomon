from datetime import timedelta
from unittest.mock import Mock

import pytest
import time_machine
from django.utils import timezone

from solomon.models import SolomonToken


@pytest.mark.django_db
@pytest.mark.parametrize("require_same_browser", [True, False])
def test_create_token(settings, active_user, require_same_browser, faker):
    settings.SOLOMON_REQUIRE_SAME_BROWSER = require_same_browser
    token = SolomonToken.objects.create(
        email=active_user.email,
        ip_address=faker.ipv4(),
        redirect_url="/" + faker.uri_path(deep=3),
    )
    assert token.email == active_user.email
    assert token.ip_address is not None
    assert token.redirect_url is not None
    assert token.token_string is not None
    assert token.expiry_date is not None
    assert token.expiry_date <= timezone.now() + timedelta(seconds=settings.SOLOMON_MAX_TOKEN_LIFETIME)
    assert token.consumed_at is None
    assert token.disabled_at is None

    if require_same_browser:
        assert token.cookie_value != ""
    else:
        assert token.cookie_value == ""

    assert str(token) == f"{active_user.email} - {token.expiry_date}"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "ip, expected, anonymize",
    [
        ("127.0.0.1", "127.0.0.0", True),
        ("127.0.0.1", "127.0.0.1", False),
        ("192.168.178.1", "192.168.0.0", True),
        ("192.168.178.1", "192.168.178.1", False),
        ("::1", "::", True),
        ("::1", "::1", False),
        ("d641:187c:53a8:da5e:0c9c:d2d9:922c:f447", "d641:187c:53a8:da5e::", True),
        ("d641:187c:53a8:da5e:0c9c:d2d9:922c:f447", "d641:187c:53a8:da5e:0c9c:d2d9:922c:f447", False),
    ],
)
def test_create_token_and_ip_address_anonymisation(settings, active_user, faker, ip, expected, anonymize):
    settings.SOLOMON_ANONYMIZE_IP_ADDRESS = anonymize
    token = SolomonToken.objects.create(
        email=active_user.email,
        ip_address=ip,
        redirect_url="/" + faker.uri_path(deep=3),
    )
    assert token.ip_address == expected


@pytest.mark.django_db
def test_is_valid_with_expired_token(token, settings):
    settings.SOLOMON_REQUIRE_SAME_IP = False
    settings.SOLOMON_REQUIRE_SAME_BROWSER = False
    with time_machine.travel(token.expiry_date + timedelta(seconds=1)):
        assert not token.is_valid({})


@pytest.mark.django_db
@pytest.mark.parametrize(
    "ip, anonymize",
    [
        ("127.0.0.1", True),
        ("127.0.0.1", False),
        ("192.168.178.1", True),
        ("192.168.178.1", False),
        ("d641:187c:53a8:da5e:0c9c:d2d9:922c:f447", True),
        ("d641:187c:53a8:da5e:0c9c:d2d9:922c:f447", False),
    ],
)
def test_is_valid_with_same_ip_address(active_user, settings, faker, ip, anonymize):
    settings.SOLOMON_REQUIRE_SAME_IP = True
    settings.SOLOMON_REQUIRE_SAME_BROWSER = False
    settings.SOLOMON_ANONYMIZE_IP_ADDRESS = anonymize
    token = SolomonToken.objects.create(
        email=active_user.email,
        ip_address=ip,
        redirect_url="/" + faker.uri_path(deep=3),
    )
    request = Mock(headers={}, META={"REMOTE_ADDR": ip})
    assert token.is_valid(request)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "login_ip, verify_ip, anonymize, is_valid",
    [
        ("127.0.0.1", "127.0.0.2", True, True),
        ("127.0.0.1", "127.1.0.1", True, False),
        ("127.0.0.1", "127.0.0.2", False, False),
        ("127.0.0.1", "127.1.0.1", False, False),
        ("192.168.178.1", "192.168.178.2", True, True),
        ("192.168.178.1", "192.169.178.2", True, False),
        ("192.168.178.1", "192.168.178.2", False, False),
        ("192.168.178.1", "192.169.178.2", False, False),
        ("d641:187c:53a8:da5e:0c9c:d2d9:922c:f447", "d641:187c:53a8:da5e:0c9c:d2d9:922c:f448", True, True),
        ("d641:187c:53a8:da5e:0c9c:d2d9:922c:f447", "d641:187c:53a8:da6e:0c9c:d2d9:922c:f447", True, False),
        ("d641:187c:53a8:da5e:0c9c:d2d9:922c:f447", "d641:187c:53a8:da5e:0c9c:d2d9:922c:f448", False, False),
        ("d641:187c:53a8:da5e:0c9c:d2d9:922c:f447", "d641:187c:53a8:da6e:0c9c:d2d9:922c:f447", False, False),
    ],
)
def test_is_valid_with_different_ip_address(active_user, settings, faker, login_ip, verify_ip, anonymize, is_valid):
    settings.SOLOMON_REQUIRE_SAME_IP = True
    settings.SOLOMON_REQUIRE_SAME_BROWSER = False
    settings.SOLOMON_ANONYMIZE_IP_ADDRESS = anonymize
    token = SolomonToken.objects.create(
        email=active_user.email,
        ip_address=login_ip,
        redirect_url="/" + faker.uri_path(deep=3),
    )
    request = Mock(headers={}, META={"REMOTE_ADDR": verify_ip})
    assert token.is_valid(request) == is_valid


@pytest.mark.django_db
def test_is_valid_check_same_browser(settings, active_user, faker):
    settings.SOLOMON_REQUIRE_SAME_IP = False
    settings.SOLOMON_REQUIRE_SAME_BROWSER = True
    token = SolomonToken.objects.create(
        email=active_user.email,
        ip_address=faker.ipv4(),
        redirect_url="/" + faker.uri_path(deep=3),
    )
    request = Mock(headers={}, META={}, COOKIES={settings.SOLOMON_COOKIE_NAME: token.cookie_value})
    assert token.is_valid(request)

    request = Mock(headers={}, META={}, COOKIES={settings.SOLOMON_COOKIE_NAME: faker.pystr()})
    assert not token.is_valid(request)


@pytest.mark.django_db
def test_is_valid_with_disabled_token(token):
    token.disable()
    assert not token.is_valid({})


@pytest.mark.django_db
def test_is_valid_with_consumed_token(token):
    token.consume()
    assert not token.is_valid({})


@pytest.mark.django_db
def test_disable_token(token):
    token.disable()
    assert token.disabled_at is not None


@pytest.mark.django_db
def test_consume_token(token):
    token.consume()
    assert token.consumed_at is not None


@pytest.mark.django_db
def test_get_user_with_active_user(token, active_user):
    assert token.get_user() == active_user


@pytest.mark.django_db
def test_get_user_with_non_existent_user(faker):
    token = SolomonToken.objects.create(
        email=faker.email(),
        ip_address=faker.ipv4(),
        redirect_url="/" + faker.uri_path(deep=3),
    )
    assert token.get_user() is None


@pytest.mark.django_db
def test_get_verify_url(faker, rf):
    token = SolomonToken.objects.create(
        email=faker.email(),
        ip_address=faker.ipv4(),
        redirect_url="/" + faker.uri_path(deep=3),
    )
    request = rf.get("/")
    assert f"/verify/{token.pk}/{token.token_string}/" in token.get_verify_url(request)


@pytest.mark.django_db
def test_send_email(token, faker, mailoutbox, rf, settings):
    settings.SOLOMON_REQUIRE_SAME_IP = False
    settings.SOLOMON_REQUIRE_SAME_BROWSER = False
    request = rf.get("/")
    token.send_email(request)
    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == [token.email]


@pytest.mark.django_db
def test_send_email_for_invalid_token(disabled_token, faker, mailoutbox, rf, settings):
    settings.SOLOMON_REQUIRE_SAME_IP = False
    settings.SOLOMON_REQUIRE_SAME_BROWSER = False
    request = rf.get("/")
    disabled_token.send_email(request)
    assert len(mailoutbox) == 0
