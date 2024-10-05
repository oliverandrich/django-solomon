from typing import Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.http import HttpRequest

from solomon.models import SolomonToken


class SolomonBackend:
    def authenticate(
        self, request: HttpRequest, token_pk: Optional[int] = None, token_string: Optional[str] = None
    ) -> Optional[AbstractBaseUser]:
        """
        Authenticates a user based on a provided token primary key and token string.

        Args:
            request (HttpRequest): The HTTP request object. token_pk (Optional[int]): The primary key of the token.
            token_string (Optional[str]): The string representation of the token.

        Returns:
            Optional[AbstractBaseUser]: The authenticated user if the token is valid and can be consumed, otherwise
            None.
        """
        token = SolomonToken.objects.filter(pk=token_pk, token_string=token_string).first()
        if not token or not token.is_valid(request):
            return None

        token.consume()
        return token.get_user()

    def get_user(self, user_id: int) -> Optional[AbstractBaseUser]:
        """
        Retrieve a user instance by its user ID.

        Args:
            user_id (int): The ID of the user to retrieve.

        Returns:
            Optional[AbstractBaseUser]: The user instance if found, otherwise None.
        """
        return get_user_model().objects.filter(pk=user_id).first()
