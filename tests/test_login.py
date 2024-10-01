from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from faker import Faker

from solomon.conf import settings
from solomon.forms import LoginForm
from solomon.models import SolomonToken

User = get_user_model()

faker = Faker()


class LoginViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.login_view_url = reverse("solomon:login")
        cls.active_user = User.objects.create_user(
            faker.user_name(),
            email=faker.email(),
            password=faker.password(),
            is_active=True,
        )
        cls.inactive_user = User.objects.create_user(
            faker.user_name(),
            email=faker.email(),
            password=faker.password(),
            is_active=False,
        )

    def test_login_get_page_status_code(self):
        response = self.client.get(self.login_view_url)
        self.assertEqual(response.status_code, 200)

    def test_login_get_page_contains_form(self):
        response = self.client.get(self.login_view_url)
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], LoginForm)

    def test_login_get_page_template_used(self):
        response = self.client.get(self.login_view_url)
        self.assertTemplateUsed(response, settings.SOLOMON_LOGIN_TEMPLATE)

    def test_login_with_empty_formdata_status_code(self):
        response = self.client.post(self.login_view_url, {})
        self.assertEqual(response.status_code, 200)

    def test_login_with_empty_formdata_contains_form(self):
        response = self.client.post(self.login_view_url, {})
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], LoginForm)

    def test_login_with_empty_formdata_form_errors(self):
        response = self.client.post(self.login_view_url, {})
        self.assertIn("email", response.context["form"].errors)

    def test_login_with_empty_formdata_template_used(self):
        response = self.client.post(self.login_view_url, {})
        self.assertTemplateUsed(response, settings.SOLOMON_LOGIN_TEMPLATE)

    def test_login_with_invalid_formdata_status_code(self):
        response = self.client.post(self.login_view_url, {"email": faker.pystr()})
        self.assertEqual(response.status_code, 200)

    def test_login_with_invalid_formdata_contains_form(self):
        response = self.client.post(self.login_view_url, {"email": faker.pystr()})
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], LoginForm)

    def test_login_with_invalid_formdata_form_errors(self):
        response = self.client.post(self.login_view_url, {"email": faker.pystr()})
        self.assertIn("email", response.context["form"].errors)

    def test_login_with_invalid_formdata_template_used(self):
        response = self.client.post(self.login_view_url, {"email": faker.pystr()})
        self.assertTemplateUsed(response, settings.SOLOMON_LOGIN_TEMPLATE)

    def test_login_with_an_inactive_user_status_code(self):
        response = self.client.post(self.login_view_url, {"email": self.inactive_user.email})
        self.assertEqual(response.status_code, 200)

    def test_login_with_an_inactive_user_contains_form(self):
        response = self.client.post(self.login_view_url, {"email": self.inactive_user.email})
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], LoginForm)

    def test_login_with_an_inactive_user_form_errors(self):
        response = self.client.post(self.login_view_url, {"email": self.inactive_user.email})
        self.assertIn("email", response.context["form"].errors)
        self.assertIn("This user has been deactivated.", response.context["form"].errors["email"])

    def test_login_with_an_inactive_user_template_used(self):
        response = self.client.post(self.login_view_url, {"email": self.inactive_user.email})
        self.assertTemplateUsed(response, settings.SOLOMON_LOGIN_TEMPLATE)

    def test_login_with_an_active_user_status_code(self):
        response = self.client.post(self.login_view_url, {"email": self.active_user.email})
        self.assertEqual(response.status_code, 200)

    def test_login_with_an_active_user_user_count(self):
        self.client.post(self.login_view_url, {"email": self.active_user.email})
        self.assertEqual(User.objects.count(), 2)

    def test_login_with_an_active_user_token_created(self):
        self.client.post(self.login_view_url, {"email": self.active_user.email})
        self.assertEqual(SolomonToken.objects.count(), 1)
        self.assertEqual(SolomonToken.objects.first().email, self.active_user.email)
        self.assertEqual(SolomonToken.objects.first().redirect_url, settings.LOGIN_REDIRECT_URL)

    def test_login_with_an_active_user_email_sent(self):
        self.client.post(self.login_view_url, {"email": self.active_user.email})
        self.assertEqual(len(mail.outbox), 1)
        m = mail.outbox[0]
        self.assertEqual(m.from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertEqual(m.to, [self.active_user.email])
        self.assertEqual(m.subject, "")

    def test_login_with_an_active_user_template_used(self):
        response = self.client.post(self.login_view_url, {"email": self.active_user.email})
        self.assertTemplateUsed(response, settings.SOLOMON_LOGIN_DONE_TEMPLATE)

    def test_login_with_a_new_user_status_code(self):
        response = self.client.post(self.login_view_url, {"email": faker.email()})
        self.assertEqual(response.status_code, 200)

    def test_login_with_a_new_user_user_count(self):
        self.client.post(self.login_view_url, {"email": faker.email()})
        self.assertEqual(User.objects.count(), 2)

    def test_login_with_a_new_user_token_created(self):
        email = faker.email()
        self.client.post(self.login_view_url, {"email": email})
        self.assertEqual(SolomonToken.objects.count(), 1)
        self.assertEqual(SolomonToken.objects.first().email, email)
        self.assertEqual(SolomonToken.objects.first().redirect_url, settings.LOGIN_REDIRECT_URL)

    def test_login_with_a_new_user_email_sent(self):
        email = faker.email()
        self.client.post(self.login_view_url, {"email": email})
        self.assertEqual(len(mail.outbox), 1)
        m = mail.outbox[0]
        self.assertEqual(m.from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertEqual(m.to, [email])
        self.assertEqual(m.subject, "")

    def test_login_with_a_new_user_template_used(self):
        response = self.client.post(self.login_view_url, {"email": faker.email()})
        self.assertTemplateUsed(response, settings.SOLOMON_LOGIN_DONE_TEMPLATE)

    def test_login_with_next_parameter_status_code(self):
        response = self.client.post(
            self.login_view_url, {"email": self.active_user.email, "redirect_url": "/"}
        )
        self.assertEqual(response.status_code, 200)

    def test_login_with_next_parameter_token_created(self):
        self.client.post(
            self.login_view_url, {"email": self.active_user.email, "redirect_url": "/"}
        )
        self.assertEqual(SolomonToken.objects.count(), 1)
        self.assertEqual(SolomonToken.objects.first().email, self.active_user.email)
        self.assertEqual(SolomonToken.objects.first().redirect_url, "/")

    def test_login_with_next_parameter_email_sent(self):
        self.client.post(
            self.login_view_url, {"email": self.active_user.email, "redirect_url": "/"}
        )
        self.assertEqual(len(mail.outbox), 1)
        m = mail.outbox[0]
        self.assertEqual(m.from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertEqual(m.to, [self.active_user.email])
        self.assertEqual(m.subject, "")

    def test_login_with_next_parameter_template_used(self):
        response = self.client.post(
            self.login_view_url, {"email": self.active_user.email, "redirect_url": "/"}
        )
        self.assertTemplateUsed(response, settings.SOLOMON_LOGIN_DONE_TEMPLATE)
