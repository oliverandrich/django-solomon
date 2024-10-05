import re
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import models
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string

from solomon.conf import settings
from solomon.utils import anonymize_ip, get_ip_address

User = get_user_model()


class SolomonToken(models.Model):
    email = models.EmailField()
    redirect_url = models.TextField()
    ip_address = models.GenericIPAddressField()
    expiry_date = models.DateTimeField(editable=False)
    token_string = models.CharField(max_length=128, editable=False)
    cookie_value = models.CharField(max_length=64, editable=False)
    consumed_at = models.DateTimeField(null=True, editable=True)
    disabled_at = models.DateTimeField(null=True, editable=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.email} - {self.expiry_date}"

    def save(self, *args, **kwargs) -> None:
        """
        Overrides the save method to set the cookie value and expiry date for new instances.

        If the instance is being created (i.e., it does not have a primary key yet):
        - Sets the expiry date based on the current time plus the SOLOMON_MAX_TOKEN_LIFETIME
          setting.

        Args:
            *args: Variable length argument list. **kwargs: Arbitrary keyword arguments.

        Returns:
            None
        """
        if not self.pk:
            self.expiry_date = timezone.now() + timedelta(seconds=settings.SOLOMON_MAX_TOKEN_LIFETIME)
            self.token_string = get_random_string(128)
            if settings.SOLOMON_REQUIRE_SAME_BROWSER:
                self.cookie_value = get_random_string(64)
            if self.ip_address and settings.SOLOMON_ANONYMIZE_IP_ADDRESS:
                self.ip_address = anonymize_ip(self.ip_address)

        return super().save(*args, **kwargs)

    def send_email(self, request: HttpRequest) -> None:
        """
        Sends a verification email to the user if the request is valid.

        This method constructs the email subject, text content, and HTML content
        using predefined templates and context data. It then sends the email
        using Django's send_mail function.

        Args:
            request (HttpRequest): The HTTP request object containing the necessary
                                   data to validate and generate the email content.

        Returns:
            None
        """
        if not self.is_valid(request):
            return

        context = {
            "verify_url": self.get_verify_url(request),
            "expiry_date": self.expiry_date,
        }
        subject = render_to_string(settings.SOLOMON_EMAIL_SUBJECT_TEMPLATE, context=context)
        subject = re.sub(r"\s+", " ", subject)
        text_content = render_to_string(settings.SOLOMON_EMAIL_TXT_TEMPLATE, context=context)
        html_content = render_to_string(settings.SOLOMON_EMAIL_HTML_TEMPLATE, context=context)

        send_mail(
            subject.strip(),
            text_content.strip(),
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
            html_message=html_content.strip(),
        )

    def get_verify_url(self, request: HttpRequest) -> str:
        """
        Generates a URL that can be used to verify the token.

        Returns:
            str: The URL to verify the token.
        """
        url = reverse("solomon:verify", kwargs={"pk": self.pk, "token_string": self.token_string})
        return request.build_absolute_uri(url)

    def get_user(self):
        """
        Retrieves the User object that matches the email of the current instance.

        Returns:
            User: The User object with a matching email, or None if no match is found.
        """
        return User.objects.filter(email=self.email).first()

    def is_valid(self, request: HttpRequest) -> bool:
        """
        Validates the current object based on the request.

        This method performs several checks to determine if the current object is valid:
        1. Checks if the current time is past the expiry date.
        2. If SOLOMON_REQUIRE_SAME_IP is enabled, it verifies that the IP address of the request matches the stored IP
           address.
        3. If SOLOMON_REQUIRE_SAME_BROWSER is enabled, it verifies that the browser cookie value matches the stored
           cookie value.

        If any of these checks fail, the object is disabled and the method returns False.

        Args:
            request (HttpRequest): The HTTP request to validate against.

        Returns:
            bool: True if the object is valid, False otherwise.
        """
        if self.disabled_at:
            return False

        if self.consumed_at:
            return False

        if timezone.now() > self.expiry_date:
            self.disable()
            return False

        if settings.SOLOMON_REQUIRE_SAME_IP:
            ip_address = get_ip_address(request)
            if settings.SOLOMON_ANONYMIZE_IP_ADDRESS:
                ip_address = anonymize_ip(ip_address)

            if self.ip_address != ip_address:
                self.disable()
                return False

        if settings.SOLOMON_REQUIRE_SAME_BROWSER:
            cookie_value = request.COOKIES.get(settings.SOLOMON_COOKIE_NAME)
            if self.cookie_value != cookie_value:
                self.disable()
                return False

        return True

    def disable(self) -> None:
        """
        Marks the token as disabled.

        Returns:
            None
        """
        self.disabled_at = timezone.now()
        self.save()

    def consume(self) -> None:
        """
        Marks the token as consumed.

        Returns:
            None
        """
        self.consumed_at = timezone.now()
        self.save()
