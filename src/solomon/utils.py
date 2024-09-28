from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser


def get_or_create_user(
    email: str, username: str = "", first_name: str = "", last_name: str = ""
) -> AbstractBaseUser:
    User = get_user_model()  # noqa: N806

    email = email.lower()

    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        pass

    user_fields = [field.name for field in User._meta.get_fields()]

    user_details = {"email": email}
    if "username" in user_fields:
        user_details["username"] = username or email
    if "first_name" in user_fields and first_name:
        user_details["first_name"] = first_name
    if "last_name" in user_fields and last_name:
        user_details["last_name"] = last_name
    if "full_name" in user_fields:
        user_details["full_name"] = f"{first_name} {last_name}".strip()
    if "name" in user_fields:
        user_details["name"] = f"{first_name} {last_name}".strip()

    return User.objects.create(**user_details)
