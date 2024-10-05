import pytest
from django.urls import reverse

from solomon.models import SolomonToken


@pytest.fixture
def active_user(django_user_model, faker):
    return django_user_model.objects.create_user(
        faker.user_name(),
        email=faker.email(),
        password=faker.password(),
        is_active=True,
    )


@pytest.fixture
def inactive_user(django_user_model, faker):
    user = django_user_model.objects.create_user(
        faker.user_name(),
        email=faker.email(),
        password=faker.password(),
    )
    user.is_active = False
    user.save()
    return user


@pytest.fixture
def token(active_user, faker):
    return SolomonToken.objects.create(
        email=active_user.email,
        ip_address=faker.ipv4(),
        redirect_url="/" + faker.uri_path(deep=3),
    )


@pytest.fixture
def invalid_token(active_user, faker):
    token = SolomonToken.objects.create(
        email=active_user.email,
        ip_address=faker.ipv4(),
        redirect_url="/" + faker.uri_path(deep=3),
    )
    token.consume()
    return token


@pytest.fixture
def disabled_token(active_user, faker):
    token = SolomonToken.objects.create(
        email=active_user.email,
        ip_address=faker.ipv4(),
        redirect_url="/" + faker.uri_path(deep=3),
    )
    token.disable()
    return token


@pytest.fixture
def login_view_url():
    return reverse("solomon:login")


@pytest.fixture
def verify_view_url():
    return reverse("solomon:verify")
