from datetime import timedelta
from typing import Optional

import jwt
from django.db import models
from django.http import HttpRequest
from django.utils import timezone

from solomon.conf import settings

TOKEN_ALGORITHM = "HS256"


class SolomonTokenManager(models.Manager):
    def create_from_email(
        self,
        email: str,
        *,
        redirect_url: Optional[str] = None,
    ) -> "SolomonToken":
        return SolomonToken.objects.create(
            email=email,
            redirect_url=redirect_url or "",
        )

    def verify_token(self, token: str) -> Optional["SolomonToken"]:
        """
        Verifies the provided JWT token and returns the corresponding SolomonToken object if valid.

        Args:
            token (str): The JWT token to be verified.

        Returns:
            Optional["SolomonToken"]: The SolomonToken object if the token is valid and not expired,
                                      otherwise None.
        """
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[TOKEN_ALGORITHM])
        except jwt.ExpiredSignatureError:
            return None

        return (
            self.get_queryset()
            .filter(
                pk=decoded_token["jti"],
                email=decoded_token["email"],
            )
            .first()
        )


class SolomonToken(models.Model):
    email = models.EmailField()
    expiry_date = models.DateTimeField()
    redirect_url = models.TextField()
    disabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    consumed_at = models.DateTimeField(null=True, blank=True)

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
        return super().save(*args, **kwargs)

    def send_email(self, request: HttpRequest) -> None:
        pass

    @property
    def token_string(self) -> str:
        """
        Generates a JWT token string for the user.

        The token includes the user's email, an expiration date, and a unique identifier (jti).
        It is encoded using the secret key defined in the settings and the specified algorithm.

        Returns:
            str: The encoded JWT token string.
        """
        return jwt.encode(
            {
                "email": self.email,
                "exp": self.expiry_date,
                "jti": self.pk,
            },
            settings.SECRET_KEY,
            algorithm=TOKEN_ALGORITHM,
        )
