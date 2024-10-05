import ipaddress

from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.http import HttpRequest


def get_or_create_user(email: str) -> AbstractBaseUser:
    """
    Retrieves an existing user by email or creates a new user if one does not exist.

    Args:
        email (str): The email address of the user.

    Returns:
        AbstractBaseUser: The retrieved or newly created user instance.
    """
    User = get_user_model()  # noqa: N806

    email = email.lower()

    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        pass

    user_details = {"email": email}
    if "username" in [field.name for field in User._meta.get_fields()]:  # pragma: no cov
        user_details["username"] = email

    user = User.objects.create(**user_details)
    user.set_unusable_password()
    user.save()

    return user


def get_ip_address(request: HttpRequest) -> str:
    """
    Returns the IP address of the request.

    Returns:
        str: The IP address of the request.
    """
    ip_address = request.headers.get("x-forwarded-for", "")
    if ip_address:
        return ip_address.split(",")[-1].strip()

    return request.META.get("REMOTE_ADDR", "")


def anonymize_ip(ip_address: str, ipv4_mask: int = 16, ipv6_mask: int = 64) -> str:
    """
    Anonymizes an IP address by masking it with the specified subnet mask.

    Args:
        ip_address (str): The IP address to be anonymized.
        ipv4_mask (int, optional): The subnet mask for IPv4 addresses. Defaults to 16.
        ipv6_mask (int, optional): The subnet mask for IPv6 addresses. Defaults to 64.

    Returns:
        str: The anonymized IP address.
    """
    ip = ipaddress.ip_address(ip_address)
    if ip.version == 4:
        network = ipaddress.IPv4Network(f"{ip}/{ipv4_mask}", strict=False)
    else:
        network = ipaddress.IPv6Network(f"{ip}/{ipv6_mask}", strict=False)
    return str(network.network_address)
