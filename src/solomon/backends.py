from typing import Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.http import HttpRequest

from solomon.models import SolomonToken


class SolomonBackend:
    def authenticate(
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
        user_model = get_user_model()
        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None
