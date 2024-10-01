import ipaddress

from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser


def get_or_create_user(email: str) -> AbstractBaseUser:
    User = get_user_model()  # noqa: N806

    email = email.lower()

    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        pass

    user_fields = [field.name for field in User._meta.get_fields()]

    user_details = {"email": email}
    if "username" in user_fields:  # pragma: no cov
        user_details["username"] = email

    user = User.objects.create(**user_details)
    user.set_unusable_password()
    user.save()

    return user


def anonymize_ip(ip_address, ipv4_mask=16, ipv6_mask=64):
    ip = ipaddress.ip_address(ip_address)
    if ip.version == 4:
        network = ipaddress.IPv4Network(f"{ip}/{ipv4_mask}", strict=False)
    else:
        network = ipaddress.IPv6Network(f"{ip}/{ipv6_mask}", strict=False)
    return str(network.network_address)
