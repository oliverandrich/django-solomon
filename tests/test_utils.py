from unittest.mock import Mock

import pytest

from solomon.utils import anonymize_ip, get_ip_address, get_or_create_user


@pytest.mark.django_db
def test_get_existing_user(django_user_model):
    user = django_user_model.objects.create(email="test@example.com")
    fetched_user = get_or_create_user(email="test@example.com")
    assert user == fetched_user


@pytest.mark.django_db
def test_create_user_with_default_username(django_user_model, faker):
    email = faker.email()
    user = get_or_create_user(email=email)
    assert user.email == email
    assert user.username == email
    assert user.password is not None


@pytest.mark.parametrize(
    "ip, expected, ipv4_mask, ipv6_mask",
    [
        ("127.0.0.1", "127.0.0.0", 16, 64),
        ("127.0.0.1", "127.0.0.0", 24, 64),
        ("192.168.178.1", "192.168.0.0", 16, 64),
        ("192.168.178.1", "192.168.178.0", 24, 64),
        ("::1", "::", 16, 48),
        ("::1", "::", 16, 64),
        ("d641:187c:53a8:da5e:0c9c:d2d9:922c:f447", "d641:187c:53a8::", 16, 48),
        ("d641:187c:53a8:da5e:0c9c:d2d9:922c:f447", "d641:187c:53a8:da5e::", 16, 64),
    ],
)
def test_anonymize_ip(ip, expected, ipv4_mask, ipv6_mask):
    assert anonymize_ip(ip, ipv4_mask=ipv4_mask, ipv6_mask=ipv6_mask) == expected


def test_get_ip_address_from_x_forwarded_for():
    request = Mock(headers={"x-forwarded-for": "203.0.113.195, 70.41.3.18, 150.172.238.178"}, META={})
    assert get_ip_address(request) == "150.172.238.178"


def test_get_ip_address_from_remote_addr():
    request = Mock(headers={}, META={"REMOTE_ADDR": "203.0.113.195"})
    assert get_ip_address(request) == "203.0.113.195"


def test_get_ip_address_no_ip():
    request = Mock(headers={}, META={})
    assert get_ip_address(request) == ""
