from typing import Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.http import HttpRequest

from solomon.models import SolomonToken


class SolomonBackend:
    """
    Authentication backend for Solomon tokens.

    This backend provides methods to authenticate users based on Solomon tokens
    and to retrieve user instances by their ID.
    """
    def authenticate(
        """
        Authenticate a user using a Solomon token.

        Args:
            request (HttpRequest): The HTTP request object.
            token_pk (Optional[int]): The primary key of the Solomon token.
            token_string (Optional[str]): The token string.

        Returns:
            Optional[AbstractBaseUser]: The authenticated user or None if authentication fails.
        """
        self,
        request: HttpRequest,
        token_pk: Optional[int] = None,
        token_string: Optional[str] = None,
    ) -> Optional[AbstractBaseUser]:
        solomon_token = SolomonToken.objects.filter(pk=token_pk, token_string=token_string).first()
        if not solomon_token:
            return

        if not solomon_token.is_valid(request):
            return

        solomon_token.consume()

        return solomon_token.get_user()

    def get_user(self, user_id: int) -> Optional[AbstractBaseUser]:
        """
        Retrieve a user by their ID.

        Args:
            user_id (int): The ID of the user to retrieve.

        Returns:
            Optional[AbstractBaseUser]: The user instance or None if the user does not exist.
        """
        user_model = get_user_model()
        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None
