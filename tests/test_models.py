from datetime import timedelta
from unittest.mock import patch

import time_machine
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone
from faker import Faker

from solomon.conf import settings
from solomon.models import SolomonToken

faker = Faker()
User = get_user_model()


class SolomonTokenTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.active_user = User.objects.create_user(
            faker.user_name(),
            email=faker.email(),
            password=faker.password(),
            is_active=True,
        )

    def test_create_from_email(self):
        email = "test@example.com"
        token = SolomonToken.objects.create_from_email(email)
        self.assertEqual(token.email, email)
        self.assertEqual(token.redirect_url, "")

    def test_create_from_email_with_redirect_url(self):
        email = "test@example.com"
        redirect_url = "/redirect"
        token = SolomonToken.objects.create_from_email(email, redirect_url=redirect_url)
        self.assertEqual(token.email, email)
        self.assertEqual(token.redirect_url, redirect_url)

    def test_create_from_email_with_ipv4_address(self):
        email = "test@example.com"
        ip_address = "192.168.178.1"
        token = SolomonToken.objects.create_from_email(email, ip_address=ip_address)
        self.assertEqual(token.email, email)
        self.assertEqual(token.ip_address, ip_address)

    @override_settings(SOLOMON_ANONYMIZE_IP_ADDRESS=True)
    def test_create_from_email_with_ipv4_address_with_anonymization(self):
        email = "test@example.com"
        ip_address = "192.168.178.1"
        token = SolomonToken.objects.create_from_email(email, ip_address=ip_address)
        self.assertEqual(token.email, email)
        self.assertEqual(token.ip_address, "192.168.0.0")

    def test_create_from_email_with_ipv6_address(self):
        email = "test@example.com"
        ip_address = "d641:187c:53a8:da5e:0c9c:d2d9:922c:f447"
        token = SolomonToken.objects.create_from_email(email, ip_address=ip_address)
        self.assertEqual(token.email, email)
        self.assertEqual(token.ip_address, ip_address)

    @override_settings(SOLOMON_ANONYMIZE_IP_ADDRESS=True)
    def test_create_from_email_with_ipv6_address_with_anonymization(self):
        email = "test@example.com"
        ip_address = "d641:187c:53a8:da5e:0c9c:d2d9:922c:f447"
        token = SolomonToken.objects.create_from_email(email, ip_address=ip_address)
        self.assertEqual(token.email, email)
        self.assertEqual(token.ip_address, "d641:187c:53a8:da5e::")

    def test_verify_token_valid(self):
        email = "test@example.com"
        token = SolomonToken.objects.create_from_email(email)
        token_string = token.token_string
        verified_token = SolomonToken.objects.verify_token(token.pk, token_string)
        self.assertEqual(verified_token, token)

    def test_verify_token_invalid(self):
        token_string = "invalid.token.string"
        verified_token = SolomonToken.objects.verify_token(1, token_string)
        self.assertIsNone(verified_token)

    @time_machine.travel("2023-01-01 00:00:00")
    def test_verify_token_expired(self):
        email = "test@example.com"
        token = SolomonToken.objects.create_from_email(email)

        with time_machine.travel(token.expiry_date + timedelta(seconds=1)):
            verified_token = SolomonToken.objects.verify_token(token.pk, token.token_string)
            self.assertIsNone(verified_token)

    def test_save_sets_expiry_date(self):
        email = "test@example.com"
        token = SolomonToken.objects.create_from_email(email)
        self.assertLessEqual(
            token.expiry_date,
            timezone.now() + timedelta(seconds=settings.SOLOMON_MAX_TOKEN_LIFETIME),
        )

    def test_token_string(self):
        email = "test@example.com"
        token = SolomonToken.objects.create_from_email(email)
        token_string = token.token_string
        self.assertIsInstance(token_string, str)

    def test_get_verify_url(self):
        email = "test@example.com"
        token = SolomonToken.objects.create_from_email(email)
        with patch("django.http.request.HttpRequest") as MockHttpRequest:  # noqa: N806
            request = MockHttpRequest()
            request.build_absolute_uri.return_value = "http://testserver/verify"
        verify_url = token.get_verify_url(request)
        self.assertEqual(verify_url, "http://testserver/verify")

    def test_get_user(self):
        token = SolomonToken.objects.create_from_email(self.active_user.email)
        retrieved_user = token.get_user()
        self.assertEqual(retrieved_user, self.active_user)

    def test_str_method(self):
        email = "test@example.com"
        token = SolomonToken.objects.create_from_email(email)
        self.assertEqual(str(token), f"{email} - {token.expiry_date}")

    def test_save_does_not_update_token_string_and_expiry_date(self):
        email = "test@example.com"
        token = SolomonToken.objects.create_from_email(email)
        token_string = token.token_string
        expiry_date = token.expiry_date
        token.save()
        self.assertEqual(token.token_string, token_string)
        self.assertEqual(token.expiry_date, expiry_date)

    def test_send_email(self):
        token = SolomonToken.objects.create_from_email(self.active_user.email)
        with patch("django.http.request.HttpRequest") as MockHttpRequest:  # noqa: N806
            request = MockHttpRequest()
            token.send_email(request)
        self.assertEqual(len(mail.outbox), 1)
        m = mail.outbox[0]
        self.assertEqual(m.from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertEqual(m.to, [self.active_user.email])
        self.assertEqual(m.subject, "")
