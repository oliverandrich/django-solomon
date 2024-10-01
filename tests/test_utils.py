from django.contrib.auth import get_user_model
from django.test import TestCase
from parameterized import parameterized

from solomon.utils import anonymize_ip, get_or_create_user


class GetOrCreateUserTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.email = "test@example.com"
        self.username = "testuser"

    def test_get_existing_user(self):
        user = self.User.objects.create(email=self.email)
        fetched_user = get_or_create_user(email=self.email)
        self.assertEqual(user, fetched_user)

    def test_create_user_with_default_username(self):
        user = get_or_create_user(email=self.email)
        self.assertEqual(user.email, self.email)
        self.assertEqual(user.username, self.email)
        self.assertIsNotNone(user.password)


class AnonymizeIpTests(TestCase):
    @parameterized.expand(
        [
            ("127.0.0.1", "127.0.0.0", 16, 64),
            ("127.0.0.1", "127.0.0.0", 24, 64),
            ("192.168.178.1", "192.168.0.0", 16, 64),
            ("192.168.178.1", "192.168.178.0", 24, 64),
            ("::1", "::", 16, 48),
            ("::1", "::", 16, 64),
            ("d641:187c:53a8:da5e:0c9c:d2d9:922c:f447", "d641:187c:53a8::", 16, 48),
            ("d641:187c:53a8:da5e:0c9c:d2d9:922c:f447", "d641:187c:53a8:da5e::", 16, 64),
        ]
    )
    def test_anonymize_ipv4_address(self, ip, expected, ipv4_mask, ipv6_mask):
        self.assertEqual(anonymize_ip(ip, ipv4_mask=ipv4_mask, ipv6_mask=ipv6_mask), expected)

    def test_anonymize_invalid_ip_address(self):
        with self.assertRaises(ValueError):
            anonymize_ip("invalid")
