import pytest
from django.urls import reverse
from django.utils import timezone


@pytest.fixture
def now():
    return timezone.now()


@pytest.fixture
def login_view_url():
    return reverse("solomon:login")


@pytest.fixture
def signup_view_url():
    return reverse("solomon:signup")


@pytest.fixture
def active_user(django_user_model, faker):
    user = django_user_model.objects.create_user(
        faker.user_name(), email=faker.email(), password=faker.password()
    )
    user.is_active = True
    user.save()
    return user


@pytest.fixture
def inactive_user(django_user_model, faker):
    user = django_user_model.objects.create_user(
        faker.user_name(), email=faker.email(), password=faker.password()
    )
    user.is_active = False
    user.save()
    return user
