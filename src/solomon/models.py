import re
from datetime import timedelta
from typing import Optional

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import models
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string

from solomon.conf import settings
from solomon.utils import anonymize_ip

User = get_user_model()


class SolomonTokenManager(models.Manager):
    def create_from_email(
        self,
        email: str,
        *,
        redirect_url: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> "SolomonToken":
        """
        Creates a SolomonToken instance from the provided email.

        Args:
            email (str): The email address to associate with the token.
            redirect_url (Optional[str]): An optional URL to redirect to. Defaults to None.

        Returns:
            SolomonToken: The created SolomonToken instance.
        """
        if ip_address and settings.SOLOMON_ANONYMIZE_IP_ADDRESS:
            ip_address = anonymize_ip(ip_address)

        return SolomonToken.objects.create(
            email=email,
            redirect_url=redirect_url or "",
            ip_address=ip_address,
        )

    def verify_token(self, pk: int, token_string: str) -> Optional["SolomonToken"]:
        """
        Verifies the provided JWT token and returns the corresponding SolomonToken object if valid.

        Args:
            token (str): The JWT token to be verified.

        Returns:
            Optional["SolomonToken"]: The SolomonToken object if the token is valid and not expired,
                                      otherwise None.
        """
        return (
            self.get_queryset()
            .filter(pk=pk, token_string=token_string, expiry_date__gte=timezone.now())
            .first()
        )


class SolomonToken(models.Model):
    email = models.EmailField()
    redirect_url = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    consumed_at = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateTimeField(editable=False)
    token_string = models.CharField(max_length=128, editable=False)
    ip_address = models.GenericIPAddressField(null=True, editable=False)

    objects: SolomonTokenManager = SolomonTokenManager()

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
            self.expiry_date = timezone.now() + timedelta(
                seconds=settings.SOLOMON_MAX_TOKEN_LIFETIME
            )
            self.token_string = get_random_string(128)
        return super().save(*args, **kwargs)

    def send_email(self, request: HttpRequest, *, signup: bool = False) -> None:
        context = {
            "verify_url": self.get_verify_url(request),
            "signup": signup,
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
        url = reverse("solomon:verify", kwargs={"jwt_token": self.token_string})
        return request.build_absolute_uri(url)

    def get_user(self):
        """
        Retrieves the User object that matches the email of the current instance.

        Returns:
            User: The User object with a matching email, or None if no match is found.
        """
        return User.objects.filter(email=self.email).first()
